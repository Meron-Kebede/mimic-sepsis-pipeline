-- Extract adult ICU patients with sepsis from MIMIC-IV 3.1
-- Only include patients still in the ICU after 24 hours whose
-- antibiotic, culture, and SOFA timestamps fall within that time.
-- Since Sepsis-3 is calculated retrospectively, some information
-- used to identify sepsis may not have been available at 24 hours.

WITH cohort AS (
    SELECT
        s.subject_id,
        s.stay_id,
        i.hadm_id,
        i.intime,
        i.outtime,
        a.dischtime,
        s.antibiotic_time,
        s.culture_time,
        s.sofa_time,
        a.hospital_expire_flag AS mortality_label,
        p.gender,
        a.admission_type,
        p.anchor_age
            + EXTRACT(YEAR FROM a.admittime)
            - p.anchor_year AS age,
        DATETIME_ADD(i.intime, INTERVAL 24 HOUR) AS prediction_time
    FROM `physionet-data.mimiciv_3_1_derived.sepsis3` s
    JOIN `physionet-data.mimiciv_3_1_icu.icustays` i
        ON s.stay_id = i.stay_id
    JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a
        ON i.hadm_id = a.hadm_id
    JOIN `physionet-data.mimiciv_3_1_hosp.patients` p
        ON s.subject_id = p.subject_id
    WHERE s.sepsis3 = TRUE
)
SELECT
    subject_id,
    stay_id,
    hadm_id,
    age,
    gender,
    admission_type,
    intime,
    prediction_time,
    mortality_label
FROM cohort
-- Restrict the cohort to adult patients eligible at the 24-hour landmark.
WHERE age >= 18
    AND outtime > prediction_time
    AND dischtime > prediction_time
    AND antibiotic_time <= prediction_time
    AND culture_time <= prediction_time
    AND sofa_time <= prediction_time;