import os
import json
import pandas as pd
import numpy as np

def run_dataset_audit(file_path):
    print(f"Loading raw dataset from {file_path}...")
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    
    df = pd.read_excel(file_path, sheet_name=0)
    
    audit_results = {}
    audit_results['sheet_names'] = sheet_names
    audit_results['num_rows'] = len(df)
    audit_results['num_columns'] = len(df.columns)
    audit_results['exact_column_names'] = df.columns.tolist()
    audit_results['data_types'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    # Missing values
    missing = df.isnull().sum()
    audit_results['missing_values_per_column'] = missing.to_dict()
    audit_results['missing_percentage_per_column'] = (missing / len(df) * 100).round(2).to_dict()
    
    # Duplicate rows
    audit_results['duplicate_rows'] = int(df.duplicated().sum())
    
    # Districts
    if 'District' in df.columns:
        districts = df['District'].dropna().unique().tolist()
        audit_results['unique_districts'] = districts
        audit_results['num_unique_districts'] = len(districts)
        audit_results['records_per_district'] = df['District'].value_counts().to_dict()
    
    # Years
    if 'Year' in df.columns:
        years = df['Year'].dropna().astype(int).unique().tolist()
        years.sort()
        audit_results['year_range'] = {'min': min(years), 'max': max(years)}
        audit_results['num_years'] = len(years)
        audit_results['records_per_year'] = df['Year'].value_counts().to_dict()
    
    # Categorical Columns & Unique Values
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    audit_results['categorical_columns'] = cat_cols
    audit_results['unique_values_categorical'] = {col: df[col].dropna().unique().tolist() for col in cat_cols}
    
    # Numerical Statistics
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    desc = df[num_cols].describe().T
    audit_results['numerical_descriptive_stats'] = desc.to_dict(orient='index')
    
    # Target (Yield) Statistics
    if 'Yield' in df.columns:
        y_stats = df['Yield'].describe()
        audit_results['yield_statistics'] = {
            'count': float(y_stats['count']),
            'mean': float(y_stats['mean']),
            'std': float(y_stats['std']),
            'min': float(y_stats['min']),
            '25%': float(y_stats['25%']),
            '50%': float(y_stats['50%']),
            '75%': float(y_stats['75%']),
            'max': float(y_stats['max']),
            'null_count': int(df['Yield'].isnull().sum())
        }
    
    # Possible invalid/impossible values & potential outliers (IQR method)
    outliers = {}
    impossible_vals = {}
    for col in num_cols:
        col_data = df[col].dropna()
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        num_outliers = int(((col_data < lower_bound) | (col_data > upper_bound)).sum())
        outliers[col] = {
            'iqr_lower_bound': float(lower_bound),
            'iqr_upper_bound': float(upper_bound),
            'count_outliers': num_outliers
        }
        
        # Check negative values for non-negative physical quantities
        if col not in ['Year']:
            neg_count = int((col_data < 0).sum())
            if neg_count > 0:
                impossible_vals[col] = f"{neg_count} negative values found."
                
    audit_results['potential_outliers_iqr'] = outliers
    audit_results['invalid_negative_values'] = impossible_vals
    
    # Correlation with Yield
    if 'Yield' in df.columns:
        corr_yield = df[num_cols].corr()['Yield'].sort_values(ascending=False).to_dict()
        audit_results['correlation_with_yield'] = corr_yield
        
    # Save results
    os.makedirs('outputs/metrics', exist_ok=True)
    with open('outputs/metrics/dataset_audit_report.json', 'w') as f:
        json.dump(audit_results, f, indent=4)
        
    # Generate Markdown Report
    md_content = f"# Phase 1: Dataset Audit Report\n\n"
    md_content += f"- **Dataset Location:** `{file_path}`\n"
    md_content += f"- **Sheets Found:** {sheet_names}\n"
    md_content += f"- **Shape:** {len(df)} rows × {len(df.columns)} columns\n"
    md_content += f"- **Duplicate Rows:** {audit_results['duplicate_rows']}\n"
    md_content += f"- **Year Range:** {audit_results['year_range']['min']} – {audit_results['year_range']['max']} ({audit_results['num_years']} years)\n"
    md_content += f"- **Districts ({len(districts)}):** {', '.join(districts)}\n\n"
    
    md_content += "## Missing Values Analysis\n\n"
    md_content += "| Column Name | Data Type | Null Count | Null % |\n"
    md_content += "|---|---|---|---|\n"
    for col in df.columns:
        dt = audit_results['data_types'][col]
        null_c = audit_results['missing_values_per_column'][col]
        null_p = audit_results['missing_percentage_per_column'][col]
        md_content += f"| `{col}` | {dt} | {null_c} | {null_p}% |\n"
        
    md_content += "\n## Yield Statistics (Target Variable)\n\n"
    for k, v in audit_results['yield_statistics'].items():
        md_content += f"- **{k}:** {v}\n"
        
    md_content += "\n## Key Data Quality Observations\n\n"
    md_content += f"1. Target `Yield` has {audit_results['yield_statistics']['null_count']} missing values that require target-filtering during training.\n"
    md_content += f"2. Seasonal features (Kharif, Rabi, Zaid) contain missing values in earlier years (e.g. 1997-2000).\n"
    md_content += f"3. All features keep separate Kharif, Rabi, and Zaid seasonal averages without re-aggregation.\n"
    
    with open('outputs/metrics/dataset_audit_report.md', 'w') as f:
        f.write(md_content)
        
    print("Audit completed successfully! Reports saved to outputs/metrics/")
    return audit_results

if __name__ == '__main__':
    run_dataset_audit('data/raw/DS_Final_1997_2023(1).xlsx')
