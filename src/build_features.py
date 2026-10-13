import duckdb

def main():
    print("Connecting in-memory DuckDB engine...")
    con = duckdb.connect()

    query = """
        WITH cohort AS (
        SELECT
            i.subject_id,
            i.stay_id,
            a.hadm_id,
            i.intime,
            p.gender,
            p.anchor_age,
            a.hospital_expire_flag AS mortality_label
        FROM 'data/icu/icustays.csv.gz' i
        JOIN 'data/hosp/patients.csv.gz' p ON i.subject_id = p.subject_id 
        JOIN 'data/hosp/admissions.csv.gz' a ON i.hadm_id = a.hadm_id
        WHERE p.anchor_age >= 18
        ),
        first_day_vitals AS (
        SELECT
            c.stay_id,
            MAX(CASE WHEN c.itemid = 220045 THEN c.valuenum END) AS max_heart_rate,
            MIN(CASE WHEN c.itemid = 220045 THEN c.valuenum END) AS min_heart_rate,
            AVG(CASE WHEN c.itemid = 220045 THEN c.valuenum END) AS mean_heart_rate,

            AVG(CASE WHEN c.itemid = 220050 THEN c.valuenum END) AS mean_sbp,
            MIN(CASE WHEN c.itemid = 220050 THEN c.valuenum END) AS min_sbp,

            AVG(CASE WHEN c.itemid = 220210 THEN c.valuenum END) AS mean_resp_rate
        FROM 'data/icu/chartevents.csv.gz' c
        JOIN cohort ON cohort.stay_id = c.stay_id 
            WHERE itemid IN (220045, 220050, 220210) 
            AND c.charttime >= cohort.intime
            AND c.charttime <= cohort.intime + INTERVAL '24 HOURS'
        GROUP BY c.stay_id
        )
        SELECT *
        FROM cohort 
        LEFT JOIN first_day_vitals v ON cohort.stay_id = v.stay_id;
    """

    print("Executing cohort and 24hr vitals extraction query...")
    df = con.execute(query).df()
    
    print("\nFEATURE SUMMARY")
    print(f"Total Rows (Patients): {df.shape[0]}")
    print(f"Total Feature Columns:  {df.shape[1]}")
    print("\nVitals for First 5 Patients in Cohort:")
    print(df.head())

    return df
    
    
if __name__ == "__main__":
    main()