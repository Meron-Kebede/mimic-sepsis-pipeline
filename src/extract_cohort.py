import pandas as pd
import os

def extract_cohort():
    input_path = 'data/processed/cohort_raw.csv'
    output_path = 'data/processed/cohort_cleaned.csv'

    if not os.path.exists(input_path):
        print(f"Cannot find {input_path}.")
        return

    print("Loading raw cohort data from local storage...")
    df = pd.read_csv(input_path)
    initial_count = len(df)

    # Filter for adult patients (Age >= 18)
    df = df[df['age'] >= 18].copy()
    adult_count = len(df)

    # Save cleaned cohort
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Extracted cohort saved to {output_path}")

    print("\nCOHORT SUMMARY")
    print(f"Records Excluded: {initial_count - adult_count}")
    print(f"Total Adult ICU Cohort: {len(df)}")
    print(f"In-Hospital Mortality Rate: {df['mortality_label'].mean():.2%}")
    print("\nFirst 5 Patients in Cohort:")
    print(df.head())


if __name__ == "__main__":
    extract_cohort()