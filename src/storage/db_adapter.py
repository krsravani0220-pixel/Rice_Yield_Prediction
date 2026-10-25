"""
Database Storage Adapter (NeonDB / Local Structured Store)
===========================================================
Provides optional, credential-safe logging of structured rice-yield predictions
and satellite telemetry. Connects to NeonDB serverless PostgreSQL only if
NEON_DATABASE_URL is provided in configuration. Never exposes or logs credentials.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Safely load .env from project root
try:
    from dotenv import load_dotenv
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv()
except Exception:
    pass

LOCAL_LOG_PATH = os.path.abspath("data/cache/prediction_records.jsonl")


class DatabaseAdapter:
    """
    Safely connects to NeonDB if configured, or gracefully logs locally.
    Never stores or logs API credentials or database passwords.
    """
    def __init__(self):
        self.db_url = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
        self.is_neon_configured = bool(self.db_url and "neon.tech" in self.db_url)
        self._conn = None
        if self.is_neon_configured:
            try:
                self._get_connection()
                self._init_neon_table()
            except Exception as e:
                # Never expose connection string or credentials in log
                print("Notice: NeonDB initial connection deferred:", type(e).__name__)
                self.is_neon_configured = False

    def _get_connection(self):
        """Returns active database connection with automatic reconnection and autocommit for serverless PostgreSQL."""
        if not self.is_neon_configured or not self.db_url:
            return None
        try:
            import psycopg2
            if self._conn is None or self._conn.closed != 0:
                self._conn = psycopg2.connect(self.db_url, connect_timeout=10)
                self._conn.autocommit = True
            return self._conn
        except Exception:
            return None

    def _init_neon_table(self):
        """Creates table for structured prediction telemetry if NeonDB is connected."""
        conn = self._get_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS rice_yield_predictions (
                        id SERIAL PRIMARY KEY,
                        district VARCHAR(50) NOT NULL,
                        year INT NOT NULL,
                        reference_date VARCHAR(25),
                        weather_period_start VARCHAR(25),
                        weather_period_end VARCHAR(25),
                        weather_source VARCHAR(120),
                        satellite_observation_dates TEXT,
                        calculated_features TEXT,
                        baseline_yield FLOAT,
                        satellite_yield FLOAT,
                        ndvi_mean FLOAT,
                        ndre_mean FLOAT,
                        model_version VARCHAR(50),
                        status VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Ensure new columns exist on legacy tables without errors
                columns_to_add = [
                    ("reference_date", "VARCHAR(25)"),
                    ("weather_period_start", "VARCHAR(25)"),
                    ("weather_period_end", "VARCHAR(25)"),
                    ("weather_source", "VARCHAR(120)"),
                    ("satellite_observation_dates", "TEXT"),
                    ("calculated_features", "TEXT"),
                    ("ndvi_mean", "FLOAT"),
                    ("ndre_mean", "FLOAT"),
                    ("model_version", "VARCHAR(50)")
                ]
                for col_name, col_type in columns_to_add:
                    try:
                        cur.execute(f"ALTER TABLE rice_yield_predictions ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                    except Exception:
                        pass
        except Exception:
            pass

    def record_prediction(self, record: Dict[str, Any]) -> bool:
        """
        Records a prediction event safely with full provenance.
        Logs to NeonDB PostgreSQL if available, and always writes to local JSONL log.
        """
        district = str(record.get("district", "Unknown"))
        
        raw_year = record.get("year")
        year = int(raw_year) if raw_year is not None else datetime.now().year
        
        ref_date = str(record.get("reference_date") or datetime.now().strftime("%Y-%m-%d"))
        
        w_start = str(record.get("weather_period_start") or record.get("weather_observation_start") or "")
        w_end = str(record.get("weather_period_end") or record.get("weather_observation_end") or "")
        w_source = str(record.get("weather_source") or "Open-Meteo ERA5-Land Reanalysis")
        
        # Satellite observation dates
        sat_dates = record.get("satellite_observation_dates") or []
        if isinstance(sat_dates, list):
            sat_dates_str = ", ".join([str(d) for d in sat_dates[:20]])
        else:
            sat_dates_str = str(sat_dates)

        # Calculated features
        features = record.get("calculated_features") or record.get("features") or {}
        features_json = json.dumps(features) if isinstance(features, dict) else str(features)
        
        raw_base = record.get("baseline_yield") or record.get("baseline_tabular_yield_tha") or record.get("predicted_yield")
        baseline_yield = round(float(raw_base), 3) if raw_base is not None else None
        
        raw_sat = record.get("satellite_yield") or record.get("satellite_enhanced_yield_tha")
        satellite_yield = round(float(raw_sat), 3) if raw_sat is not None else None
        
        ndvi = float(record.get("ndvi_mean")) if record.get("ndvi_mean") is not None else None
        ndre = float(record.get("ndre_mean")) if record.get("ndre_mean") is not None else None
        
        model_version = str(record.get("model_version") or "ExtraTreesRegressor_v1.0")
        status = str(record.get("status") or record.get("prediction_status", "success"))

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "district": district,
            "year": year,
            "reference_date": ref_date,
            "weather_period_start": w_start,
            "weather_period_end": w_end,
            "weather_source": w_source,
            "satellite_observation_dates": sat_dates_str,
            "baseline_yield": baseline_yield,
            "satellite_yield": satellite_yield,
            "ndvi_mean": ndvi,
            "ndre_mean": ndre,
            "model_version": model_version,
            "status": status
        }

        # 1. Record in NeonDB if configured
        neon_success = False
        if self.is_neon_configured:
            try:
                conn = self._get_connection()
                if conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO rice_yield_predictions (
                                district, year, reference_date, weather_period_start,
                                weather_period_end, weather_source, satellite_observation_dates,
                                calculated_features, baseline_yield, satellite_yield,
                                ndvi_mean, ndre_mean, model_version, status
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (
                            district, year, ref_date, w_start, w_end, w_source,
                            sat_dates_str, features_json, baseline_yield, satellite_yield,
                            ndvi, ndre, model_version, status
                        ))
                    neon_success = True
            except Exception:
                try:
                    if self._conn and self._conn.closed == 0:
                        self._conn.rollback()
                except Exception:
                    pass
                neon_success = False

        # 2. Local fallback log (always preserved)
        try:
            os.makedirs(os.path.dirname(LOCAL_LOG_PATH), exist_ok=True)
            with open(LOCAL_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            jsonl_success = True
        except Exception:
            jsonl_success = False

        return neon_success or jsonl_success

    def get_recent_predictions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves recent prediction records from NeonDB if available, else local JSONL."""
        if self.is_neon_configured:
            try:
                conn = self._get_connection()
                if conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT id, district, year, reference_date, baseline_yield,
                                   satellite_yield, ndvi_mean, status, created_at
                            FROM rice_yield_predictions
                            ORDER BY id DESC
                            LIMIT %s;
                        """, (limit,))
                        rows = cur.fetchall()
                        results = []
                        for r in rows:
                            results.append({
                                "id": r[0],
                                "district": r[1],
                                "year": r[2],
                                "reference_date": r[3],
                                "baseline_yield": r[4],
                                "satellite_yield": r[5],
                                "ndvi_mean": r[6],
                                "status": r[7],
                                "created_at": r[8].isoformat() if r[8] else None,
                                "source": "NeonDB Serverless PostgreSQL"
                            })
                        return results
            except Exception:
                pass

        # Fallback to local JSONL
        records = []
        if os.path.exists(LOCAL_LOG_PATH):
            try:
                with open(LOCAL_LOG_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            records.append(json.loads(line.strip()))
                records = records[-limit:]
                records.reverse()
                for rec in records:
                    rec["source"] = "Local Structured Log"
            except Exception:
                pass
        return records
