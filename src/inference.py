import sys
import os
import joblib
import pandas as pd
import numpy as np

# Adjust path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.explainability.shap_explainer import YieldShapExplainer
from src.insights.historical_insights import HistoricalInsightsEngine
from src.forecasting.seasonal_forecaster import DistrictSeasonalForecaster
from src.crop_health.crop_health import CropHealthEngine

class RiceYieldInferenceSystem:
    def __init__(self, models_dir='models'):
        print("Initializing Rice Yield Unified Inference System...")
        self.model = joblib.load(os.path.join(models_dir, 'best_yield_model.joblib'))
        self.preprocessor = joblib.load(os.path.join(models_dir, 'preprocessing_pipeline.joblib'))
        self.metadata = joblib.load(os.path.join(models_dir, 'feature_metadata.joblib'))
        
        self.shap_explainer = YieldShapExplainer(
            model_path=os.path.join(models_dir, 'best_yield_model.joblib'),
            metadata_path=os.path.join(models_dir, 'feature_metadata.joblib')
        )
        self.insights_engine = HistoricalInsightsEngine()
        self.forecaster = DistrictSeasonalForecaster()
        self.crop_health_engine = CropHealthEngine()
        
        self.processed_df = pd.read_csv('data/processed/rice_yield_processed.csv')
        self.districts = self.insights_engine.districts
        
        self.required_features = [
            'District', 'Year', 'Soil_Type',
            'Kharif Temperature', 'Kharif Rainfall', 'Kharif Humidity', 'Kharif Wind_Speed', 'Kharif Soil_Moisture',
            'Rabi Temperature', 'Rabi Rainfall', 'Rabi Humidity', 'Rabi Wind_Speed', 'Rabi Soil_Moisture',
            'Zaid Temperature', 'Zaid Rainfall', 'Zaid Humidity', 'Zaid Wind_Speed', 'Zaid Soil_Moisture',
            'Soil_PH', 'N', 'P', 'K', 'Fertilizer', 'Pesticide', 'Area'
        ]

    def _validate_and_build_dataframe(self, input_dict, allow_missing=False):
        """
        Constructs DataFrame for inference.
        If allow_missing is False (Manual Mode), enforces that ALL required features are present and non-null.
        NO silent median substitution for missing user inputs.
        """
        missing_fields = []
        full_row = {}

        # Explicitly reject Chennai
        dist_input = str(input_dict.get('District', '')).strip()
        if dist_input.title() == 'Chennai':
            raise ValueError("District 'Chennai' is urbanized and excluded from this agricultural rice yield system.")
        if dist_input and dist_input not in self.districts:
            raise ValueError(f"District '{dist_input}' is invalid or excluded.")

        for feat in self.required_features:
            val = input_dict.get(feat, None)
            if val is None or val == "":
                missing_fields.append(feat)
            else:
                if feat == 'District' or feat == 'Soil_Type':
                    full_row[feat] = str(val)
                elif feat == 'Year':
                    full_row[feat] = int(val)
                else:
                    full_row[feat] = float(val)

        if not allow_missing and missing_fields:
            raise ValueError(f"Missing required input features: {', '.join(missing_fields)}. All fields are required.")

        df_row = pd.DataFrame([full_row])
        return df_row, full_row

    def predict_manual(self, input_dict, allow_missing=False):
        df_row, full_row_dict = self._validate_and_build_dataframe(input_dict, allow_missing=allow_missing)
        
        # 1. Preprocess
        X_trans = self.preprocessor.transform(df_row)
        
        # 2. ML Prediction
        pred_yield = float(self.model.predict(X_trans)[0])
        pred_yield = round(max(0.0, pred_yield), 2)
        
        # 3. SHAP Explanation
        shap_res = self.shap_explainer.explain_instance(X_trans, full_row_dict)
        
        # 4. Historical Condition Insights & District Avg Yield
        district = full_row_dict.get('District', 'Thanjavur')
        insights = self.insights_engine.generate_full_insights(district, full_row_dict)
        dist_avg_yield = self.insights_engine.district_avg_yield.get(district, 3.53)
        
        # 5. Suggestions
        suggestions_en = []
        suggestions_ta = []
        for ins in insights:
            if ins['status'] != 'Within Typical Range':
                suggestions_en.append(ins['insight_en'])
                suggestions_ta.append(ins['insight_ta'])
                
        if not suggestions_en:
            suggestions_en.append("All environmental and agricultural inputs are within optimal historical ranges for this district.")
            suggestions_ta.append("அனைத்து சுற்றுச்சூழல் மற்றும் விவசாய உள்ளீடுகளும் இந்த மாவட்டத்திற்கான உகந்த வரம்பிற்குள் உள்ளன.")
            
        return {
            'mode': 'Manual Input Mode',
            'district': district,
            'historical_district_avg_yield': float(dist_avg_yield),
            'year': int(full_row_dict.get('Year', 2024)),
            'predicted_yield': float(pred_yield),
            'unit': 'tonnes/ha',
            'shap_explanation': {
                'base_value': float(shap_res['base_value']),
                'top_positive': shap_res['top_positive_contributors'],
                'top_negative': shap_res['top_negative_contributors']
            },
            'historical_insights': insights,
            'suggestions_en': suggestions_en[:5],
            'suggestions_ta': suggestions_ta[:5]
        }

    def predict_forecast(self, district, target_year=2026, method='Exponential Smoothing'):
        if int(target_year) not in [2026, 2027]:
            raise ValueError(f"Forecast year '{target_year}' is invalid. Only 2026 and 2027 are available for forecasting.")
        fc_dict, all_methods = self.forecaster.generate_district_forecast(district, target_year, method=method)
        # Forecast mode passes full forecasted features dictionary into Yield ML model
        res = self.predict_manual(fc_dict, allow_missing=True)
        res['mode'] = f'Forecast Mode ({method})'
        res['selected_method'] = method
        res['forecasted_features'] = fc_dict
        res['all_methods_forecasts'] = all_methods
        return res
