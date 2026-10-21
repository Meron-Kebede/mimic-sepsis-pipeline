# ICU Sepsis Mortality Prediction

I am building a machine learning pipeline to predict in-hospital mortality for adults with sepsis using information recorded during their first 24 hours in the ICU. The project uses MIMIC-IV v3.1, with SQL and Google BigQuery for data extraction and Python for preprocessing, modeling, and evaluation.

## What I've built

- **Cohort:** Identified 22,829 ICU stays (from 19,002 adult patients) meeting the project's Sepsis-3 cohort criteria. The in-hospital mortality rate is 14.3%.
- **Features:** Extracted first-day vital signs and calculated summary statistics for heart rate, blood pressure, respiratory rate, and oxygen saturation, along with monitoring indicators.
- **Preprocessing:** Split the data by patient so that ICU stays from the same person cannot appear in both training and test sets. Fitted missing-value imputation, scaling, and categorical encoding on training data only.
- **Models:** Trained logistic regression, random forest, and XGBoost classifiers, with adjustments for class imbalance.

## Prediction window

Each ICU stay has a prediction cutoff **24 hours after ICU admission** (`intime + 24 hours`). The cohort only includes stays for patients who are still hospitalized at that point. The model uses vital-sign measurements recorded **at or after ICU admission and strictly before the cutoff**; measurements taken at the cutoff or later are excluded.

The goal is to predict whether the patient will die during their admission using only the selected predictors available by that 24-hour point. Keeping this window fixed helps prevent future measurements from leaking into the model. The Sepsis-3 cohort definition itself is retrospective, so this should not be interpreted as a prospectively validated sepsis-screening system.

## Initial results

Results from a held-out test set of 4,625 ICU stays:

| Model | AUROC | Average precision | Mortality recall |
| --- | ---: | ---: | ---: |
| Logistic regression | 0.7097 | 0.3088 | 0.66 |
| Random forest | 0.7200 | 0.3107 | 0.18 |
| XGBoost | **0.7288** | **0.3377** | **0.67** |

XGBoost had the highest AUROC and average precision in this initial comparison. These are preliminary results, not a clinically validated model. Model selection, calibration, and further validation are still in progress.

## Tools

Python, SQL, Google BigQuery, pandas, scikit-learn, XGBoost, and joblib.

## Running the pipeline

MIMIC-IV v3.1 access through PhysioNet and the corresponding BigQuery datasets is required. Once access and Python dependencies are configured, run the scripts from the repository root:

```bash
python src/extract_cohort.py
python src/build_features.py
python src/preprocess.py
python src/train.py
```

The scripts extract the cohort, build a set of predictor features, create patient-separated training and test sets, and train and evaluate the models. The trained models and fitted preprocessor are saved locally in `models/`.

## Project structure

```text
mimic-sepsis-pipeline/
├── data/
│   ├── raw/                  # Optional local data (git-ignored)
│   └── processed/            # Extracted cohort, features and train/test CSVs
├── models/                   # Saved preprocessor and trained models
├── notebooks/                # Reserved for exploratory analysis
├── sql/
│   ├── extract_cohort.sql
│   └── extract_features.sql
├── src/
│   ├── extract_cohort.py
│   ├── build_features.py
│   ├── preprocess.py
│   └── train.py
├── .gitignore
├── requirements.txt
└── README.md

```

The data CSVs and `.joblib` files are local outputs, not files shared in the public repository. Empty directories are retained with `.gitkeep` files.

## Data access

MIMIC-IV is a credentialed-access clinical dataset. Patient-level data, processed datasets, and saved model artifacts are not included in this public repository. See [PhysioNet's MIMIC-IV page](https://physionet.org/content/mimiciv/) for access requirements.

**This is an educational research project, not a model intended for clinical use.**

