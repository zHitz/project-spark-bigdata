import os
import pandas as pd
import json

PROCESSED_FOLDER = os.path.abspath('/home/ubuntu/spark/ProjectSpark/data/processed')
CSV_PATH = os.path.join(PROCESSED_FOLDER, 'github_commits_flat.csv')

def check_logic(active_file):
    print(f"--- Checking for active_file: {active_file} ---")
    if active_file and active_file != 'Unknown':
         target_path = os.path.join(PROCESSED_FOLDER, active_file)
    else:
         target_path = CSV_PATH
    
    print(f"Target Path: {target_path}")
    print(f"Exists: {os.path.exists(target_path)}")
    print(f"Is Dir: {os.path.isdir(target_path)}")

    current_csv_path = target_path
    if os.path.isdir(current_csv_path):
        found = False
        for f in os.listdir(current_csv_path):
            if f.startswith("part-") and f.endswith(".csv"):
                print(f"Found part file: {f}")
                current_csv_path = os.path.join(current_csv_path, f)
                found = True
                break
        if not found:
            print("ERROR: No part file found")
            return

    print(f"Final CSV Path: {current_csv_path}")
    
    try:
        df = pd.read_csv(current_csv_path, quotechar='"', encoding='utf-8', on_bad_lines='skip', nrows=10)
        print(f"Read Success. Shape: {df.shape}")
        print(df.head(1))
    except Exception as e:
        print(f"Read Failed: {e}")

check_logic("github_commits_flat.csv")
