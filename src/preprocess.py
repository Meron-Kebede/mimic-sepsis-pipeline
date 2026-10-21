import os
import joblib
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def preprocess_and_split():
    cohort_path = 'data/processed/cohort_cleaned.csv'
    features_path = 'data/processed/features.csv'

    if not os.path.exists(cohort_path):
        raise FileNotFoundError(
            f"Cannot find {cohort_path}. Run extract_cohort.py first."
    )

    if not os.path.exists(features_path):
        raise FileNotFoundError(
            f"Cannot find {features_path}. Run build_features.py first."
    )
    
    print("Loading cohort and feature data...")
    cohort_df = pd.read_csv(cohort_path)
    features_df = pd.read_csv(features_path)

    raw_df = cohort_df.merge(
        features_df,
        on='stay_id',
        how='left',
        validate='one_to_one'
    )

    # Separate predictors from the mortality label, IDs, and timestamps
    features = raw_df.drop(columns=[
        'subject_id', 'stay_id', 'hadm_id', 
        'intime', 'mortality_label', 'prediction_time'
    ])
    mortality_labels = raw_df['mortality_label']

    # Split by patient to prevent leakage across ICU stays
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42
    )

    train_idx, test_idx = next(
        splitter.split(raw_df, groups=raw_df['subject_id'])
    )

    train_features = features.iloc[train_idx]
    train_labels = mortality_labels.iloc[train_idx]

    test_features = features.iloc[test_idx]
    test_labels = mortality_labels.iloc[test_idx]

    # Ensure no patient appears in both sets
    train_patients = set(raw_df.iloc[train_idx]['subject_id'])
    test_patients = set(raw_df.iloc[test_idx]['subject_id'])

    if not train_patients.isdisjoint(test_patients):
        raise ValueError("Patient overlap detected between train and test sets")

    # Preprocess numeric and categorical features separately
    categorical_columns = ['gender', 'admission_type']
    numeric_columns = train_features.columns.difference(categorical_columns).tolist()
    
    
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer([
        ('numeric', numeric_pipeline, numeric_columns),
        ('categorical', categorical_pipeline, categorical_columns)
    ])

    # Fit preprocessing on training set only
    train_features_processed = preprocessor.fit_transform(train_features)
    test_features_processed = preprocessor.transform(test_features)

    # Label the transformed feature columns
    column_names = preprocessor.get_feature_names_out()
    train_features_df = pd.DataFrame(train_features_processed, columns=column_names)
    test_features_df = pd.DataFrame(test_features_processed, columns=column_names)

    # Save split datasets to disk
    os.makedirs('data/processed', exist_ok=True)
    train_features_df.to_csv('data/processed/X_train.csv', index=False)
    test_features_df.to_csv('data/processed/X_test.csv', index=False)
    train_labels.to_csv('data/processed/y_train.csv', index=False)
    test_labels.to_csv('data/processed/y_test.csv', index=False)
    print("Saved train/test datasets to data/processed/")

    # Save fitted preprocessor for model inference
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.joblib')
    print("Saved fitted preprocessor to models/")

    print("\nPREPROCESSING COMPLETE")
    print(f"Training Set: {train_features_df.shape[0]} ICU stays, {len(train_patients)} patients")
    print(f"Testing Set:  {test_features_df.shape[0]} ICU stays, {len(test_patients)} patients")
    print(f"Features:     {train_features_df.shape[1]}")
    print(f"Train Mortality Rate:  {train_labels.mean():.2%}")
    print(f"Test Mortality Rate:   {test_labels.mean():.2%}")
    print(f"Missing Values Remaining: {train_features_df.isna().sum().sum() + test_features_df.isna().sum().sum()}")
    

if __name__ == "__main__":
    preprocess_and_split()
