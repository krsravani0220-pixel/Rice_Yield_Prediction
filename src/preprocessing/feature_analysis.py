import os
import json
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def calculate_vif_pure_sklearn(df_features):
    vif_dict = {}
    X = df_features.values
    cols = df_features.columns.tolist()
    
    for i in range(X.shape[1]):
        y_i = X[:, i]
        X_other = np.delete(X, i, axis=1)
        
        lr = LinearRegression()
        lr.fit(X_other, y_i)
        r_squared = lr.score(X_other, y_i)
        
        if r_squared >= 1.0:
            vif = float('inf')
        else:
            vif = 1.0 / (1.0 - r_squared)
            
        vif_dict[cols[i]] = round(float(vif), 2)
        
    return vif_dict

def run_feature_analysis():
    print("Running Phase 3 Feature Analysis...")
    df = pd.read_csv('data/processed/rice_yield_processed.csv')
    df_valid = df.dropna(subset=['Yield']).copy()
    
    num_cols = df_valid.select_dtypes(include=[np.number]).columns.tolist()
    
    # 1. Pearson & Spearman Correlations with Yield
    pearson_corr = df_valid[num_cols].corr()['Yield'].sort_values(ascending=False).to_dict()
    spearman_corr = df_valid[num_cols].corr(method='spearman')['Yield'].sort_values(ascending=False).to_dict()
    
    # 2. VIF Analysis for numerical features (excluding target Yield)
    feature_cols = [c for c in num_cols if c != 'Yield']
    # Drop rows with any NaN in feature_cols for VIF calculation
    vif_df = df_valid[feature_cols].dropna()
    
    vif_data = calculate_vif_pure_sklearn(vif_df)
            
    # 3. Seasonal Feature Correlations Comparison
    seasonal_summary = {
        'Kharif': {c: round(pearson_corr.get(c, 0), 4) for c in num_cols if 'Kharif' in c},
        'Rabi': {c: round(pearson_corr.get(c, 0), 4) for c in num_cols if 'Rabi' in c},
        'Zaid': {c: round(pearson_corr.get(c, 0), 4) for c in num_cols if 'Zaid' in c}
    }
    
    # 4. Year Feature Impact Analysis
    year_corr = round(pearson_corr.get('Year', 0), 4)
    
    report = {
        'pearson_correlation_with_yield': {k: round(v, 4) for k, v in pearson_corr.items()},
        'spearman_correlation_with_yield': {k: round(v, 4) for k, v in spearman_corr.items()},
        'variance_inflation_factor_vif': vif_data,
        'seasonal_correlations': seasonal_summary,
        'year_correlation': year_corr,
        'year_inclusion_justification': (
            "Year has a positive correlation of +0.2219 with Yield, reflecting gradual agricultural technological "
            "advancements, improved crop varieties, and irrigation growth over time (1997-2023). "
            "However, models will be evaluated both with and without Year to ensure models do not over-rely on Year "
            "when predicting unseen future years (e.g. 2026)."
        )
    }
    
    os.makedirs('outputs/metrics', exist_ok=True)
    with open('outputs/metrics/feature_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("Feature analysis completed! Report saved to outputs/metrics/feature_analysis_report.json")
    return report

if __name__ == '__main__':
    run_feature_analysis()
