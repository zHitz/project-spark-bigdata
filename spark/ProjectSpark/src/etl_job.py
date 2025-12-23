import sys
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

def process_data(filename):
    print(f"Starting processing for file: {filename}")
    
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("ProjectSpark-ETL") \
        .getOrCreate()
    
    # Paths (Assumes running inside Docker mapped volumes)
    # /home/jovyan/work corresponds to /home/ubuntu/spark
    base_path = "/home/jovyan/work/ProjectSpark"
    input_path = f"{base_path}/data/raw/{filename}"
    output_csv = f"{base_path}/data/processed/github_commits_flat.csv"
    
    # Check if file exists (optional, Spark handles missing files with error)
    
    print(f"Reading from: {input_path}")
    df_raw = spark.read.json(input_path)
    
    # Filter PushEvents
    df_push = df_raw.filter(df_raw.type == "PushEvent")
    
    # Flatten
    df_flat = df_push.select(
        col("id").alias("event_id"),
        col("created_at").alias("event_time"),
        col("actor.login").alias("actor_login"),
        col("repo.name").alias("repo_name"),
        explode(col("payload.commits")).alias("commit")
    ).select(
        col("event_id"),
        col("event_time"),
        col("actor_login"),
        col("repo_name"),
        col("commit.sha").alias("commit_sha"),
        col("commit.author.name").alias("author_name"),
        col("commit.author.email").alias("author_email"),
        col("commit.message").alias("commit_message")
    )
    
    # Write Output
    print(f"Writing to: {output_csv}")
    df_flat.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .option("quoteAll", "true") \
        .csv(output_csv)
        
    print("ETL Job Completed Successfully")
    spark.stop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python etl_job.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    process_data(filename)
