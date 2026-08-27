import os
import joblib
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer

class AgriculturalDataCleaner(BaseEstimator, TransformerMixin):
    """
    Custom transformer for domain-specific data cleaning:
    1. Standardizes Soil_Type text (e.g., fixing typos like 'coastal alluviam' -> 'coastal alluvium').
    2. Identifies and clips/nullifies invalid physical values (e.g., Kharif Humidity > 100%).
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_clean = X.copy()
        
        # Clean Soil_Type text
        if 'Soil_Type' in X_clean.columns:
            X_clean['Soil_Type'] = X_clean['Soil_Type'].astype(str).str.strip().str.lower()
            X_clean['Soil_Type'] = X_clean['Soil_Type'].replace({
                'coastal alluviam': 'coastal alluvium'
            })
            
        # Clean physical impossible values
        humidity_cols = [c for c in X_clean.columns if 'Humidity' in c]
        for col in humidity_cols:
            # Humidity cannot exceed 100%
            X_clean.loc[X_clean[col] > 100.0, col] = np.nan
            X_clean.loc[X_clean[col] < 0.0, col] = np.nan

        # Temperature logical bounds (10°C to 50°C)
        temp_cols = [c for c in X_clean.columns if 'Temperature' in c]
        for col in temp_cols:
            X_clean.loc[(X_clean[col] > 50.0) | (X_clean[col] < 10.0), col] = np.nan

        # Soil pH bounds (0 to 14)
        if 'Soil_PH' in X_clean.columns:
            X_clean.loc[(X_clean['Soil_PH'] > 14.0) | (X_clean['Soil_PH'] < 0.0), 'Soil_PH'] = np.nan

        return X_clean

def load_and_preprocess_raw_data(raw_file_path):
    print(f"Loading raw data from {raw_file_path}...")
    df = pd.read_excel(raw_file_path, sheet_name=0)
    
    # 0. Exclude Chennai completely (urbanized non-agricultural district)
    df['District'] = df['District'].astype(str).str.strip()
    df = df[df['District'].str.title() != 'Chennai'].copy()
    print(f"Dataset filtered (Chennai excluded). Remaining rows: {len(df)}")
    
    # 1. Clean domain-specific anomalies
    cleaner = AgriculturalDataCleaner()
    df_clean = cleaner.transform(df)
    
    # 2. Filter out rows missing target 'Yield' for training/eval
    df_valid_target = df_clean.dropna(subset=['Yield']).copy()
    print(f"Total valid target rows: {len(df_valid_target)} (dropped {len(df_clean) - len(df_valid_target)} rows missing Yield)")
    
    # 3. Save full cleaned dataset to data/processed/rice_yield_processed.csv
    os.makedirs('data/processed', exist_ok=True)
    df_clean.to_csv('data/processed/rice_yield_processed.csv', index=False)
    
    return df_valid_target

def get_chronological_splits(df):
    """
    Chronological Split:
    Train: 1997 - 2018
    Val:   2019 - 2021
    Test:  2022 - 2023
    """
    train_df = df[df['Year'] <= 2018].copy()
    val_df = df[(df['Year'] >= 2019) & (df['Year'] <= 2021)].copy()
    test_df = df[df['Year'] >= 2022].copy()
    
    print(f"Train split (1997-2018): {len(train_df)} rows")
    print(f"Val split   (2019-2021): {len(val_df)} rows")
    print(f"Test split  (2022-2023): {len(test_df)} rows")
    
    return train_df, val_df, test_df

def create_preprocessing_pipeline(categorical_cols, numerical_cols):
    """
    Creates Sklearn ColumnTransformer with Imputation, OneHotEncoding, and Scaling.
    """
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', num_pipeline, numerical_cols),
        ('cat', cat_pipeline, categorical_cols)
    ])
    
    return preprocessor

def run_preprocessing_pipeline():
    raw_path = 'DS_Final_1997_2023(1).xlsx' if os.path.exists('DS_Final_1997_2023(1).xlsx') else 'data/raw/DS_Final_1997_2023(1).xlsx'
    df = load_and_preprocess_raw_data(raw_path)
    
    # Define features and target
    target_col = 'Yield'
    categorical_cols = ['District', 'Soil_Type']
    numerical_cols = [c for c in df.columns if c not in categorical_cols + [target_col]]
    
    # Chronological Split
    train_df, val_df, test_df = get_chronological_splits(df)
    
    X_train_raw = train_df.drop(columns=[target_col])
    y_train = train_df[target_col].values
    
    X_val_raw = val_df.drop(columns=[target_col])
    y_val = val_df[target_col].values
    
    X_test_raw = test_df.drop(columns=[target_col])
    y_test = test_df[target_col].values
    
    # Fit preprocessor ONLY on Training set
    preprocessor = create_preprocessing_pipeline(categorical_cols, numerical_cols)
    print("Fitting preprocessor on training data ONLY...")
    preprocessor.fit(X_train_raw)
    
    # Transform splits
    X_train_trans = preprocessor.transform(X_train_raw)
    X_val_trans = preprocessor.transform(X_val_raw)
    X_test_trans = preprocessor.transform(X_test_raw)
    
    # Get feature names after OneHotEncoding
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['encoder']
    cat_feature_names = cat_encoder.get_feature_names_out(categorical_cols).tolist()
    feature_names = numerical_cols + cat_feature_names
    
    print(f"Total features after preprocessing: {len(feature_names)}")
    
    # Save preprocessing artifacts
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessing_pipeline.joblib')
    
    metadata = {
        'categorical_cols': categorical_cols,
        'numerical_cols': numerical_cols,
        'feature_names': feature_names,
        'target_col': target_col
    }
    joblib.dump(metadata, 'models/feature_metadata.joblib')
    
    # Save transformed numpy arrays or dataframes for model training
    train_data = {'X': X_train_trans, 'y': y_train, 'raw': X_train_raw}
    val_data = {'X': X_val_trans, 'y': y_val, 'raw': X_val_raw}
    test_data = {'X': X_test_trans, 'y': y_test, 'raw': X_test_raw}
    
    joblib.dump(train_data, 'data/processed/train_data.joblib')
    joblib.dump(val_data, 'data/processed/val_data.joblib')
    joblib.dump(test_data, 'data/processed/test_data.joblib')
    
    print("Preprocessing completed and artifacts saved successfully!")
    return preprocessor, feature_names

if __name__ == '__main__':
    run_preprocessing_pipeline()
