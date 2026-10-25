"""
Open-Meteo Historical Weather API Client
=======================================
Retrieves real reanalysis weather data (ECMWF ERA5-Land) for any Tamil Nadu
district across a one-year observation period. Computes seasonal aggregates
(Kharif: Jun-Sep, Rabi: Oct-Feb, Zaid: Mar-May) and cumulative rainfall totals.
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from src.satellite.district_registry import get_district_profile

CACHE_DIR = os.path.abspath("data/cache/weather")
os.makedirs(CACHE_DIR, exist_ok=True)


class OpenMeteoWeatherClient:
    """
    Client for Open-Meteo Historical Weather API.
    Provides free, keyless access to ERA5-Land reanalysis meteorological records.
    """
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, cache_ttl_hours: int = 24):
        self.cache_ttl_seconds = cache_ttl_hours * 3600

    def _get_cache_path(self, district: str, ref_date_str: str) -> str:
        clean_name = district.strip().lower().replace(" ", "_")
        return os.path.join(CACHE_DIR, f"weather_{clean_name}_{ref_date_str}.json")

    def fetch_district_weather_12m(
        self,
        district: str,
        reference_date: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves 1-year daily weather observations for the specified district
        and calculates seasonal averages and cumulative totals.
        """
        prof = get_district_profile(district)
        if not prof:
            raise ValueError(f"District '{district}' is not recognized in Tamil Nadu registry.")

        lat = prof["lat"]
        lon = prof["lon"]

        # Determine reference date (defaults to current local date)
        if reference_date:
            try:
                ref_dt = datetime.strptime(reference_date[:10], "%Y-%m-%d")
            except Exception:
                ref_dt = datetime.now()
        else:
            ref_dt = datetime.now()

        ref_date_str = ref_dt.strftime("%Y-%m-%d")
        cache_path = self._get_cache_path(district, ref_date_str)

        # Check local cache
        if not force_refresh and os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    cached_data = json.load(f)
                cached_time = cached_data.get("cached_at_timestamp", 0)
                if (time.time() - cached_time) < self.cache_ttl_seconds:
                    cached_data["is_cached"] = True
                    return cached_data
            except Exception:
                pass

        # Calculate exact 1-year lookback
        start_dt = ref_dt - timedelta(days=365)
        # ERA5-Land reanalysis has ~3-5 day lag; cap at 4 days ago for archive, or use today
        archive_end_dt = min(ref_dt, datetime.now() - timedelta(days=4))
        
        start_date_str = start_dt.strftime("%Y-%m-%d")
        end_date_str = archive_end_dt.strftime("%Y-%m-%d")

        daily_vars = [
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "relative_humidity_2m_mean",
            "wind_speed_10m_max",
            "shortwave_radiation_sum",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_7cm_mean"
        ]

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "daily": daily_vars,
            "timezone": "Asia/Kolkata"
        }

        raw_daily = None
        error_msg = None

        for attempt in range(3):
            try:
                resp = requests.get(self.ARCHIVE_URL, params=params, timeout=20)
                if resp.status_code == 200:
                    raw_daily = resp.json().get("daily", {})
                    break
                else:
                    error_msg = f"HTTP {resp.status_code}: {resp.text[:150]}"
            except Exception as e:
                error_msg = str(e)
            time.sleep(1.5)

        if not raw_daily or "time" not in raw_daily:
            # Fallback to local cache if exists
            if os.path.exists(cache_path):
                with open(cache_path, "r") as f:
                    cached_data = json.load(f)
                cached_data["is_cached"] = True
                cached_data["warning"] = f"Live API query failed ({error_msg}); serving cached observation."
                return cached_data
            raise RuntimeError(f"Failed to retrieve weather data from Open-Meteo for {district}: {error_msg}")

        # Process and calculate seasonal aggregates
        dates = raw_daily.get("time", [])
        temp_mean = raw_daily.get("temperature_2m_mean", [])
        temp_max = raw_daily.get("temperature_2m_max", [])
        temp_min = raw_daily.get("temperature_2m_min", [])
        precip = raw_daily.get("precipitation_sum", [])
        humidity = raw_daily.get("relative_humidity_2m_mean", [])
        wind = raw_daily.get("wind_speed_10m_max", [])
        radiation = raw_daily.get("shortwave_radiation_sum", [])
        et0 = raw_daily.get("et0_fao_evapotranspiration", [])
        soil_m = raw_daily.get("soil_moisture_0_to_7cm_mean", [])

        # Categorize into seasons:
        # Kharif: Jun, Jul, Aug, Sep (months 6, 7, 8, 9) -> 4 months
        # Rabi: Oct, Nov, Dec, Jan, Feb (months 10, 11, 12, 1, 2) -> 5 months
        # Zaid: Mar, Apr, May (months 3, 4, 5) -> 3 months
        seasons_data = {
            "kharif": {"temp": [], "precip": [], "humidity": [], "wind": [], "soil_m": [], "days": 0},
            "rabi": {"temp": [], "precip": [], "humidity": [], "wind": [], "soil_m": [], "days": 0},
            "zaid": {"temp": [], "precip": [], "humidity": [], "wind": [], "soil_m": [], "days": 0}
        }

        all_valid_temp = []
        all_valid_precip = []
        all_valid_humidity = []
        all_valid_wind = []
        all_valid_soil_m = []

        for i, d_str in enumerate(dates):
            try:
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                m = dt.month
            except Exception:
                continue

            t = temp_mean[i] if i < len(temp_mean) and temp_mean[i] is not None else None
            p = precip[i] if i < len(precip) and precip[i] is not None else 0.0
            h = humidity[i] if i < len(humidity) and humidity[i] is not None else None
            w = wind[i] if i < len(wind) and wind[i] is not None else None
            sm = soil_m[i] if i < len(soil_m) and soil_m[i] is not None else None

            if t is not None: all_valid_temp.append(t)
            all_valid_precip.append(p)
            if h is not None: all_valid_humidity.append(h)
            if w is not None: all_valid_wind.append(w)
            if sm is not None: all_valid_soil_m.append(sm)

            if 6 <= m <= 9:
                s_key = "kharif"
            elif m in [10, 11, 12, 1, 2]:
                s_key = "rabi"
            else:
                s_key = "zaid"

            seasons_data[s_key]["days"] += 1
            if t is not None: seasons_data[s_key]["temp"].append(t)
            seasons_data[s_key]["precip"].append(p)
            if h is not None: seasons_data[s_key]["humidity"].append(h)
            if w is not None: seasons_data[s_key]["wind"].append(w)
            if sm is not None: seasons_data[s_key]["soil_m"].append(sm)

        def _safe_mean(arr, default_val=0.0):
            return round(float(sum(arr) / len(arr)), 2) if arr else default_val

        # Seasonal Feature Construction for ML Pipeline:
        # Temperature, Humidity, Wind Speed, Soil Moisture -> Arithmetic mean of months
        # Rainfall in dataset -> Monthly average rate = Total Season Rainfall / Season Month Count
        kharif_temp = _safe_mean(seasons_data["kharif"]["temp"], 29.5)
        kharif_tot_rain = round(float(sum(seasons_data["kharif"]["precip"])), 2)
        kharif_rain_monthly = round(kharif_tot_rain / 4.0, 2)
        kharif_humidity = _safe_mean(seasons_data["kharif"]["humidity"], 68.0)
        kharif_wind = _safe_mean(seasons_data["kharif"]["wind"], 3.5)
        kharif_soil_m = _safe_mean(seasons_data["kharif"]["soil_m"], 0.45)

        rabi_temp = _safe_mean(seasons_data["rabi"]["temp"], 25.5)
        rabi_tot_rain = round(float(sum(seasons_data["rabi"]["precip"])), 2)
        rabi_rain_monthly = round(rabi_tot_rain / 5.0, 2)
        rabi_humidity = _safe_mean(seasons_data["rabi"]["humidity"], 78.0)
        rabi_wind = _safe_mean(seasons_data["rabi"]["wind"], 2.8)
        rabi_soil_m = _safe_mean(seasons_data["rabi"]["soil_m"], 0.52)

        zaid_temp = _safe_mean(seasons_data["zaid"]["temp"], 31.0)
        zaid_tot_rain = round(float(sum(seasons_data["zaid"]["precip"])), 2)
        zaid_rain_monthly = round(zaid_tot_rain / 3.0, 2)
        zaid_humidity = _safe_mean(seasons_data["zaid"]["humidity"], 62.0)
        zaid_wind = _safe_mean(seasons_data["zaid"]["wind"], 3.2)
        zaid_soil_m = _safe_mean(seasons_data["zaid"]["soil_m"], 0.35)

        annual_tot_rain = round(float(sum(all_valid_precip)), 2)
        annual_mean_temp = _safe_mean(all_valid_temp, 28.0)
        annual_mean_humidity = _safe_mean(all_valid_humidity, 72.0)
        annual_mean_soil_m = _safe_mean(all_valid_soil_m, 0.44)
        annual_mean_wind = _safe_mean(all_valid_wind, 3.1)

        result = {
            "status": "success",
            "district": prof["district"],
            "coordinates": {"lat": lat, "lon": lon},
            "observation_window": {
                "start_date": start_date_str,
                "end_date": end_date_str,
                "requested_reference_date": ref_date_str,
                "total_days_retrieved": len(dates)
            },
            "data_source": "Open-Meteo ERA5-Land Reanalysis (ECMWF)",
            "is_reanalysis": True,
            "annual_summary": {
                "total_rainfall_mm": annual_tot_rain,
                "mean_temperature_c": annual_mean_temp,
                "mean_relative_humidity_pct": annual_mean_humidity,
                "mean_soil_moisture_fraction": annual_mean_soil_m,
                "mean_wind_speed_ms": annual_mean_wind
            },
            "seasonal_breakdown": {
                "kharif": {
                    "season_label": "Kharif / Kuruvai (Jun–Sep, 4 Months)",
                    "total_rainfall_mm": kharif_tot_rain,
                    "monthly_avg_rainfall_mm": kharif_rain_monthly,
                    "mean_temperature_c": kharif_temp,
                    "mean_humidity_pct": kharif_humidity,
                    "mean_wind_speed_ms": kharif_wind,
                    "mean_soil_moisture_fraction": kharif_soil_m,
                    "days_recorded": seasons_data["kharif"]["days"]
                },
                "rabi": {
                    "season_label": "Rabi / Samba / Thaladi (Oct–Feb, 5 Months)",
                    "total_rainfall_mm": rabi_tot_rain,
                    "monthly_avg_rainfall_mm": rabi_rain_monthly,
                    "mean_temperature_c": rabi_temp,
                    "mean_humidity_pct": rabi_humidity,
                    "mean_wind_speed_ms": rabi_wind,
                    "mean_soil_moisture_fraction": rabi_soil_m,
                    "days_recorded": seasons_data["rabi"]["days"]
                },
                "zaid": {
                    "season_label": "Zaid / Navarai / Summer (Mar–May, 3 Months)",
                    "total_rainfall_mm": zaid_tot_rain,
                    "monthly_avg_rainfall_mm": zaid_rain_monthly,
                    "mean_temperature_c": zaid_temp,
                    "mean_humidity_pct": zaid_humidity,
                    "mean_wind_speed_ms": zaid_wind,
                    "mean_soil_moisture_fraction": zaid_soil_m,
                    "days_recorded": seasons_data["zaid"]["days"]
                }
            },
            "model_input_features": {
                "Kharif Temperature": kharif_temp,
                "Kharif Rainfall": kharif_rain_monthly,
                "Kharif Humidity": kharif_humidity,
                "Kharif Wind_Speed": kharif_wind,
                "Kharif Soil_Moisture": kharif_soil_m,
                "Rabi Temperature": rabi_temp,
                "Rabi Rainfall": rabi_rain_monthly,
                "Rabi Humidity": rabi_humidity,
                "Rabi Wind_Speed": rabi_wind,
                "Rabi Soil_Moisture": rabi_soil_m,
                "Zaid Temperature": zaid_temp,
                "Zaid Rainfall": zaid_rain_monthly,
                "Zaid Humidity": zaid_humidity,
                "Zaid Wind_Speed": zaid_wind,
                "Zaid Soil_Moisture": zaid_soil_m
            },
            "is_cached": False,
            "cached_at_timestamp": time.time(),
            "cached_at": datetime.now().isoformat()
        }

        # Save to local cache
        try:
            with open(cache_path, "w") as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass

        return result
