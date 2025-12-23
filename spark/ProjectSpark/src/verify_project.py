from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
import os

print("Starting Verification...")

# Init Spark
spark = SparkSession.builder \
    .appName("ProjectSpark-Verify") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

print(f"Spark Version: {spark.version}")

# Path setup (Inside Docker, /home/ubuntu is mounted to /home/jovyan/work)
# Input: /home/jovyan/work/ProjectSpark/data/raw/2015-01-01-15.json
input_path = "/home/jovyan/work/ProjectSpark/data/raw/2015-01-01-15.json"
output_path = "/home/jovyan/work/ProjectSpark/data/processed/verify_output"

if not os.path.exists(input_path):
    # Fallback to relative path if running locally or different mount
    # But inside container it should be absolute
    print(f"Checking path: {input_path}")
    # try listing dir
    print(os.listdir("/home/jovyan/work/ProjectSpark/data/raw/"))

try:
    print(f"Reading {input_path}...")
    df_raw = spark.read.json(input_path)
    print(f"Count Raw: {df_raw.count()}")
    
    # Logic from Notebook 2
    df_push = df_raw.filter(df_raw.type == "PushEvent")
    print(f"Count Push: {df_push.count()}")
    
    df_flat = (
        df_push
        .select(
            col("id").alias("event_id"),
            col("created_at").alias("event_time"),
            col("actor.login").alias("actor_login"),
            col("repo.name").alias("repo_name"),
            explode(col("payload.commits")).alias("commit")
        )
    )
    
    df_final = df_flat.select(
        col("event_id"),
        col("event_time"),
        col("actor_login"),
        col("repo_name"),
        col("commit.sha").alias("commit_sha"),
        col("commit.message").alias("commit_message")
    )
    
    print("Showing sample output:")
    df_final.show(5)
    
    print(f"Saving to {output_path}...")
    df_final.write.mode("overwrite").csv(output_path)
    print("Verification Successful!")

except Exception as e:
    print(f"Verification FAILED: {e}")
    import traceback
    traceback.print_exc()

spark.stop()
