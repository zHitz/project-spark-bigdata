# IPython startup: automatically create spark and sc when a kernel starts
import os
import sys

# Master URL from environment or fallback to spark://spark-master:7077
master = os.environ.get("PYSPARK_MASTER", "spark://spark-master:7077")

# Optional: customize app name or read more confs from env
app_name = os.environ.get("PYSPARK_APP_NAME", "jupyter-notebook")

print(f"Initializing SparkSession with master: {master}")

# Build or get existing SparkSession
try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder \
        .master(master) \
        .appName(app_name) \
        .getOrCreate()
    sc = spark.sparkContext
    # Make available in interactive namespace (IPython does this automatically for startup files)
    print(f"Connected to Spark master at {master}")
    print(f"Spark Version: {spark.version}")
    print(f"SparkContext: {sc}")
except ImportError:
    print("ERROR: PySpark not found. Please ensure it is installed in the environment.")
except Exception as e:
    # don't prevent the kernel from starting; just show an informative message
    print(f"WARNING: could not create SparkSession automatically. Error: {e}")
    import traceback
    traceback.print_exc()
