# ICU Sepsis Mortality Prediction

A clinical data pipeline to predict in-hospital mortality among adult ICU patients diagnosed with sepsis using MIMIC-IV clinical data.

I am using Python, DuckDB, and SQL to identify the sepsis cohort, extract vital signs and lab results from their first 24 hours in the ICU, and train predictive machine learning models.

## Status

**In Progress:** Repository structure is initialized and MIMIC-IV demo dataset is loaded. Currently exploring clinical tables and validating cohort extraction logic.

## Tools

- **Language & Logic:** Python, SQL
- **Database Engine:** DuckDB
- **ML & Analytics:** scikit-learn, pandas

## Data

MIMIC-IV data is stored locally and is excluded from Git per PhysioNet data use agreements.

*Note: This repository is for research and educational purposes only and is not intended for clinical use.*

## Project Structure

```text
mimic-sepsis-pipeline/
|-- data/           # Local raw MIMIC-IV files (git-ignored)
|-- notebooks/      # Exploratory data analysis
|-- src/            # Core pipeline, cohort extraction, and ML scripts
|-- .gitignore
`-- README.md

