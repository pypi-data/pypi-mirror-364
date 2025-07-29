# WARNING - Do not add import * in this module
from pyspark import Row
from pyspark.sql import SparkSession
from functools import lru_cache
from datetime import datetime, date
import os
import logging

logger = logging.getLogger(__name__)

is_serverless = bool(int(os.environ.get("DATABRICKS_SERVERLESS_MODE_ENABLED", "0")))
logger.info(f'is_serverless is {is_serverless}')

class ConfigBase:

    class SecretValue:
        def __init__(self, prophecy_spark=None, secretScope: str="", secretKey: str="", providerType: str="Databricks", **kwargs):
            self.prophecy_spark = prophecy_spark
            self.secretScope = secretScope
            self.secretKey = secretKey
            self.providerType = providerType

        def __deepcopy__(self, memo):
            import copy
            from pyspark.sql import SparkSession
            cls = self.__class__
            result = cls.__new__(cls)
            memo[id(self)] = result
            for k, v in self.__dict__.items():
                if isinstance(v, SparkSession):
                    setattr(result, k, v)
                else:
                    setattr(result, k, copy.deepcopy(v, memo))
            return result

        @lru_cache()
        def __str__(self):
            if is_serverless:
                from prophecy.utils.secrets import ProphecySecrets
                self.secret_manager = ProphecySecrets
                return self.secret_manager.get(self.secretScope, self.secretKey, self.providerType)

            if (self.prophecy_spark is not None and self.prophecy_spark.sparkContext.getConf().get("prophecy.schema.analysis") == "True"):
                return f"{self.secretScope}:{self.secretKey}"
            self.jvm = self.prophecy_spark.sparkContext._jvm
            self.secret_manager = self.jvm.io.prophecy.libs.secrets.ProphecySecrets
            return self.secret_manager.get(self.secretScope, self.secretKey, self.providerType)

    def updateSpark(self, spark):
        self.spark = spark

    def get_dbutils(self, spark):
        try:
            dbutils  # Databricks provides an instance of dbutils be default. Checking for it's existence
            return dbutils
        except NameError:
            try:
                from pyspark.dbutils import DBUtils

                _dbutils = DBUtils(spark)
            except:
                try:
                    import IPython

                    _dbutils = IPython.get_ipython().user_ns["dbutils"]
                except Exception as e:
                    from prophecy.test.utils import ProphecyDBUtil

                    _dbutils = ProphecyDBUtil

            return _dbutils

    def get_int_value(self, value):
        if value is not None:
            return int(value)
        else:
            return value

    def get_float_value(self, value):
        if value is not None:
            return float(value)
        else:
            return value

    def get_bool_value(self, value):
        if value is not None:
            return bool(value)
        else:
            return value

    def get_timestamp_value(self, value):
        if value is None:
            return value
        if type(value) is datetime:
            return value
        if type(value) is date:
            return datetime.combine(value, datetime.min.time())
        if type(value) is str and value != "":
            formats = [
                # with timezone
                "%d-%m-%YT%H:%M:%SZ%z", # default format that prophecy uses
                "%d-%m-%Y %H:%M:%S %z",
                "%d-%m-%YT%H:%M:%S.%fZ%z",
                "%d-%m-%YT%H:%M:%S.%f%z",
                "%d-%m-%YT%H:%M:%S%z",
                "%d-%m-%Y %H:%M:%S.%f %z",
                "%d-%m-%Y %H:%M:%S.%f%z",
                "%d-%m-%Y %H:%M:%S%z",
                # without timezone
                "%d-%m-%YT%H:%M:%S.%f",
                "%d-%m-%YT%H:%M:%S",
                "%d-%m-%Y %H:%M:%S.%f",
                "%d-%m-%Y %H:%M:%S",

                # other formats
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%m-%d-%YT%H:%M:%S.%f%z",
                "%m-%d-%YT%H:%M:%S%z",
                "%m-%d-%Y %H:%M:%S.%f%z",
                "%m-%d-%Y %H:%M:%S%z",
                "%m-%d-%YT%H:%M:%S.%f",
                "%m-%d-%YT%H:%M:%S",
                "%m-%d-%Y %H:%M:%S.%f",
                "%m-%d-%Y %H:%M:%S",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue

            raise ValueError(f"Timestamp string '{value}' does not match any known formats.")
        return None

    def get_date_value(self, value):
        if type(value) is date:
            return value
        if type(value) is str and value != "":
            formats = [
                # date
                "%Y-%m-%d",
                "%m-%d-%Y",
                "%d-%m-%Y",

                "%Y/%m/%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

            raise ValueError(f"Date string '{value}' does not match any known formats.")
        return None

    def get_date_list(self, date_list):
        if date_list is None:
            return date_list
        if isinstance(date_list, list):
            return [self.get_date_value(x) for x in date_list]
        else:
            raise ValueError(f"Expected a list of dates, but got {type(date_list)}")

    def get_timestamp_list(self, timestamp_list):
        if timestamp_list is None:
            return timestamp_list
        if isinstance(timestamp_list, list):
            return [self.get_timestamp_value(x) for x in timestamp_list]
        else:
            raise ValueError(f"Expected a list of timestamps, but got {type(timestamp_list)}")

    # Old function, keeping it for backward compatibility
    def generate_object(self, value, cls):
        if isinstance(value, list):
            return [self.generate_object(x, cls) for x in value]
        elif isinstance(value, dict):
            return cls(**value)
        return value

    # Old function, keeping it for backward compatibility
    def get_object(self, default, override, cls):
        if override == None:
            return default
        else:
            return self.generate_object(override, cls)

    def generate_config_object(self, spark, value, cls):
        if isinstance(value, list):
            return [self.generate_config_object(spark, x, cls) for x in value]
        elif isinstance(value, dict):
            return cls(**{**{"prophecy_spark": spark}, **value})
        return value

    def get_secret_config_object(self, spark, default, override, cls):
        if isinstance(override, str) and override.count(":") == 1:
            parts = override.split(":")
            values = {"providerType": "Databricks", "secretScope": parts[0], "secretKey": parts[1]}
            return self.get_config_object(spark, default, values, cls)
        else:
            return self.get_config_object(spark, default, override, cls)

    def get_config_object(self, spark, default, override, cls):
        if override == None:
            return default
        else:
            return self.generate_config_object(spark, override, cls)

    def to_dict(self):
        to_ignore = ["spark", "prophecy_spark", "jvm", "secret_manager"]
        def to_dict_recursive(obj):
            def should_include(key, value):
                # remove any unwanted objects from the config:
                return key not in to_ignore and not isinstance(value, SparkSession)
            if isinstance(obj, (list, tuple)):
                return [to_dict_recursive(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: to_dict_recursive(value) for key, value in obj.items() if should_include(key, value)}
            elif type(obj) is date:
                return obj.strftime("%d-%m-%Y")
            elif type(obj) is datetime:
                if obj.tzinfo is None:
                    return obj.strftime("%d-%m-%YT%H:%M:%SZ")
                else:
                    return obj.strftime("%d-%m-%YT%H:%M:%SZ%z")
            elif hasattr(obj, "__dict__"):
                return to_dict_recursive({key: value for key, value in obj.__dict__.items() if should_include(key, value)})
            elif hasattr(obj, "__slots__"):
                return to_dict_recursive({slot: getattr(obj, slot) for slot in obj.__slots__ if should_include(slot, getattr(obj, slot))})
            else:
                return obj
        return to_dict_recursive(self)

    def update_all(self, name, new_value):
        def process_attr_value(attr_val):
            if isinstance(attr_val, ConfigBase):
                attr_val.update_all(name, new_value)
            elif isinstance(attr_val, list) or isinstance(attr_val, tuple):
                for element in attr_val:
                    if isinstance(element, ConfigBase):
                        element.update_all(name, new_value)
            elif isinstance(attr_val, dict):
                for k, v in attr_val.items():
                    if isinstance(v, ConfigBase):
                        v.update_all(name, new_value)
            else:
                pass

        if hasattr(self, "__dict__"):
            for attr_name, attr_val in self.__dict__.items():
                if attr_name == name:
                    setattr(self, attr_name, new_value)
                else:
                    process_attr_value(attr_val)
        if hasattr(self, "__slots__"):
            for attr_name in self.__slots__:
                if attr_name == name:
                    setattr(self, attr_name, new_value)
                else:
                    process_attr_value(getattr(self, attr_name))
        else:
            pass

    def find_spark(self, instance):
        if isinstance(instance, list):
            for element in instance:
                spark = self.find_spark(element)
                if spark is not None:
                    return spark
        if isinstance(instance, ConfigBase) or isinstance(instance, ConfigBase.SecretValue):
            if hasattr(instance, "spark") and isinstance(instance.spark, SparkSession):
                    return instance.spark
            elif hasattr(instance, "prophecy_spark") and isinstance(instance.prophecy_spark, SparkSession):
                    return instance.prophecy_spark
            for key, value in instance.__dict__.items():
                    spark = self.find_spark(value)
                    if spark is not None:
                        return spark
        return None

    def update_from_row(self, row: Row):
        import copy
        new_config = copy.deepcopy(self)
        spark_variable = self.find_spark(self)
        updated_config_json = {**new_config.to_dict(), **row.asDict(recursive=True)}
        return self.get_config_object(spark_variable, new_config, updated_config_json, new_config.__class__)

    def update_from_row_map(self, row: Row, config_to_column: dict):
        import copy
        new_config = copy.deepcopy(self)
        spark_variable = self.find_spark(self)
        row_as_dict = row.asDict(recursive=True)
        overridden_values = {}
        for config_name, column_name in config_to_column.items():
            overridden_values[config_name] = row_as_dict[column_name]
        updated_config_json = {**new_config.to_dict(), **overridden_values}
        return self.get_config_object(spark_variable, new_config, updated_config_json, new_config.__class__)

    def __deepcopy__(self, memo):
        import copy
        from pyspark.sql import SparkSession
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if isinstance(v, SparkSession):
                setattr(result, k, v)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result
