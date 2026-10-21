import os
from google.cloud import bigquery

def build_features():
    output_path = 'data/processed/features.csv'
    sql_path = 'sql/extract_features.sql'

    # Load SQL Query
    with open(sql_path, 'r', encoding='utf-8') as file:
        query = file.read()

    # Run in BigQuery 
    print("Extracting first-24-hour vital signs from BigQuery...")
    client = bigquery.Client(project='mimic-sepsis-pipeline')
    df = client.query(query).to_dataframe()

    # Validate extracted features
    if df.empty:
        raise ValueError("Extracted feature matrix is empty")

    if not df['stay_id'].is_unique:
        raise ValueError("Duplicate ICU stay IDs found")

    # Save extracted features 
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Feature matrix saved to {output_path}")    

    print("\nFEATURE SUMMARY")
    print(f"Total ICU Stays: {df.shape[0]}")
    print(f"Total Features:  {df.shape[1] - 1}")
    print("\nMissing Values Per Feature:")
    print(df.isna().sum())
    
if __name__ == "__main__":
    build_features()