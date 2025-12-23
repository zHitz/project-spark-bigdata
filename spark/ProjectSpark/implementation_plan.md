# ProjectSpark Implementation Plan: Complex Nested JSON Analysis

## Goal Description
Implement a Big Data processing pipeline using Apache Spark to analyze complex nested JSON data from GitHub Archive (Topic 25).
The system will ingest raw JSON logs (5-6 levels deep), flatten them into a relational tabular format using Spark SQL (`explode`, `posexplode`), and generate analytical insights (CSV output) for reporting.

## User Review Required
> [!IMPORTANT]
> The sample data `2015-01-01-15.json` is located in `Present/artifact`. I will use this for the demo.
> I will use the existing Docker Spark stack we set up in `/home/ubuntu`. I will assume you run the code from the Jupyter Notebook environment.

## Proposed Changes

### 1. Workspace Organization
- Create `src` (Source Code) directory in `ProjectSpark`.
- Create `data/raw` and `data/processed` directories for data management.

### 2. Implementation Code (Jupyter Notebooks / Python Scripts)
#### [NEW] [1_ingest_and_explore.ipynb](file:///home/ubuntu/ProjectSpark/src/1_ingest_and_explore.ipynb)
- Load the raw JSON data.
- Print schema to visualize the nested structure.
- Count original records.

#### [NEW] [2_flatten_data.ipynb](file:///home/ubuntu/ProjectSpark/src/2_flatten_data.ipynb)
- **Core Logic**: Use `explode` and `posexplode` to unnest `commits` array and flatten fields.
- Extract key fields: `actor`, `repo`, `payload.commits` details.
- Save the result as CSV and Parquet.

#### [NEW] [3_analyze_dashboard.ipynb](file:///home/ubuntu/ProjectSpark/src/3_analyze_dashboard.ipynb)
- Perform analysis on flattened data:
    - Top 10 Active Repositories.
    - Top 10 Contributors.
    - Activity by Hour (if applicable).
- Generate visualizations (using `matplotlib` or just tables) for the report.

### 3. Documentation & Reporting support
#### [NEW] [REPORT_CONTENT.md](file:///home/ubuntu/ProjectSpark/REPORT_CONTENT.md)
- Draft text for the Word/PDF report:
    - Problem Statement.
    - System Architecture Diagram (Mermaid).
    - Technology constraints/benefits (Spark vs others).
    - Installation Guide.

#### [NEW] [SLIDES_OUTLINE.md](file:///home/ubuntu/ProjectSpark/SLIDES_OUTLINE.md)
- Bullet points for the PowerPoint presentation.

## Verification Plan
### Automated Tests
- Run the extraction pipeline on the sample `2015-01-01-15.json`.
- Verify output CSV exists and has columns like `actor_login`, `repo_name`, `commit_message`.
- Verify rows count matches expected exploded actions.

### Manual Verification
- Open the generated CSV in Jupyter to confirm readability.
- Check if the "Dashboard" charts are generated correctly in the notebook.
