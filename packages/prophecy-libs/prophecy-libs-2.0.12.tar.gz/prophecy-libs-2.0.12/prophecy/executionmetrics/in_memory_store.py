"""
InMemoryStore implementation for PySpark execution metrics.

This module provides in-memory storage for pipeline execution metrics during runtime.
"""

import json
import logging
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import threading
from abc import ABC
import re

# PySpark imports
from pyspark.sql import SparkSession, DataFrame

from prophecy.executionmetrics.evolutions.models import MetricsStore
from prophecy.executionmetrics.models import PipelineStatus
from prophecy.executionmetrics.pipelineruns.pipeline_run_service import (
    PipelineRunsService,
)
from prophecy.executionmetrics.schemas.em import (
    ComponentDetails,
    GemEdge,
    GemProgress,
    SerializableException,
    TimestampedOutput,
)
from prophecy.executionmetrics.schemas.external import (
    LInterimContent,
    InterimKey,
    MetricsWriteDetails,
)
from prophecy.executionmetrics.package import (
    ComponentRuns,
    UnavailableWorkflowJsonException,
)
from prophecy.executionmetrics.evolutions.metrics_storage_initializer import (
    StorageMetadata,
    create_storage_metadata,
)
from prophecy.executionmetrics.utils.common import is_databricks_environment, now_millis
from prophecy.executionmetrics.utils.external import compress
from prophecy.executionmetrics.workflow_parser import (
    HasProcessesConnectionsPorts,
    WorkflowEdge,
    WorkflowGraph,
    WorkflowGroup,
    WorkflowNode,
    get_workflow_graph,
)


def get_slug_to_process_map(code: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """Extract slug to process mapping from code."""
    graph = get_workflow_graph(code)
    if graph:
        return extract_slug_to_process_mapping(graph.processes)
    return None


def extract_slug_to_process_mapping(
    processes: Dict[str, WorkflowNode],
) -> Dict[str, str]:
    """Extract mapping from slug to process ID."""
    slug_to_process = {}

    def extract_from_node(node: WorkflowNode, parent_slug: str = ""):
        """Recursively extract slug mappings."""
        current_slug = node.metadata.get("slug", "")
        if parent_slug:
            current_slug = f"{parent_slug}.{current_slug}"

        slug_to_process[current_slug] = node.id

        if isinstance(node, WorkflowGroup):
            for _, child_node in node.processes.items():
                extract_from_node(child_node, current_slug)

    for _, node in processes.items():
        extract_from_node(node)

    return slug_to_process


class InMemoryStore:
    """
    In-memory store for pipeline execution metrics.

    This class maintains runtime state for a pipeline execution and handles
    offloading metrics to persistent storage.
    """

    def __init__(self, spark: SparkSession, uuid: str):
        """Initialize the in-memory store."""
        self.spark = spark
        self.uuid = uuid
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{uuid}")
        self.logger.info("Created InMemoryStore")

        # Storage metadata
        self._storage_metadata: Optional["StorageMetadata"] = None

        # Pipeline execution state
        self._pipeline_uri: str = ""
        self._job_uri: Optional[str] = None
        self._job_run_uid: str = ""
        self._task_run_uid: str = ""
        self._status: str = PipelineStatus.STARTED
        self._fabric_uid: str = ""
        self._time_taken: Optional[int] = None
        self._time_started: int = now_millis()
        self._rows_read: Optional[int] = None
        self._rows_written: Optional[int] = None
        self._run_type: str = ""
        self._created_by: str = ""
        self._code: Optional[Dict[str, str]] = None
        self._interims: List[LInterimContent] = []
        self._submission_time: int = int(time.time() * 1000)
        self._branch: str = ""
        self._db_suffix: str = ""
        self._expected_interims: List[InterimKey] = []
        self._pipeline_config: Optional[str] = None

        # Workflow metadata
        self._slug_to_process_id_map: Optional[Dict[str, str]] = None
        self._process_to_gem_map: Optional[Dict[str, GemProgress]] = None
        self._graph: Optional[WorkflowGraph] = None
        self._processes: Optional[Dict[str, WorkflowNode]] = None
        self._process_to_output_process_map: Optional[Dict[str, List[str]]] = None

        # Thread safety
        self._lock = threading.RLock()

    @property
    def has_storage_metadata(self) -> bool:
        """Check if storage metadata is initialized."""
        return self._storage_metadata is not None

    def init(
        self,
        pipeline_uri: str,
        job_uri: Optional[str],
        fabric_uid: str,
        run_type: str,
        created_by: str,
        code: Optional[Dict[str, str]],
        branch: str,
        db_suffix: str,
        expected_interims: List[InterimKey],
        pipeline_config: Optional[str] = None,
        metrics_write_details: Optional["MetricsWriteDetails"] = None,
    ) -> None:
        """
        Initialize the store with pipeline execution details.

        This is called from sendPipelineRunStartedEvent which is used in both
        interactive pipeline and job runs.
        """
        with self._lock:
            # Initialize storage metadata
            if metrics_write_details is None:
                self.logger.info("metrics writing is not enabled")
                self._storage_metadata = None
            else:
                self.logger.info(
                    f"initialising metrics tables if needed: {metrics_write_details.names}"
                )
                self._storage_metadata = create_storage_metadata(
                    self.spark,
                    metrics_write_details.names,
                    db_suffix,
                    created_by,
                    MetricsStore.from_string(metrics_write_details.storage_format),
                    read_only=False,
                    is_partitioning_disabled=metrics_write_details.is_partitioning_disabled,
                )

            # Set pipeline execution state
            self._time_started = now_millis()
            self._pipeline_uri = pipeline_uri
            self._job_uri = job_uri
            self._fabric_uid = fabric_uid
            self._run_type = run_type
            self._created_by = created_by
            self._branch = branch
            self._db_suffix = db_suffix
            self._expected_interims = expected_interims
            self._pipeline_config = pipeline_config
            self._code = code  # or self._get_pipeline_code()

            # Parse workflow metadata
            self._graph = get_workflow_graph(self._code)
            self._processes = self._all_processes(self._graph) if self._graph else None
            self._slug_to_process_id_map = (
                extract_slug_to_process_mapping(self._graph.processes)
                if self._graph
                else None
            )
            self._process_to_gem_map = (
                self._extract_process_to_gem_map() if self._graph else None
            )
            self._process_to_output_process_map = (
                self._populate_process_to_output_process_map()
            )

    def _populate_process_to_output_process_map(self) -> Optional[Dict[str, List[str]]]:
        """Populate mapping from process to its output processes."""
        if not self._process_to_gem_map:
            return None

        input_to_output_pairs = []
        for process, gem_progress in self._process_to_gem_map.items():
            for gem_edge in gem_progress.input_gems:
                if gem_edge.gem_name and self._slug_to_process_id_map:
                    input_process = self._slug_to_process_id_map.get(gem_edge.gem_name)
                    if input_process:
                        input_to_output_pairs.append((input_process, process))

        # Group by input process
        result = defaultdict(list)
        for input_proc, output_proc in input_to_output_pairs:
            result[input_proc].append(output_proc)

        return dict(result)

    def get_process_id_from_hierarchical_gem_name(
        self, gem_name: Optional[str]
    ) -> Optional[str]:
        """Get process ID from gem name, handling hierarchical names."""
        if not self._code:
            self.logger.error(
                "Code not propagated for this pipeline run, pipeline monitoring will not work!"
            )
        if not gem_name:
            self.logger.error("Expected a valid gem name")
            return None

        self.logger.info(f"Gem name to be fetched {gem_name}")

        if not self._slug_to_process_id_map:
            return None

        # Try exact match first
        if gem_name in self._slug_to_process_id_map:
            return self._slug_to_process_id_map[gem_name]

        # Try suffix match for hierarchical names
        for slug, process in self._slug_to_process_id_map.items():
            if slug.endswith(gem_name):
                return process

        return None

    # TODO (KK) - Do we need to implement this for whl files?
    def _get_pipeline_code(self) -> Optional[Dict[str, str]]:
        """Get pipeline code from Spark configuration."""
        package_path = self.spark.conf.get("spark.prophecy.pipeline.package", None)
        if package_path:
            # MOCK: CommonUtils.PipelineCodeFromClassPath would be imported
            return self._read_package(package_path)
        return None

    def _read_package(self, package_path: str) -> Optional[Dict[str, str]]:
        """Read package contents from path."""
        # MOCK: Simplified package reading
        try:
            if package_path.endswith(".zip") or package_path.endswith(".jar"):
                return self._extract_zip(package_path)
            else:
                return self._read_directory(package_path)
        except Exception as e:
            self.logger.error(f"Failed to read package from {package_path}: {e}")
            return None

    def _extract_zip(self, zip_path: str) -> Dict[str, str]:
        """Extract contents from zip file."""
        contents = {}
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            for file_info in zip_file.filelist:
                if not file_info.is_dir():
                    contents[file_info.filename] = zip_file.read(
                        file_info.filename
                    ).decode("utf-8")
        return contents

    def _read_directory(self, dir_path: str) -> Dict[str, str]:
        """Read contents from directory."""
        contents = {}
        path = Path(dir_path)
        for file_path in path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(path))
                contents[relative_path] = file_path.read_text()
        return contents

    def _all_processes(self, graph: WorkflowGraph) -> Dict[str, WorkflowNode]:
        """Get all processes from workflow graph recursively."""
        all_procs = {}

        def collect_processes(processes: Dict[str, WorkflowNode]):
            for proc_id, node in processes.items():
                all_procs[proc_id] = node
                if isinstance(node, WorkflowGroup):
                    collect_processes(node.processes)

        collect_processes(graph.processes)
        return all_procs

    def _all_connections(self) -> List[WorkflowEdge]:
        graph = self._graph
        all_conns = []
        if not graph:
            return all_conns

        def collect_connections(
            connections: List[WorkflowEdge], processes: Dict[str, WorkflowNode]
        ):
            all_conns.extend(connections)
            # Check for subgraphs and collect their connections
            for node in processes.values():
                if isinstance(node, WorkflowGroup):
                    collect_connections(node.connections, node.processes)

        collect_connections(graph.connections, graph.processes)
        return all_conns

    def _extract_process_to_gem_map(self) -> Dict[str, GemProgress]:
        """Extract mapping from process ID to GemProgress."""
        graph = self._graph
        processes = self._processes
        if graph is None or processes is None:
            return {}

        slug_to_process_map = extract_slug_to_process_mapping(graph.processes)
        process_to_slug_map = {v: k for k, v in slug_to_process_map.items()}

        connections = self._all_connections()
        target_port_to_connection_map = {c.target_port: c for c in connections}

        # Group connections by source port
        source_port_to_connection_multi_map: Dict[str, List[WorkflowEdge]] = {}
        for conn in connections:
            if conn.source_port not in source_port_to_connection_multi_map:
                source_port_to_connection_multi_map[conn.source_port] = []
            source_port_to_connection_multi_map[conn.source_port].append(conn)

        def fetch_output_details(out_port: str) -> List[Tuple[str, str]]:
            """
            Fetch output details for a given output port.

            Args:
                out_port: The output port ID

            Returns:
                List of tuples (target process ID, target port ID)
            """
            connections_list = source_port_to_connection_multi_map.get(out_port, [])
            target_connection_to_node = {
                c: processes.get(c.target) for c in connections_list
            }

            result = []
            for connection, node in target_connection_to_node.items():
                if node and node.component == "Subgraph":
                    # Recursively fetch output details for subgraph
                    result.extend(fetch_output_details(connection.target_port))
                elif node:
                    result.append((connection.target, connection.target_port))

            return result

        def fetch_input_details(in_port: str) -> Tuple[Optional[str], Optional[str]]:
            """
            Fetch input details for a given input port.

            Args:
                in_port: The input port ID

            Returns:
                Tuple of (source process ID, source port ID)
            """
            connection = target_port_to_connection_map.get(in_port)
            if not connection:
                return (None, None)

            source_node = processes.get(connection.source)
            if source_node and source_node.component == "Subgraph":
                # Recursively fetch input details for subgraph
                return fetch_input_details(connection.source_port)
            else:
                return (
                    connection.source if connection else None,
                    connection.source_port if connection else None,
                )

        def extract_process_to_gem_map_inner() -> Dict[str, GemProgress]:
            """
            Internal function to extract process to gem mapping.

            Returns:
                List of tuples (process ID, GemProgress)
            """
            result = {}

            for process_id, current_process in processes.items():
                gem_name = process_to_slug_map.get(
                    current_process.id
                ) or current_process.metadata.get("slug", "")

                out_ports = [port.slug for port in current_process.ports.outputs]
                in_ports = [port.slug for port in current_process.ports.inputs]

                # Get input process details
                input_process_details = []
                for current_process_in_port in current_process.ports.inputs:
                    input_process, source_port_id = fetch_input_details(
                        current_process_in_port.id
                    )
                    input_process_details.append(
                        (input_process, source_port_id, current_process_in_port.slug)
                    )

                # Get output process details
                output_process_details = []
                for current_process_out_port in current_process.ports.outputs:
                    output_details = fetch_output_details(current_process_out_port.id)
                    for output_process, target_port_id in output_details:
                        output_process_details.append(
                            (
                                output_process,
                                current_process_out_port.slug,
                                target_port_id,
                            )
                        )

                # Create input gem edges
                input_gem_edges = []
                for (
                    process_id_opt,
                    from_port_id_opt,
                    to_port_slug,
                ) in input_process_details:
                    gem_name_opt = (
                        process_to_slug_map.get(process_id_opt)
                        if process_id_opt
                        else None
                    )
                    input_process = (
                        processes.get(process_id_opt) if process_id_opt else None
                    )

                    from_port_slug = None
                    if from_port_id_opt and input_process:
                        for port in input_process.ports.outputs:
                            if port.id == from_port_id_opt:
                                from_port_slug = port.slug
                                break

                    input_gem_edges.append(
                        GemEdge(
                            gem_name=gem_name_opt,
                            from_port=from_port_slug,
                            to_port=to_port_slug,
                        )
                    )

                # Create output gem edges
                output_gem_edges = []
                for process_id, from_port_slug, to_port_id in output_process_details:
                    gem_name_opt = process_to_slug_map.get(process_id)
                    output_process = processes.get(process_id)

                    to_port_slug = None
                    if output_process:
                        for port in output_process.ports.inputs:
                            if port.id == to_port_id:
                                to_port_slug = port.slug
                                break

                    output_gem_edges.append(
                        GemEdge(
                            gem_name=gem_name_opt,
                            from_port=from_port_slug,
                            to_port=to_port_slug,
                        )
                    )

                # Create GemProgress
                gem_progress = GemProgress(
                    gem_name=gem_name,
                    process_id=current_process.id,
                    gem_type=current_process.component,
                    input_gems=input_gem_edges,
                    output_gems=output_gem_edges,
                    in_ports=in_ports,
                    out_ports=out_ports,
                    num_rows_output=None,
                    stdout=None,
                    stderr=None,
                    start_time=None,
                    end_time=None,
                    state=None,
                    exception=None,
                )

                result[current_process.id] = gem_progress

            return result

        return extract_process_to_gem_map_inner()

    def update_run_uid(self, job_run_uid: str, task_run_uid: str) -> None:
        """Update job and task run UIDs."""
        with self._lock:
            self._job_run_uid = job_run_uid
            self._task_run_uid = task_run_uid

    def update_interims(self, interim: LInterimContent) -> None:
        """Update interims and connecting gem rows."""
        with self._lock:
            self._interims.append(interim)
            interim_process_id = interim.processId or interim.component
            # TODO - This might not work as process id is not available
            self._update_connecting_gem_rows(interim_process_id, interim)

    def update_selective_interims(self, key: str, payload: str) -> None:
        key = re.sub(r"_interim.*$", "", key)
        parts = key.split("__")
        interim_rows = json.loads(payload)
        # TODO - subgraph, process id is not available
        interims = LInterimContent(
            subgraph="subgraph",
            component=parts[0],
            port=parts[1],
            runId=parts[2] if len(parts) == 3 else None,
            interimRows=interim_rows,
            numRecords=len(interim_rows),
        )
        self.update_interims(interims)

    def update_metrics(
        self,
        status: str,
        rows_read: Optional[int],
        rows_written: Optional[int],
        time_taken: Optional[int],
    ) -> None:
        """Update pipeline execution metrics."""
        with self._lock:
            # Only update status if it's higher priority
            if PipelineStatus.is_status_higher_than_previous_status(
                self._status, status
            ):
                self._status = status

            self._time_taken = time_taken
            self._rows_read = rows_read
            self._rows_written = rows_written

    def update_gem_progress(
        self,
        process: str,
        start_time: str,
        end_time: Optional[str],
        stdout: Optional[List[TimestampedOutput]],
        stderr: Optional[List[TimestampedOutput]],
        state: str,
        exception: Optional[SerializableException],
    ) -> None:
        """Update gem progress information."""
        with self._lock:
            if not self._process_to_gem_map:
                return

            if process in self._process_to_gem_map:
                gem_progress = self._process_to_gem_map[process]
                updated_gem_progress = gem_progress.update_progress(
                    start_time=int(start_time),
                    end_time=int(end_time) if end_time else None,
                    stdout=stdout,
                    stderr=stderr,
                    state=state,
                    exception=exception,
                )
                self._process_to_gem_map[process] = updated_gem_progress

    def _update_connecting_gem_rows(
        self, interim_process: str, interim: LInterimContent
    ) -> None:
        """Update row counts for connecting gems."""
        out_port_id = interim.port
        num_records = interim.numRecords
        interims_rows = num_records or 0

        if not self._process_to_gem_map:
            return

        # Get gem name for interim process
        interim_process_gem_name = None
        if interim_process in self._process_to_gem_map:
            interim_process_gem_name = self._process_to_gem_map[
                interim_process
            ].gem_name

        # Get port slug
        interim_port_slug = None
        if self._processes and interim_process in self._processes:
            node = self._processes[interim_process]
            for port in node.ports.get("outputs", []):
                if port["id"] == out_port_id:
                    interim_port_slug = port.get("slug")
                    break

        # Get output processes for this interim
        output_processes_to_interim = set()
        if (
            self._process_to_output_process_map
            and interim_process in self._process_to_output_process_map
        ):
            output_processes_to_interim = set(
                self._process_to_output_process_map[interim_process]
            )

        # Update input gems of output processes
        for current_process, gem_progress in self._process_to_gem_map.items():
            if current_process in output_processes_to_interim:
                # Update input gem rows
                for gem in gem_progress.input_gems:
                    if (
                        gem.gem_name == interim_process_gem_name
                        and gem.from_port == interim_port_slug
                        and interims_rows > (gem.num_rows or 0)
                    ):
                        gem.num_rows = num_records

        # Update the interim process itself
        if interim_process in self._process_to_gem_map:
            gem_progress = self._process_to_gem_map[interim_process]

            # Update num_rows_output
            if num_records and gem_progress.num_rows_output:
                gem_progress.num_rows_output = max(
                    num_records, gem_progress.num_rows_output
                )
            else:
                gem_progress.num_rows_output = (
                    num_records or gem_progress.num_rows_output
                )

            # Update output gem rows
            for gem in gem_progress.output_gems:
                if gem.from_port == interim_port_slug and interims_rows > (
                    gem.num_rows or 0
                ):
                    gem.num_rows = num_records

    def offload(
        self,
        pipeline_status: str,
        interim_details: List[Tuple[InterimKey, DataFrame]] = None,
    ) -> Tuple[List["ComponentRuns"], List[str]]:
        """
        Offload metrics to persistent storage.

        Returns tuple of (component_runs, interim_ids).
        """
        if interim_details is None:
            interim_details = []

        self.logger.info(f"Starting offload at {datetime.now()}")

        # Calculate expected vs actual interims
        num_actual_interims = len(set(i.port for i in self._interims))
        # TODO (KK) - Add impl
        interim_store_summary = {"executed": {"size": 0}}  # Mock interim store summary
        # num_expected_interims = min(
        #     len(set(i.port for i in self._expected_interims)),
        #     interim_store_summary["executed"]["size"],
        # )
        num_expected_interims = len(set(i.port for i in self._expected_interims))

        logs = []

        # Check for missing interims
        if num_expected_interims != 0 and num_actual_interims != num_expected_interims:
            expected_interim_components = {
                (
                    interim,
                    # self._process_to_component_name_map().get(interim.component, ""),
                )
                for interim in self._expected_interims
            }

            actual_interim_components = {
                (
                    InterimKey(i.subgraph, i.component, i.port),
                    # self._process_to_component_name_map().get(i.component, ""),
                )
                for i in self._interims
            }

            self.logger.error(
                f"Expected ports -> {[i.port for i in self._expected_interims]}"
            )
            self.logger.error(f"Actual ports -> {[i.port for i in self._interims]}")
            self.logger.error(
                f"Uh oh! Expected interims on {num_expected_interims} ports, got {num_actual_interims}"
            )

            missing_components = {k[0] for k in expected_interim_components} - {
                k[0] for k in actual_interim_components
            }
            self.logger.error(
                f"Components where interims were missing {missing_components}"
            )
            self.logger.error(
                "Logical plan details for all dataframes where interims are missing"
            )

            # Log missing interim details
            missing_keys = {k[0] for k in expected_interim_components} - {
                k[0] for k in actual_interim_components
            }
            for interim_key, df in interim_details:
                if interim_key in missing_keys:
                    self.logger.error(f"Missing {interim_key}")

            # Try to read logs
            try:
                if self._is_databricks_environment():
                    log_path = "/databricks/driver/logs/log4j-active.log"
                    with open(log_path, "r") as f:
                        logs = f.readlines()
                else:
                    # Optional: EMR logs are available on S3
                    logs = [""]
            except Exception as e:
                self.logger.warning(f"Could not read logs from path: {e}")

        # Perform the actual offload
        self.logger.info(f"Storage details: {self._storage_metadata}")
        self.logger.info(f"In memory state before offloading metrics\n {self}")
        self.logger.info(
            f"Inserting pipeline run id {self.uuid} for pipeline {self._pipeline_uri}"
        )

        # MOCK: InstrumentationJobId and InstrumentationJobDescription would be constants
        instrumentation_job_id = "prophecy-instrumentation"
        instrumentation_job_description = "Prophecy Instrumentation Job"

        try:
            # MOCK: withProphecyJob and withJobDescription would be Spark context managers
            # In real implementation, these would set job group and description
            if not self._storage_metadata:
                raise Exception("storage metadata expected to be initialized")

            pipeline_runs_service = self._create_pipeline_runs_service()

            # Compress logs
            compressed_logs = compress("".join(logs))

            # Add pipeline run and component runs
            component_runs, interim_ids = pipeline_runs_service.add_recursive(
                uid=self.uuid,
                pipeline_uri=self._pipeline_uri,
                job_uri=self._job_uri,
                job_run_uid=self._job_run_uid,
                task_run_uid=self._task_run_uid,
                status=pipeline_status,
                submission_time=self._submission_time,
                fabric_uid=self._fabric_uid,
                time_taken=now_millis() - self._time_started,
                rows_read=self._rows_read,
                rows_written=self._rows_written,
                run_type=self._run_type,
                created_by=self._created_by,
                code=self._code,
                interims=self._interims,
                branch=self._branch,
                expected_interims=num_expected_interims,
                actual_interims=num_actual_interims,
                logs=compressed_logs,
                pipeline_config_opt=self._pipeline_config,
                gem_progress_map=self._process_to_gem_map,
            )

            self.logger.info(f"Successfully executed offload {int(time.time() * 1000)}")
            return component_runs, interim_ids

        except UnavailableWorkflowJsonException as e:
            self.logger.error(
                f"Offload failed at {int(time.time() * 1000)} because of UnavailableWorkflowJson "
                f"failure for pipelineId {self._pipeline_uri} and spark-conf for path "
                f"{self.spark.conf.get('spark.prophecy.packages.path', 'N/A')}"
            )
            return [], []
        except Exception as e:
            self.logger.error(f"Offload failed at {int(time.time() * 1000)}: {e}")
            raise

    def _is_databricks_environment(self) -> bool:
        """Check if running in Databricks environment."""
        return is_databricks_environment(self.spark)

    def _create_pipeline_runs_service(self) -> PipelineRunsService:
        """Create pipeline runs service instance."""

        return PipelineRunsService.create(self.spark, self._storage_metadata)

    def _process_to_component_name_map(self) -> Dict[str, ComponentDetails]:
        """Get mapping from process ID to component details."""
        if not self._graph:
            return {}

        component_details_list = self._get_component_details(self._graph, "graph")
        return {cd.process_id: cd for cd in component_details_list}

    def _get_component_details(
        self, graph: WorkflowGroup, subgraph_name: str
    ) -> List[ComponentDetails]:
        """Extract component details from workflow graph."""
        target_port_connection_map = {
            edge.target_port: edge for edge in graph.connections
        }

        component_details_list = []

        for process_id, node in graph.processes.items():
            if isinstance(node, WorkflowGroup):
                # Handle subgraph
                component_name = node.metadata.get("slug", "")
                component_type = node.component

                interim_ports = [p.id for p in node.ports.outputs]
                gem_progress = (
                    self._process_to_gem_map.get(process_id)
                    if self._process_to_gem_map
                    else None
                )

                if not interim_ports:
                    component_details_list.append(
                        ComponentDetails(
                            component_uri="",
                            component_type=component_type,
                            process_id=process_id,
                            component_name=component_name,
                            interim_process_id=process_id,
                            interim_component_name=component_name,
                            interim_subgraph_name=subgraph_name,
                            interim_out_port_id="",
                            gem_progress=gem_progress,
                        )
                    )
                else:
                    for port in interim_ports:
                        component_details_list.append(
                            ComponentDetails(
                                component_uri="",
                                component_type=component_type,
                                process_id=process_id,
                                component_name=component_name,
                                interim_process_id=process_id,
                                interim_component_name=component_name,
                                interim_subgraph_name=subgraph_name,
                                interim_out_port_id=port,
                                gem_progress=gem_progress,
                            )
                        )

                # Recursively process subgraph
                component_details_list.extend(
                    self._get_component_details(node, component_name)
                )
            else:
                # Handle regular node
                component_name = node.metadata.get("slug", "")
                component_type = node.component

                # Default interim details
                interim_subgraph = subgraph_name
                interim_node = node
                interim_ports = [p.id for p in node.ports.outputs]

                # Special handling for Target nodes
                if component_type == "Target" and node.ports.inputs:
                    first_input_port = node.ports.inputs[0].id
                    connection, parent_graph, target_subgraph = (
                        self._fetch_target_component_source_port(
                            target_port_connection_map,
                            graph,
                            subgraph_name,
                            first_input_port,
                        )
                    )

                    if connection and connection.source in parent_graph.processes:
                        interim_node = parent_graph.processes[connection.source]
                        interim_subgraph = target_subgraph
                        interim_ports = [connection.source_port]

                interim_process_id = interim_node.id
                interim_component_name = interim_node.metadata.get("slug", "")
                gem_progress = (
                    self._process_to_gem_map.get(process_id)
                    if self._process_to_gem_map
                    else None
                )

                if not interim_ports:
                    component_details_list.append(
                        ComponentDetails(
                            component_uri="",
                            component_type=component_type,
                            process_id=process_id,
                            component_name=component_name,
                            interim_process_id=interim_process_id,
                            interim_component_name=interim_component_name,
                            interim_subgraph_name=interim_subgraph,
                            interim_out_port_id="",
                            gem_progress=gem_progress,
                        )
                    )
                else:
                    for port in interim_ports:
                        component_details_list.append(
                            ComponentDetails(
                                component_uri="",
                                component_type=component_type,
                                process_id=process_id,
                                component_name=component_name,
                                interim_process_id=interim_process_id,
                                interim_component_name=interim_component_name,
                                interim_subgraph_name=interim_subgraph,
                                interim_out_port_id=port,
                                gem_progress=gem_progress,
                            )
                        )

        return component_details_list

    def _fetch_target_component_source_port(
        self,
        target_port_connection_map: Dict[str, WorkflowEdge],
        graph: "HasProcessesConnectionsPorts",
        subgraph_name: str,
        port: str,
    ) -> Tuple[Optional[WorkflowEdge], "HasProcessesConnectionsPorts", str]:
        """
        Recursively fetch the source port for a target component.

        This handles cases where target components connect through subgraphs.
        """
        connection = target_port_connection_map.get(port)
        if not connection:
            return None, graph, subgraph_name

        source_node = graph.processes.get(connection.source)
        if isinstance(source_node, WorkflowGroup):
            # Source is a subgraph, recurse into it
            source_subgraph_name = source_node.metadata.get("slug", "")
            subgraph_target_port_map = {
                edge.target_port: edge for edge in source_node.connections
            }
            return self._fetch_target_component_source_port(
                subgraph_target_port_map,
                source_node,
                source_subgraph_name,
                connection.source_port,
            )
        else:
            return connection, graph, subgraph_name

    def __str__(self) -> str:
        """String representation of the store state."""
        gems_in_pipeline = []
        if self._slug_to_process_id_map:
            gems_in_pipeline = list(self._slug_to_process_id_map.keys())

        gems_progress = []
        if self._process_to_gem_map:
            gems_progress = [
                json.dumps(gp.to_dict(), indent=2)
                for gp in self._process_to_gem_map.values()
            ]

        file_names = []
        if self._code:
            file_names = list(self._code.keys())

        return f"""(
uuid = {self.uuid}
pipelineURI = {self._pipeline_uri}
jobURI = {self._job_uri}
jobRunUID = {self._job_run_uid}
taskRunUID = {self._task_run_uid}
status = {self._status}
fabricUID = {self._fabric_uid}
timeTaken = {self._time_taken}
rowsRead = {self._rows_read}
rowsWritten = {self._rows_written}
runType = {self._run_type}
createdBy = {self._created_by}
gemsInPipeline = [{', '.join(gems_in_pipeline)}]
gemsProgress = [{', '.join(gems_progress)}]
  -- number of files = {len(self._code) if self._code else 0}
     file names - [{', '.join(file_names)}]
  -- number of interims = {len(self._interims)}
)"""
