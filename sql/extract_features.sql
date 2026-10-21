-- Calculate min, max, and average vital signs during the first 24 hours of each ICU stay.

SELECT
    cohort.stay_id,

    MIN(v.heart_rate) AS heart_rate_min,
    AVG(v.heart_rate) AS heart_rate_mean,
    MAX(v.heart_rate) AS heart_rate_max,

    MIN(COALESCE(v.sbp, v.sbp_ni)) AS sbp_min,
    AVG(COALESCE(v.sbp, v.sbp_ni)) AS sbp_mean,
    MAX(COALESCE(v.sbp, v.sbp_ni)) AS sbp_max,
    MAX(IF(v.sbp IS NOT NULL, 1, 0)) AS invasive_sbp_recorded,


    MIN(COALESCE(v.mbp, v.mbp_ni)) AS map_min,
    AVG(COALESCE(v.mbp, v.mbp_ni)) AS map_mean,
    MAX(COALESCE(v.mbp, v.mbp_ni)) AS map_max,
    MAX(IF(v.mbp IS NOT NULL, 1, 0)) AS invasive_map_recorded,

    MIN(v.resp_rate) AS resp_rate_min,
    AVG(v.resp_rate) AS resp_rate_mean,
    MAX(v.resp_rate) AS resp_rate_max,

    MIN(v.spo2) AS spo2_min,
    AVG(v.spo2) AS spo2_mean,
    MAX(v.spo2) AS spo2_max

FROM `mimic-sepsis-pipeline.sepsis_pipeline.cohort_cleaned` cohort
LEFT JOIN `physionet-data.mimiciv_3_1_derived.vitalsign` v
    ON cohort.stay_id = v.stay_id
    AND v.charttime >= cohort.intime
    AND v.charttime < cohort.prediction_time

GROUP BY cohort.stay_id;