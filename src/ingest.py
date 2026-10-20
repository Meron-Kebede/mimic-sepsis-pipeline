import os
import duckdb

def ingest_mimic_data():
    print("Connecting to DuckDB engine...")
    con = duckdb.connect(database=':memory:')

    req_hosp_patients = 'data/raw/hosp/patients.csv.gz'
    req_hosp_admissions = 'data/raw/hosp/admissions.csv.gz'
    req_icu_stays = 'data/raw/icu/icustays.csv.gz'

    for f in [req_hosp_patients, req_hosp_admissions, req_icu_stays]:
        if not os.path.exists(f):
            print(f"Missing file: {f}")
            return
    
    # Join patient demographics, admissions, and ICU stays
    query = f"""
    SELECT 
        p.subject_id,
        a.hadm_id,
        i.stay_id,
        p.gender,
        p.anchor_age + (
            EXTRACT(YEAR FROM a.admittime) - p.anchor_year
        ) AS age,
        a.admission_type,
        i.intime,
        a.hospital_expire_flag AS mortality_label
    FROM '{req_hosp_patients}' p
    JOIN '{req_hosp_admissions}' a 
        ON p.subject_id = a.subject_id
    JOIN '{req_icu_stays}' i 
        ON a.hadm_id = i.hadm_id;
    """

    print("Executing DuckDB query across raw compressed MIMIC-IV files...")
    df = con.execute(query).df()
    print(f"Extracted {len(df)} ICU stay records.")
    
    # Save extracted cohort
    output_path = 'data/processed/cohort_raw.csv'
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved raw cohort to {output_path}")
    
if __name__ == "__main__":
    ingest_mimic_data()