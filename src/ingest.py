import os
import duckdb
import pandas as pd

def ingest_mimic_data():
    #Use DuckDB to query compressed MIMIC-IV raw files and build a cohort dataset
    print("Connecting to DuckDB engine...")
    con = duckdb.connect(database=':memory:')

    # Check for required core files
    req_hosp_patients = 'data/raw/hosp/patients.csv.gz'
    req_hosp_admissions = 'data/raw/hosp/admissions.csv.gz'
    req_icu_stays = 'data/raw/icu/icustays.csv.gz'

    for f in [req_hosp_patients, req_hosp_admissions, req_icu_stays]:
        if not os.path.exists(f):
            print(f"Missing file: {f}")
            print("Please ensure patients.csv.gz and admissions.csv.gz are in data/raw/hosp/ and icustays.csv.gz is in data/raw/icu/")
            return None

    print("Executing DuckDB query across raw compressed MIMIC-IV files...")
    
    # Query joining core patient demographics and ICU mortality
    query = f"""
    SELECT 
        p.subject_id,
        a.hadm_id,
        i.stay_id,
        p.gender,
        p.anchor_age as age,
        a.admission_type,
        a.hospital_expire_flag as mortality_label
    FROM '{req_hosp_patients}' p
    JOIN '{req_hosp_admissions}' a 
        ON p.subject_id = a.subject_id
    JOIN '{req_icu_stays}' i 
        ON a.hadm_id = i.hadm_id;
    """
    
    df = con.execute(query).df()
    print(f"Ingestion complete! Extracted {len(df)} ICU stay records.")
    
    # Save extracted cohort
    output_path = 'data/processed/cohort_raw.csv'
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved raw cohort to {output_path}")
    
    return df

if __name__ == "__main__":
    ingest_mimic_data()