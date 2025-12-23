from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# Path to the processed CSV file
CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed/github_commits_flat.csv'))

import json

# Configuration
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/raw'))
PROCESSED_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed'))
METADATA_FILE = os.path.join(PROCESSED_FOLDER, 'metadata.json')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_active_file():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f).get('active_file', 'Unknown')
        except:
            return 'Unknown'
    return 'None (Run ETL first)'

def set_active_file(filename):
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    with open(METADATA_FILE, 'w') as f:
        json.dump({'active_file': filename, 'last_updated': str(pd.Timestamp.now())}, f)

@app.route('/')
def index():
    return render_template('index.html')

# --- DATA MANAGEMENT APIs ---

@app.route('/api/files', methods=['GET'])
def list_files():
    """List all available JSON/GZ files in raw directory."""
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.json') or f.endswith('.json.gz')]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a new file from user."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": f"File {filename} uploaded successfully"}), 200

@app.route('/api/processed_files', methods=['GET'])
def list_processed_files():
    """List available processed datasets."""
    try:
        # List all items in processed folder
        items = os.listdir(PROCESSED_FOLDER)
        # Filter logic: We assume folders or CSVs are valid datasets
        datasets = [f for f in items if f.endswith('.csv') or os.path.isdir(os.path.join(PROCESSED_FOLDER, f))]
        # Filter out metadata.json or hidden files
        datasets = [d for d in datasets if d != 'metadata.json' and not d.startswith('.')]
        return jsonify({"datasets": datasets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/select_source', methods=['POST'])
def select_source():
    """Manually select an existing processed dataset."""
    data = request.json
    filename = data.get('filename')
    if not filename:
         return jsonify({"error": "Filename required"}), 400
    
    set_active_file(filename)
    return jsonify({"message": f"Switched to dataset: {filename}"})

@app.route('/api/process', methods=['POST'])
def process_data():
    """Trigger Spark Job via Docker."""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "Filename is required"}), 400
    
    # Command to run inside the Jupyter container
    # map local /home/ubuntu/spark to /home/jovyan/work
    cmd = [
        "docker", "exec", "jupyter-notebook", 
        "python3", "/home/jovyan/work/ProjectSpark/src/etl_job.py", filename
    ]
    
    try:
        # Run blocking (for demo simplicity)
        import subprocess # Local import to ensure it exists
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            set_active_file(filename) # <--- Save state
            return jsonify({"message": "Processing Complete!", "logs": result.stdout})
        else:
            return jsonify({"error": "Processing Failed", "details": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/raw_data', methods=['GET'])
def get_raw_data():
    """Get the first 500 rows of processed data for the table."""
    try:
        active_file = get_active_file()
        if active_file and active_file != 'Unknown' and active_file != 'None (Run ETL first)':
             target_path = os.path.join(PROCESSED_FOLDER, active_file)
        else:
             target_path = CSV_PATH

        current_csv_path = target_path
        
        if os.path.isdir(current_csv_path):
            found = False
            for f in os.listdir(current_csv_path):
                if f.startswith("part-") and f.endswith(".csv"):
                    current_csv_path = os.path.join(current_csv_path, f)
                    found = True
                    break
            if not found:
                return jsonify({"error": "No CSV part found in dataset"}), 404
        
        if not os.path.exists(current_csv_path):
             return jsonify({"error": f"Data file not found: {active_file}"}), 404
        
        # Read limited rows for performance
        df = pd.read_csv(current_csv_path, quotechar='"', encoding='utf-8', on_bad_lines='skip', nrows=500)
        
        return jsonify({
            "columns": df.columns.tolist(),
            "data": df.fillna("").astype(str).values.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ANALYTICS API (Existing) ---
@app.route('/api/stats')
def stats():
    active_file = get_active_file()
    
    active_file = get_active_file()
    
    try:
        # Determine Path based on Active File
        if active_file and active_file != 'Unknown' and active_file != 'None (Run ETL first)':
             target_path = os.path.join(PROCESSED_FOLDER, active_file)
        else:
             target_path = CSV_PATH # Fallback

        current_csv_path = target_path
        
        # Handle directory limits (Spark output is a dir containing CSVs)
        if os.path.isdir(current_csv_path):
            found = False
            for f in os.listdir(current_csv_path):
                if f.startswith("part-") and f.endswith(".csv"):
                    current_csv_path = os.path.join(current_csv_path, f)
                    found = True
                    break
            if not found:
                 # If no part file found in dir, maybe the user selected a non-spark dir?
                 return jsonify({"total_commits": 0, "active_file": active_file, "error": "No CSV found in dataset"})
        
        if not os.path.exists(current_csv_path):
            return jsonify({"total_commits": 0, "active_file": active_file, "error": f"File not found: {active_file}"})

        # Read CSV with robust options
        df = pd.read_csv(current_csv_path, quotechar='"', encoding='utf-8', on_bad_lines='skip')
        
        if df.empty:
             return jsonify({
                "total_commits": 0, "unique_authors": 0, "unique_repos": 0,
                "top_authors": {"labels":[], "data":[]}, "top_repos": {"labels":[], "data":[]}, 
                "top_orgs": {"labels":[], "data":[]}, "top_domains": {"labels":[], "data":[]},
                "hourly_activity": {"labels":[], "data":[]}, "msg_length": {"labels":[], "data":[]},
                "active_file": active_file
            })

        # Prepare Data
        # Extract Organization
        df['org'] = df['repo_name'].apply(lambda x: x.split('/')[0] if isinstance(x, str) and '/' in x else 'Unknown')
        
        # Extract Domain
        df['domain'] = df['author_email'].apply(lambda x: x.split('@')[1] if isinstance(x, str) and '@' in x else 'Unknown')
        
        # Extract Hour (Safely)
        try:
            df['event_time'] = pd.to_datetime(df['event_time'], errors='coerce', utc=True)
            df = df.dropna(subset=['event_time']) 
            
            if df.empty:
                return jsonify({"total_commits": 0, "active_file": active_file, "error": "No valid dates found in data"})

            df['hour'] = df['event_time'].dt.hour
        except Exception as dt_err:
             print(f"Date conversion error: {dt_err}")
             return jsonify({"total_commits": len(df), "active_file": active_file, "error": f"Date parsing failed: {str(dt_err)}"})

        # METRICS
        top_authors = df['actor_login'].value_counts().head(10).to_dict()
        top_repos = df['repo_name'].value_counts().head(10).to_dict()
        top_orgs = df['org'].value_counts().head(10).to_dict()
        top_domains = df['domain'].value_counts().head(10).to_dict()
        hourly_activity = df['hour'].value_counts().sort_index().to_dict()
        
        df['msg_len'] = df['commit_message'].str.len().fillna(0)
        len_bins = pd.cut(df['msg_len'], bins=[0, 20, 50, 100, 500], labels=['Short', 'Medium', 'Long', 'Very Long']).value_counts().to_dict()

        return jsonify({
            "total_commits": len(df),
            "unique_authors": df['actor_login'].nunique(),
            "unique_repos": df['repo_name'].nunique(),
            "top_authors": {"labels": list(top_authors.keys()), "data": list(top_authors.values())},
            "top_repos": {"labels": list(top_repos.keys()), "data": list(top_repos.values())},
            "top_orgs": {"labels": list(top_orgs.keys()), "data": list(top_orgs.values())},
            "top_domains": {"labels": list(top_domains.keys()), "data": list(top_domains.values())},
            "hourly_activity": {"labels": list(hourly_activity.keys()), "data": list(hourly_activity.values())},
            "msg_length": {"labels": list(len_bins.keys()), "data": list(len_bins.values())},
            "active_file": active_file
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "active_file": active_file}), 500

if __name__ == '__main__':
    # Listen on all interfaces so it can be accessed externally
    app.run(host='0.0.0.0', port=5000, debug=True)

