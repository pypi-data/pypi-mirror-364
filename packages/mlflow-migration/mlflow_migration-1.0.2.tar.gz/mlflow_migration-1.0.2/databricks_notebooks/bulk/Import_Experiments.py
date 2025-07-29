# Databricks notebook source
# MAGIC %md ## Import Experiments
# MAGIC
# MAGIC Widgets
# MAGIC * `1. Input directory` - directory of exported experiments.
# MAGIC * `2. Experiment rename file` - Experiment rename file.
# MAGIC * `3. Import permissions`
# MAGIC * `4. Import source tags`
# MAGIC * `5. Use threads` - use multi-threaded import.
# MAGIC
# MAGIC See https://github.com/mlflow-oidc/mlflow-migration/blob/master/README_bulk.md#Import-experiments.

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Input directory", "")
input_dir = dbutils.widgets.get("1. Input directory")
input_dir = input_dir.replace("dbfs:", "/dbfs")

dbutils.widgets.text("2. Experiment rename file", "")
val = dbutils.widgets.get("2. Experiment rename file")
experiment_rename_file = val or None

dbutils.widgets.dropdown("3. Import permissions", "no", ["yes", "no"])
import_permissions = dbutils.widgets.get("3. Import permissions") == "yes"

dbutils.widgets.dropdown("4. Import source tags", "no", ["yes", "no"])
import_source_tags = dbutils.widgets.get("4. Import source tags") == "yes"

dbutils.widgets.dropdown("5. Use threads", "no", ["yes", "no"])
use_threads = dbutils.widgets.get("5. Use threads") == "yes"

print("input_dir:", input_dir)
print("experiment_rename_file:", experiment_rename_file)
print("import_permissions:", import_permissions)
print("import_source_tags:", import_source_tags)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(input_dir, "1. Input directory")

# COMMAND ----------

from mlflow_migration.bulk.import_experiments import import_experiments

import_experiments(
    input_dir=input_dir,
    import_source_tags=import_source_tags,
    experiment_renames=experiment_rename_file,
    import_permissions=import_permissions,
    use_threads=use_threads,
)
