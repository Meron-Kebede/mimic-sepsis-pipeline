import duckdb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from build_features import main as build_24hr_features

def preprocess_and_split():
    print("Connecting to DuckDB engine and extracting 24hr cohort vitals...")
    raw_df = build_24hr_features()

    # Drop target answer and identifier columns
    features = raw_df.drop(columns=['subject_id', 'stay_id', 'hadm_id', 'gender', 'intime', 'mortality_label'])
    mortality_labels = raw_df['mortality_label']
    column_names = features.columns.tolist()

    # Stratified 80/20 train-test split
    train_features, test_features, train_labels, test_labels = train_test_split(
        features, 
        mortality_labels, 
        test_size=0.20, 
        random_state=42, 
        stratify=mortality_labels
    )

    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()

    # Fit & transform training set only (prevent data leakage)
    train_features_imputed = imputer.fit_transform(train_features)
    train_features_scaled = scaler.fit_transform(train_features_imputed)

    # Transform test set using saved training stats
    test_features_imputed = imputer.transform(test_features)
    test_features_scaled = scaler.transform(test_features_imputed)

    # Convert numpy arrays back to labeled DataFrames
    train_features_df = pd.DataFrame(train_features_scaled, columns=column_names)
    test_features_df = pd.DataFrame(test_features_scaled, columns=column_names)

    # Save datasets to disk
    train_features_df.to_csv('data/processed/X_train.csv', index=False)
    test_features_df.to_csv('data/processed/X_test.csv', index=False)
    train_labels.to_csv('data/processed/y_train.csv', index=False)
    test_labels.to_csv('data/processed/y_test.csv', index=False)
    print("Files successfully saved to 'data/processed/' folder!")

    print("PREPROCESSING COMPLETE")
    print(f"Training Set  (X_train): {train_features_df.shape[0]} patients, {train_features_df.shape[1]} features")
    print(f"Testing Set   (X_test):  {test_features_df.shape[0]} patients, {test_features_df.shape[1]} features")
    print(f"Train Mortality Rate:    {train_labels.mean():.2%}")
    print(f"Test Mortality Rate:     {test_labels.mean():.2%}")
    print(f"Missing Values Remaining: {train_features_df.isna().sum().sum()}")
    

if __name__ == "__main__":
    preprocess_and_split()
