import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier  
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

def load_processed_data():
    print("Loading processed training and testing datasets...")
    X_train = pd.read_csv('data/processed/X_train.csv')
    X_test = pd.read_csv('data/processed/X_test.csv')
    y_train = pd.read_csv('data/processed/y_train.csv').values.ravel()
    y_test = pd.read_csv('data/processed/y_test.csv').values.ravel()
    
    return X_train, X_test, y_train, y_test

def train_baseline_logistic_regression(X_train, y_train):
    print("Training Baseline Logistic Regression model...")
    
    # Class weight='balanced' adjusts for class imbalance (14.29% mortality rate)
    model = LogisticRegression(
        random_state=42, 
        max_iter=1000, 
        class_weight='balanced'
    )
    
    # Fit strictly on training data
    model.fit(X_train, y_train)
    return model

def train_random_forest(X_train, y_train):
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100, 
        random_state=42, 
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    return model

def train_xgboost(X_train, y_train):
    print("Training XGBoost Classifier...")
    
    # Calculate scale_pos_weight for class imbalance (~24 / 4 = 6)
    ratio = (len(y_train) - sum(y_train)) / sum(y_train)
    
    model = XGBClassifier(
        n_estimators=100, 
        learning_rate=0.05, 
        max_depth=3, 
        scale_pos_weight=ratio, 
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test, model_name="Model"):
    # Binary predictions (survived = 0, died = 1)
    y_pred = model.predict(X_test)
    
    # Predicted probabilities for the positive class (mortality = 1)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    auroc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"\n{model_name.upper()} EVALUATION")
    print(f"AUROC Score: {auroc:.4f}")
    print("\nConfusion Matrix:")
    print(f"  True Negatives (Survived):  {cm[0][0]}  |  False Positives:  {cm[0][1]}")
    print(f"  False Negatives (Missed):   {cm[1][0]}  |  True Positives (Died): {cm[1][1]}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Survived (0)', 'Died (1)']))

def main():
    # 1. Load preprocessed data
    X_train, X_test, y_train, y_test = load_processed_data()
    
    # 2. Train models
    lr_model = train_baseline_logistic_regression(X_train, y_train)
    rf_model = train_random_forest(X_train, y_train)
    xgb_model = train_xgboost(X_train, y_train)
    
    # 3. Evaluate on unseen test data
    evaluate_model(lr_model, X_test, y_test, "1. Logistic Regression Baseline")
    evaluate_model(rf_model, X_test, y_test, "2. Random Forest")
    evaluate_model(xgb_model, X_test, y_test, "3. XGBoost")  

if __name__ == "__main__":
    main()