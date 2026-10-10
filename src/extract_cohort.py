import duckdb

def main():
    print("Connecting in-memory DuckDB engine...")
    con = duckdb.connect()

    query = """
    WITH icu_adults AS (
        SELECT 
            i.subject_id,
            i.hadm_id,
            i.stay_id,
            p.gender,
            p.anchor_age,
            i.intime,
            i.outtime,
            i.los AS icu_length_of_stay_days,
            a.hospital_expire_flag AS mortality_label
        FROM 'data/icu/icustays.csv.gz' i
        JOIN 'data/hosp/patients.csv.gz' p ON i.subject_id = p.subject_id
        JOIN 'data/hosp/admissions.csv.gz' a ON i.hadm_id = a.hadm_id
        WHERE p.anchor_age >= 18
    )
    SELECT * 
    FROM icu_adults
    ORDER BY subject_id, intime;
    """

    print("Executing cohort extraction query...")
    df = con.execute(query).df()

    print("\nCOHORT SUMMARY")
    print(f"Total Adult ICU Admissions: {len(df)}")
    print(f"In-Hospital Mortality Rate: {df['mortality_label'].mean():.2%}")
    print("\nFirst 5 Patients in Cohort:")
    print(df.head())


if __name__ == "__main__":
    main()