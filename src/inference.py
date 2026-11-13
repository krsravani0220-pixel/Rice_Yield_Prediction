import sys
import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List

# Adjust path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.explainability.shap_explainer import YieldShapExplainer
from src.insights.historical_insights import HistoricalInsightsEngine
from src.forecasting.seasonal_forecaster import DistrictSeasonalForecaster
from src.crop_health.crop_health import CropHealthEngine
from src.weather.openmeteo_client import OpenMeteoWeatherClient
from src.satellite.copernicus_client import CopernicusSatelliteClient
from src.satellite.district_registry import get_district_profile, get_all_districts
from src.storage.db_adapter import DatabaseAdapter

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
        self.weather_client = OpenMeteoWeatherClient()
        self.copernicus_client = CopernicusSatelliteClient()
        self.db_adapter = DatabaseAdapter()
        
        self.processed_df = pd.read_csv('data/processed/rice_yield_processed.csv')
        self.districts = self.insights_engine.districts
        self.all_30_districts = get_all_districts()
        
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

    def predict_forecast(self, district, target_year=None, method='Exponential Smoothing'):
        if target_year is None:
            target_year = datetime.now().year
        target_year = int(target_year)
        if target_year < 1997:
            raise ValueError(f"Forecast year '{target_year}' is invalid. Reference timeline starts from 1997.")
        fc_dict, all_methods = self.forecaster.generate_district_forecast(district, target_year, method=method)
        # Forecast mode passes full forecasted features dictionary into Yield ML model
        res = self.predict_manual(fc_dict, allow_missing=True)
        res['mode'] = f'Forecast Mode ({method})'
        res['selected_method'] = method
        res['target_year'] = target_year
        res['is_historical'] = False
        res['forecasted_features'] = fc_dict
        res['all_methods_forecasts'] = all_methods
        return res

    def predict_live(self, district: str, reference_date: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Predicts rice yield using live-fetched Sentinel-2 satellite observations from
        Copernicus Data Space Ecosystem and ECMWF ERA5-Land reanalysis from Open-Meteo.
        Does NOT rely on historical Excel record substitution.
        """
        clean_dist = district.strip()
        prof = get_district_profile(clean_dist)
        if not prof:
            raise ValueError(f"District '{district}' is not recognized in Tamil Nadu registry.")

        dist_name = prof["district"]

        # Chennai special handling (urban metropolitan district)
        if dist_name == "Chennai":
            return {
                "status": "insufficient_data",
                "district": "Chennai",
                "is_agricultural": False,
                "predicted_yield": None,
                "unit": "tonnes/ha",
                "message": "Chennai is a metropolitan urban district with negligible commercial rice cultivation (21 of 27 years missing in agricultural census).",
                "warning": "Yield prediction is not applicable for non-agricultural urban center Chennai.",
                "data_quality_warnings": [
                    "Urban non-agricultural tract; census records virtually zero commercial paddy acreage.",
                    "Model prediction intentionally withheld to prevent misleading output."
                ]
            }

        ref_year = int(reference_date[:4]) if reference_date else datetime.now().year

        # 1. Fetch live Open-Meteo weather
        weather_res = self.weather_client.fetch_district_weather_12m(
            dist_name, reference_date=reference_date, force_refresh=force_refresh
        )

        # 2. Fetch live Copernicus Sentinel-2 observations
        sat_res = self.copernicus_client.fetch_district_observations_12m(
            dist_name, reference_date=reference_date, force_refresh=force_refresh
        )

        # 3. Construct input dictionary matching trained Extra Trees model schema
        model_input = {
            "District": dist_name,
            "Year": ref_year,
            "Soil_Type": prof["soil_type"],
            "Soil_PH": prof["soil_ph"],
            "N": prof["n"],
            "P": prof["p"],
            "K": prof["k"],
            "Fertilizer": prof["fertilizer"],
            "Pesticide": prof["pesticide"],
            "Area": prof["area"],
            **weather_res["model_input_features"]
        }

        # 4. Validate and build DataFrame
        df_row, full_row_dict = self._validate_and_build_dataframe(model_input, allow_missing=False)

        # 5. Preprocess and predict baseline yield
        X_trans = self.preprocessor.transform(df_row)
        pred_yield = float(self.model.predict(X_trans)[0])
        pred_yield = round(max(0.0, pred_yield), 2)

        # 6. SHAP explanation
        shap_res = self.shap_explainer.explain_instance(X_trans, full_row_dict)

        # 7. Historical Condition Insights
        insights = self.insights_engine.generate_full_insights(dist_name, full_row_dict)
        dist_avg_yield = self.insights_engine.district_avg_yield.get(dist_name, 3.53)

        suggestions_en = []
        suggestions_ta = []
        for ins in insights:
            if ins['status'] != 'Within Typical Range':
                suggestions_en.append(ins['insight_en'])
                suggestions_ta.append(ins['insight_ta'])

        if not suggestions_en:
            suggestions_en.append("All seasonal environmental inputs are within typical historical bounds for this district.")
            suggestions_ta.append("அனைத்து பருவகால சுற்றுச்சூழல் உள்ளீடுகளும் இந்த மாவட்டத்திற்கான பொதுவான வரலாற்று வரம்புகளுக்குள் உள்ளன.")

        # 8. Data quality warnings
        warnings = [
            f"Weather data represents {weather_res['data_source']} rather than direct localized rain-gauge station measurements.",
            f"Seasonal rainfall parameters reflect mean monthly precipitation rates (Kharif/4, Rabi/5, Zaid/3) aligning with model training bounds.",
            "Satellite canopy vigor indicators (NDVI/NDRE) indicate photosynthetic vegetative vigor and are not directly multiplied by yield.",
            "This result is an algorithmic predictive estimate, not a certified post-harvest crop cutting survey."
        ]
        if sat_res.get("warning"):
            warnings.append(sat_res["warning"])
        if weather_res.get("warning"):
            warnings.append(weather_res["warning"])

        sat_dates = [obs["date"] for obs in sat_res.get("observations_summary", [])[:15]]

        # 9. Record prediction provenance in NeonDB / structured log
        telemetry_record = {
            "district": dist_name,
            "year": ref_year,
            "reference_date": weather_res["observation_window"]["requested_reference_date"],
            "weather_period_start": weather_res["observation_window"]["start_date"],
            "weather_period_end": weather_res["observation_window"]["end_date"],
            "weather_source": weather_res["data_source"],
            "satellite_observation_dates": sat_dates,
            "calculated_features": model_input,
            "baseline_yield": pred_yield,
            "satellite_yield": None,
            "ndvi_mean": sat_res.get("vegetation_indices", {}).get("ndvi_mean"),
            "ndre_mean": sat_res.get("vegetation_indices", {}).get("ndre_mean"),
            "model_version": "ExtraTreesRegressor_v1.0",
            "status": "success"
        }
        self.db_adapter.record_prediction(telemetry_record)

        return {
            "mode": "Live Satellite & Weather Mode",
            "status": "success",
            "district": dist_name,
            "reference_year": ref_year,
            "historical_district_avg_yield": float(dist_avg_yield),
            "predicted_yield": pred_yield,
            "unit": "tonnes/ha",
            "coordinates": prof["bbox"],
            "agro_climatic_zone": prof["agro_climatic_zone"],
            "soil_profile": {
                "soil_type": prof["soil_type"],
                "soil_ph": prof["soil_ph"],
                "n_kg_ha": prof["n"],
                "p_kg_ha": prof["p"],
                "k_kg_ha": prof["k"],
                "fertilizer_kg_ha": prof["fertilizer"],
                "pesticide_kg_ha": prof["pesticide"],
                "cultivated_area_ha": prof["area"],
                "source": "Tamil Nadu Agricultural Baseline Census"
            },
            "weather_data": {
                "source": weather_res["data_source"],
                "observation_window": weather_res["observation_window"],
                "annual_summary": weather_res["annual_summary"],
                "seasonal_breakdown": weather_res["seasonal_breakdown"],
                "is_cached": weather_res.get("is_cached", False)
            },
            "satellite_data": {
                "source": sat_res["data_source"],
                "observation_window": sat_res["observation_window"],
                "total_observations": sat_res["total_usable_observations"],
                "cloud_filtering": sat_res["cloud_filtering"],
                "dominant_season": sat_res["season_identification"]["dominant_rice_season"],
                "vegetation_indices": sat_res["vegetation_indices"],
                "observation_dates_sample": sat_dates,
                "is_cached": sat_res.get("is_cached", False)
            },
            "shap_explanation": {
                "base_value": float(shap_res["base_value"]),
                "top_positive": shap_res["top_positive_contributors"],
                "top_negative": shap_res["top_negative_contributors"]
            },
            "historical_insights": insights,
            "suggestions_en": suggestions_en[:5],
            "suggestions_ta": suggestions_ta[:5],
            "data_quality_warnings": warnings,
            "model_metrics": {
                "model_name": "Tuned Extra Trees Regressor",
                "test_mae_tonnes_ha": 0.2666,
                "test_rmse_tonnes_ha": 0.3662,
                "test_r2_score": 0.6626,
                "evaluation_split": "Unseen Test Set (2022–2023)"
            },
            "scientific_disclaimer": "This is an algorithmic model prediction based on ECMWF ERA5-Land reanalysis weather and Copernicus Sentinel-2 Level-2A satellite data, not an official post-harvest crop cutting survey."
        }
