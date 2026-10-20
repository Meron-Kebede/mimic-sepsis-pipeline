import os
from google.cloud import bigquery

def extract_cohort():
    output_path = 'data/processed/cohort_cleaned.csv'
    output_table_id = 'mimic-sepsis-pipeline.sepsis_pipeline.cohort_cleaned'
    sql_path = 'sql/extract_cohort.sql'

    # Load SQL query
    with open(sql_path, 'r', encoding='utf-8') as file:
        query = file.read()

    # Run in BigQuery 
    print("Extracting Sepsis-3 cohort from BigQuery...")
    client = bigquery.Client(project='mimic-sepsis-pipeline')

    job_config = bigquery.QueryJobConfig(
        destination=output_table_id,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    query_job = client.query(query, job_config=job_config)
    df = query_job.to_dataframe()
    print(f"BigQuery result saved to {output_table_id}")

    # Validate extracted cohort
    if df.empty:
        raise ValueError("Extracted cohort is empty")
    
    if not df['stay_id'].is_unique:
        raise ValueError("Duplicate ICU stay IDs found")
    
    if df['mortality_label'].isna().any():
        raise ValueError ("Missing mortality labels found")

    # Save cleaned cohort
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Extracted cohort saved to {output_path}")

    print("\nCOHORT SUMMARY")
    print(f"Total ICU Stays: {len(df)}")
    print(f"Unique Patients: {df['subject_id'].nunique()}")
    print(f"In-Hospital Mortality Rate: {df['mortality_label'].mean():.2%}")


if __name__ == "__main__":
    extract_cohort()