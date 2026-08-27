import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

class DistrictSeasonalForecaster:
    def __init__(self, excel_path='DS_Final_1997_2023(1).xlsx'):
        if os.path.exists(excel_path):
            self.df = pd.read_excel(excel_path)
        elif os.path.exists(os.path.join('data', 'raw', 'DS_Final_1997_2023(1).xlsx')):
            self.df = pd.read_excel(os.path.join('data', 'raw', 'DS_Final_1997_2023(1).xlsx'))
        elif os.path.exists('data/processed/rice_yield_processed.csv'):
            self.df = pd.read_csv('data/processed/rice_yield_processed.csv')
        else:
            raise FileNotFoundError("Could not locate historical dataset Excel file.")
        self.df['District'] = self.df['District'].astype(str).str.strip()
        self.df = self.df[self.df['District'].str.title() != 'Chennai'].copy()

        self.districts = sorted(self.df['District'].dropna().unique().tolist())
        self.numerical_cols = [
            'Kharif Temperature', 'Kharif Rainfall', 'Kharif Humidity', 'Kharif Wind_Speed', 'Kharif Soil_Moisture',
            'Rabi Temperature', 'Rabi Rainfall', 'Rabi Humidity', 'Rabi Wind_Speed', 'Rabi Soil_Moisture',
            'Zaid Temperature', 'Zaid Rainfall', 'Zaid Humidity', 'Zaid Wind_Speed', 'Zaid Soil_Moisture',
            'Soil_PH', 'N', 'P', 'K', 'Fertilizer', 'Pesticide', 'Area'
        ]

    def _get_district_history(self, district, feature, train_max_year=2023):
        d_df = self.df[(self.df['District'] == district) & (self.df['Year'] <= train_max_year)].sort_values('Year')
        clean_df = d_df[['Year', feature]].dropna()
        return clean_df

    def forecast_district_feature_moving_avg(self, district, feature, target_year, window=5, train_max_year=2023):
        clean_df = self._get_district_history(district, feature, train_max_year)
        vals = list(clean_df[feature].values)
        if len(vals) == 0:
            return 0.0
        
        last_year = int(clean_df['Year'].max()) if len(clean_df) > 0 else 2023
        horizon = max(1, target_year - last_year)

        history = list(vals)
        for _ in range(horizon):
            recent = history[-window:]
            history.append(float(np.mean(recent)))
        
        pred = history[-1]
        min_b = float(np.min(vals) * 0.8)
        max_b = float(np.max(vals) * 1.2)
        return float(np.clip(pred, min_b, max_b))

    def forecast_district_feature_linear_trend(self, district, feature, target_year, train_max_year=2023):
        clean_df = self._get_district_history(district, feature, train_max_year)
        if len(clean_df) < 3:
            vals = clean_df[feature].values
            return float(vals.mean()) if len(vals) > 0 else 0.0
            
        years = clean_df['Year'].values.astype(float)
        vals = clean_df[feature].values.astype(float)
        
        slope, intercept = np.polyfit(years, vals, 1)
        pred = slope * float(target_year) + intercept
        
        min_b = float(vals.min() * 0.8)
        max_b = float(vals.max() * 1.2)
        return float(np.clip(pred, min_b, max_b))

    def forecast_district_feature_exp_smoothing(self, district, feature, target_year, alpha=0.3, beta=0.1, train_max_year=2023):
        clean_df = self._get_district_history(district, feature, train_max_year)
        vals = clean_df[feature].values
        if len(vals) == 0:
            return 0.0
        if len(vals) < 2:
            return float(vals[0])

        last_year = int(clean_df['Year'].max())
        horizon = max(1, target_year - last_year)

        # Holt's Linear Exponential Smoothing (Level + Trend)
        l = float(vals[0])
        b = float(vals[1] - vals[0])
        for v in vals[1:]:
            v_flt = float(v)
            l_next = alpha * v_flt + (1 - alpha) * (l + b)
            b = beta * (l_next - l) + (1 - beta) * b
            l = l_next

        pred = l + horizon * b
        min_b = float(vals.min() * 0.8)
        max_b = float(vals.max() * 1.2)
        return float(np.clip(pred, min_b, max_b))

    def generate_district_forecast(self, district, target_year=2026, method='Exponential Smoothing'):
        d_df = self.df[self.df['District'] == district]
        if d_df.empty:
            raise ValueError(f"District '{district}' not found in historical dataset.")

        soil_mode = d_df['Soil_Type'].mode().iloc[0] if not d_df['Soil_Type'].mode().empty else d_df['Soil_Type'].iloc[-1]

        base_meta = {
            'District': str(district),
            'Year': int(target_year),
            'Soil_Type': str(soil_mode)
        }

        exp_dict = dict(base_meta)
        ma_dict = dict(base_meta)
        lt_dict = dict(base_meta)

        for col in self.numerical_cols:
            val_exp = self.forecast_district_feature_exp_smoothing(district, col, target_year)
            val_ma = self.forecast_district_feature_moving_avg(district, col, target_year)
            val_lt = self.forecast_district_feature_linear_trend(district, col, target_year)

            exp_dict[col] = round(float(val_exp), 4)
            ma_dict[col] = round(float(val_ma), 4)
            lt_dict[col] = round(float(val_lt), 4)

        all_methods = {
            'Exponential Smoothing': exp_dict,
            '5-Year Moving Average': ma_dict,
            'Linear Trend': lt_dict
        }

        if method == 'Linear Trend':
            selected_dict = lt_dict
        elif method in ['5-Year Moving Average', 'Moving Average']:
            selected_dict = ma_dict
        else:
            selected_dict = exp_dict

        return selected_dict, all_methods

    def run_backtest_validation(self, train_max_year=2018, test_years=[2019, 2020, 2021]):
        test_df = self.df[self.df['Year'].isin(test_years)].copy()
        
        models_to_test = {
            '5-Year Moving Average': self.forecast_district_feature_moving_avg,
            'Linear Trend': self.forecast_district_feature_linear_trend,
            'Exponential Smoothing (alpha=0.3)': self.forecast_district_feature_exp_smoothing
        }
        
        backtest_results = {}
        for m_name, m_func in models_to_test.items():
            y_true_all = []
            y_pred_all = []
            
            for idx, row in test_df.iterrows():
                dist = row['District']
                yr = row['Year']
                
                for col in self.numerical_cols:
                    true_v = row[col]
                    if pd.notnull(true_v):
                        pred_v = m_func(dist, col, yr, train_max_year=train_max_year)
                        y_true_all.append(true_v)
                        y_pred_all.append(pred_v)
                        
            mae = mean_absolute_error(y_true_all, y_pred_all)
            rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
            mape = np.mean(np.abs((np.array(y_true_all) - np.array(y_pred_all)) / (np.array(y_true_all) + 1e-5))) * 100
            
            backtest_results[m_name] = {
                'MAE': round(float(mae), 4),
                'RMSE': round(float(rmse), 4),
                'MAPE_pct': round(float(mape), 2)
            }
            
        os.makedirs('outputs/metrics', exist_ok=True)
        with open('outputs/metrics/forecast_backtest_report.json', 'w') as f:
            json.dump(backtest_results, f, indent=4)
            
        return backtest_results

if __name__ == '__main__':
    forecaster = DistrictSeasonalForecaster()
    fc = forecaster.generate_district_forecast('Thanjavur', 2026, 'Exponential Smoothing')
    print("Sample Forecast 2026 for Thanjavur:")
    print(json.dumps(fc, indent=2))

