import os
import sys
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure root directory is on Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.inference import RiceYieldInferenceSystem

app = FastAPI(
    title="Tamil Nadu Rice Yield Decision Support System API",
    description="Machine Learning Yield Prediction, SHAP Explainability, Historical Insights & Forecasting API",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Inference System Singleton
inference_system = RiceYieldInferenceSystem(models_dir='models')

class ManualPredictRequest(BaseModel):
    District: str = Field(..., example="Thanjavur")
    Year: int = Field(..., example=2024)
    Soil_Type: str = Field(..., alias="Soil_Type", example="alluvial soil")
    
    # All 15 seasonal features REQUIRED
    Kharif_Temperature: float = Field(..., alias="Kharif Temperature")
    Kharif_Rainfall: float = Field(..., alias="Kharif Rainfall")
    Kharif_Humidity: float = Field(..., alias="Kharif Humidity")
    Kharif_Wind_Speed: float = Field(..., alias="Kharif Wind_Speed")
    Kharif_Soil_Moisture: float = Field(..., alias="Kharif Soil_Moisture")
    
    Rabi_Temperature: float = Field(..., alias="Rabi Temperature")
    Rabi_Rainfall: float = Field(..., alias="Rabi Rainfall")
    Rabi_Humidity: float = Field(..., alias="Rabi Humidity")
    Rabi_Wind_Speed: float = Field(..., alias="Rabi Wind_Speed")
    Rabi_Soil_Moisture: float = Field(..., alias="Rabi Soil_Moisture")
    
    Zaid_Temperature: float = Field(..., alias="Zaid Temperature")
    Zaid_Rainfall: float = Field(..., alias="Zaid Rainfall")
    Zaid_Humidity: float = Field(..., alias="Zaid Humidity")
    Zaid_Wind_Speed: float = Field(..., alias="Zaid Wind_Speed")
    Zaid_Soil_Moisture: float = Field(..., alias="Zaid Soil_Moisture")
    
    # Soil & Inputs REQUIRED
    Soil_PH: float = Field(..., alias="Soil_PH", example=7.2)
    N: float = Field(..., example=300.0)
    P: float = Field(..., example=20.0)
    K: float = Field(..., example=200.0)
    Fertilizer: float = Field(..., example=160.0)
    Pesticide: float = Field(..., example=2.2)
    Area: float = Field(..., example=60000.0)

    class Config:
        populate_by_name = True

class ForecastRequest(BaseModel):
    district: str = Field(..., example="Thanjavur")
    target_year: int = Field(2026, example=2026)
    method: str = Field("Exponential Smoothing", example="Exponential Smoothing")

class CropHealthRequest(BaseModel):
    growth_stage: str = Field("Tillering", example="Tillering")
    leaf_condition: str = Field("Normal", example="Yellowing")
    water_status: str = Field("Adequate", example="Drought Stress")
    pest_obs: str = Field("None", example="Stem Borer")
    disease_obs: str = Field("None", example="Blast")

@app.get("/api/districts")
def get_districts():
    return {
        "districts": sorted(inference_system.districts),
        "soil_types": [
            "alluvial soil", "black soil", "coastal alluvium", "coastal sandy soil",
            "laterite soil", "red soil", "red loamy soil", "red sandy loam soil",
            "red sandy soil", "sandy soil"
        ]
    }

@app.get("/api/historical-ranges")
def get_historical_ranges(district: str):
    if district not in inference_system.insights_engine.district_stats:
        raise HTTPException(status_code=404, detail=f"District '{district}' not found.")
    return {
        "district": district,
        "feature_statistics": inference_system.insights_engine.district_stats[district]
    }

@app.get("/api/district-year-params")
def get_district_year_params(district: str, year: int):
    import pandas as pd
    if district not in inference_system.districts:
        raise HTTPException(status_code=400, detail=f"District '{district}' is invalid or excluded.")
    
    if 1997 <= year <= 2023:
        df_match = inference_system.processed_df[
            (inference_system.processed_df['District'] == district) & 
            (inference_system.processed_df['Year'] == year)
        ]
        if df_match.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for district '{district}' in year {year}.")
        row = df_match.iloc[0].to_dict()
        for k, v in row.items():
            if pd.isna(v):
                row[k] = None
        return {
            "source_type": "Dataset Value",
            "district": district,
            "year": year,
            "params": row
        }
    elif year in [2026, 2027]:
        fc_dict, _ = inference_system.forecaster.generate_district_forecast(district, year, method='Exponential Smoothing')
        return {
            "source_type": "Forecasted Value",
            "district": district,
            "year": year,
            "params": fc_dict
        }
    else:
        raise HTTPException(status_code=400, detail=f"Year {year} is not supported. Supported years are historical (1997-2023) or future (2026, 2027).")

@app.post("/api/predict-yield")
def predict_yield(request: ManualPredictRequest):
    try:
        input_dict = request.model_dump(by_alias=True, exclude_none=True)
        result = inference_system.predict_manual(input_dict, allow_missing=False)
        return json.loads(json.dumps(result, default=str))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forecast")
def forecast_yield(request: ForecastRequest):
    try:
        if request.target_year not in [2026, 2027]:
            raise HTTPException(status_code=400, detail=f"Forecast target year must be 2026 or 2027. Received: {request.target_year}")
        result = inference_system.predict_forecast(
            district=request.district,
            target_year=request.target_year,
            method=request.method
        )
        return json.loads(json.dumps(result, default=str))
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crop-health")
def diagnose_crop_health(request: CropHealthRequest):
    try:
        obs = request.model_dump()
        result = inference_system.crop_health_engine.diagnose_crop_health(obs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model-metrics")
def get_model_metrics():
    try:
        import pandas as pd
        metrics_df = pd.read_csv('outputs/metrics/model_comparison.csv')
        records = json.loads(metrics_df.to_json(orient='records'))
        return {
            "best_model": inference_system.shap_explainer.model.__class__.__name__,
            "metrics": records
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Mount Static Files (both /static and root / for static assets)
from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
