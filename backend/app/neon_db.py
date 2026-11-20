import os
import sys
import json
import datetime
import hashlib
import hmac
import base64
import secrets
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')))
except Exception:
    pass

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# Try importing psycopg2 for Neon PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Try sqlite3 as automatic graceful fallback if Neon DATABASE_URL is not set
import sqlite3

JWT_SECRET = os.getenv("JWT_SECRET", "tamilnadu-rice-yield-dss-neon-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

def _secure_hash(password: str) -> str:
    if BCRYPT_AVAILABLE:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"sha256${salt}${hashed}"

def _verify_hash(password: str, pw_hash: str) -> bool:
    if pw_hash.startswith("sha256$"):
        parts = pw_hash.split("$")
        if len(parts) == 3:
            salt = parts[1]
            expected = parts[2]
            computed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
            return hmac.compare_digest(expected, computed)
    if BCRYPT_AVAILABLE:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), pw_hash.encode('utf-8'))
        except Exception:
            return False
    # Fallback comparison if plain sha256 was used
    return False

class NeonDatabaseManager:
    def __init__(self):
        self.neon_url = os.getenv("DATABASE_URL") or os.getenv("NEON_DATABASE_URL")
        self.is_neon = False
        self.connection_error = None
        self._init_connection()

    def _init_connection(self):
        if self.neon_url and PSYCOPG2_AVAILABLE:
            try:
                # Test connection to Neon PostgreSQL
                conn = psycopg2.connect(self.neon_url, sslmode='require')
                conn.close()
                self.is_neon = True
                print(" Successfully connected to Neon Cloud PostgreSQL!")
                self._create_tables_postgres()
                self._ensure_profile_columns()
                return
            except Exception as e:
                self.connection_error = str(e)
                print(f"⚠️ Neon connection attempt failed: {e}. Falling back to local storage.")
        
        # Fallback to local SQLite
        self.is_neon = False
        self._create_tables_sqlite()
        self._ensure_profile_columns()
        print(" Using local database fallback for user storage (Set DATABASE_URL to link Neon.tech).")

    def _get_pg_connection(self):
        return psycopg2.connect(self.neon_url, sslmode='require')

    def _get_sqlite_connection(self):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/user_auth_store.db'))
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables_postgres(self):
        sql_users = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(120) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            district VARCHAR(100) DEFAULT 'Thanjavur',
            role VARCHAR(50) DEFAULT 'Farmer',
            phone VARCHAR(30),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """
        sql_predictions = """
        CREATE TABLE IF NOT EXISTS user_predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            district VARCHAR(100) NOT NULL,
            year INTEGER NOT NULL,
            prediction_type VARCHAR(50) NOT NULL,
            predicted_yield NUMERIC(6, 2) NOT NULL,
            unit VARCHAR(20) DEFAULT 'tonnes/ha',
            input_summary JSONB,
            shap_insights JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_user_predictions_user_id ON user_predictions(user_id);
        """
        conn = self._get_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql_users)
                cur.execute(sql_predictions)
            conn.commit()
            print(" Neon PostgreSQL tables verified/created successfully.")
        finally:
            conn.close()

    def _create_tables_sqlite(self):
        conn = self._get_sqlite_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                district TEXT DEFAULT 'Thanjavur',
                role TEXT DEFAULT 'Farmer',
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS user_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                district TEXT NOT NULL,
                year INTEGER NOT NULL,
                prediction_type TEXT NOT NULL,
                predicted_yield REAL NOT NULL,
                unit TEXT DEFAULT 'tonnes/ha',
                input_summary TEXT,
                shap_insights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()
        finally:
            conn.close()

    def _ensure_profile_columns(self):
        if self.is_neon:
            cols = [
                ("farm_size", "REAL DEFAULT 5.0"),
                ("preferred_soil", "VARCHAR(100) DEFAULT 'Clayey'"),
                ("primary_crop", "VARCHAR(100) DEFAULT 'Rice (Paddy)'"),
                ("api_key", "VARCHAR(150)"),
                ("external_api_keys", "TEXT DEFAULT '{}'"),
                ("last_login_at", "TIMESTAMP WITH TIME ZONE"),
                ("updated_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
            ]
            conn = self._get_pg_connection()
            try:
                with conn.cursor() as cur:
                    for col_name, col_type in cols:
                        try:
                            cur.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                        except Exception:
                            pass
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()
        else:
            cols = [
                ("farm_size", "REAL DEFAULT 5.0"),
                ("preferred_soil", "TEXT DEFAULT 'Clayey'"),
                ("primary_crop", "TEXT DEFAULT 'Rice (Paddy)'"),
                ("api_key", "TEXT"),
                ("external_api_keys", "TEXT DEFAULT '{}'"),
                ("last_login_at", "TEXT"),
                ("updated_at", "TEXT")
            ]
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                for col_name, col_type in cols:
                    try:
                        cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")
                    except Exception:
                        pass
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()

    # --- Authentication Methods ---

    def register_user(self, full_name: str, email: str, password: str, district: str = "Thanjavur", role: str = "Farmer", phone: str = "") -> Dict[str, Any]:
        email = email.strip().lower()
        full_name = full_name.strip()
        district = district.strip() or "Thanjavur"
        role = role.strip() or "Farmer"

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if "@" not in email or "." not in email:
            raise ValueError("Please provide a valid email address.")

        hashed = _secure_hash(password)
        api_key = f"ry_live_{secrets.token_hex(16)}"
        now_ts = datetime.datetime.utcnow().isoformat()

        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                    if cur.fetchone():
                        raise ValueError("An account with this email address already exists. Please Sign In.")
                    
                    cur.execute("""
                    INSERT INTO users (full_name, email, password_hash, district, role, phone, api_key, farm_size, preferred_soil, primary_crop, created_at, last_login_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 5.0, 'Clayey', 'Rice (Paddy)', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id, full_name, email, district, role, phone, api_key, farm_size, preferred_soil, primary_crop, created_at, last_login_at, updated_at;
                    """, (full_name, email, hashed, district, role, phone, api_key))
                    user = cur.fetchone()
                conn.commit()
                return dict(user)
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cur.fetchone():
                    raise ValueError("An account with this email address already exists. Please Sign In.")

                cur.execute("""
                INSERT INTO users (full_name, email, password_hash, district, role, phone, api_key, farm_size, preferred_soil, primary_crop, created_at, last_login_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 5.0, 'Clayey', 'Rice (Paddy)', ?, ?, ?);
                """, (full_name, email, hashed, district, role, phone, api_key, now_ts, now_ts, now_ts))
                user_id = cur.lastrowid
                conn.commit()
                return {
                    "id": user_id,
                    "full_name": full_name,
                    "email": email,
                    "district": district,
                    "role": role,
                    "phone": phone,
                    "api_key": api_key,
                    "farm_size": 5.0,
                    "preferred_soil": "Clayey",
                    "primary_crop": "Rice (Paddy)",
                    "created_at": now_ts,
                    "last_login_at": now_ts,
                    "updated_at": now_ts
                }
            finally:
                conn.close()

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        email = email.strip().lower()
        now_ts = datetime.datetime.utcnow().isoformat()

        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()
                    if not user:
                        raise ValueError("No account found with this email. Please check or register.")
                    
                    pw_hash = user['password_hash']
                    if not _verify_hash(password, pw_hash):
                        raise ValueError("Incorrect password. Please try again.")

                    user_dict = dict(user)
                    user_dict.pop('password_hash', None)

                    # Ensure api_key exists
                    if not user_dict.get('api_key'):
                        user_dict['api_key'] = f"ry_live_{secrets.token_hex(16)}"
                    
                    cur.execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP, api_key = %s WHERE id = %s", 
                                (user_dict['api_key'], user_dict['id']))
                conn.commit()
                return user_dict
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cur.fetchone()
                if not row:
                    raise ValueError("No account found with this email. Please check or register.")
                
                pw_hash = row['password_hash']
                if not _verify_hash(password, pw_hash):
                    raise ValueError("Incorrect password. Please try again.")

                row_dict = dict(row)
                api_key = row_dict.get('api_key') or f"ry_live_{secrets.token_hex(16)}"
                cur.execute("UPDATE users SET last_login_at = ?, api_key = ? WHERE id = ?", (now_ts, api_key, row_dict['id']))
                conn.commit()

                return {
                    "id": row_dict['id'],
                    "full_name": row_dict['full_name'],
                    "email": row_dict['email'],
                    "district": row_dict.get('district', 'Thanjavur'),
                    "role": row_dict.get('role', 'Farmer'),
                    "phone": row_dict.get('phone', ''),
                    "api_key": api_key,
                    "farm_size": row_dict.get('farm_size', 5.0),
                    "preferred_soil": row_dict.get('preferred_soil', 'Clayey'),
                    "primary_crop": row_dict.get('primary_crop', 'Rice (Paddy)'),
                    "created_at": row_dict.get('created_at', now_ts),
                    "last_login_at": now_ts,
                    "updated_at": row_dict.get('updated_at', now_ts)
                }
            finally:
                conn.close()

    def create_token(self, user_dict: Dict[str, Any]) -> str:
        payload = {
            "sub": str(user_dict["id"]),
            "email": user_dict["email"],
            "full_name": user_dict["full_name"],
            "district": user_dict.get("district", "Thanjavur"),
            "role": user_dict.get("role", "Farmer"),
            "exp": (datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp()
        }
        if JWT_AVAILABLE:
            try:
                return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            except Exception:
                pass
        # Graceful token fallback
        data_str = json.dumps(payload, default=str)
        b64_data = base64.urlsafe_b64encode(data_str.encode()).decode()
        sig = hmac.new(JWT_SECRET.encode(), b64_data.encode(), hashlib.sha256).hexdigest()
        return f"{b64_data}.{sig}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        if JWT_AVAILABLE:
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                return payload
            except Exception:
                pass
        try:
            parts = token.split(".")
            if len(parts) == 2:
                b64_data, sig = parts
                expected_sig = hmac.new(JWT_SECRET.encode(), b64_data.encode(), hashlib.sha256).hexdigest()
                if hmac.compare_digest(expected_sig, sig):
                    data_str = base64.urlsafe_b64decode(b64_data.encode()).decode()
                    payload = json.loads(data_str)
                    if payload.get("exp") and datetime.datetime.utcnow().timestamp() > payload["exp"]:
                        return None
                    return payload
            return None
        except Exception:
            return None

    # --- Prediction History Methods ---

    def save_prediction(self, user_id: int, district: str, year: int, prediction_type: str, 
                        predicted_yield: float, input_summary: Optional[Dict] = None, 
                        shap_insights: Optional[Dict] = None) -> int:
        input_json = json.dumps(input_summary or {})
        shap_json = json.dumps(shap_insights or {})

        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                    INSERT INTO user_predictions 
                    (user_id, district, year, prediction_type, predicted_yield, input_summary, shap_insights)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """, (user_id, district, year, prediction_type, predicted_yield, input_json, shap_json))
                    pred_id = cur.fetchone()[0]
                conn.commit()
                return pred_id
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO user_predictions 
                (user_id, district, year, prediction_type, predicted_yield, input_summary, shap_insights)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (user_id, district, year, prediction_type, predicted_yield, input_json, shap_json))
                pred_id = cur.lastrowid
                conn.commit()
                return pred_id
            finally:
                conn.close()

    def get_user_predictions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                    SELECT id, district, year, prediction_type, predicted_yield, unit, 
                           input_summary, shap_insights, created_at
                    FROM user_predictions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s;
                    """, (user_id, limit))
                    rows = cur.fetchall()
                    return [dict(r) for r in rows]
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                SELECT id, district, year, prediction_type, predicted_yield, unit, 
                       input_summary, shap_insights, created_at
                FROM user_predictions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?;
                """, (user_id, limit))
                rows = cur.fetchall()
                result = []
                for r in rows:
                    result.append({
                        "id": r["id"],
                        "district": r["district"],
                        "year": r["year"],
                        "prediction_type": r["prediction_type"],
                        "predicted_yield": r["predicted_yield"],
                        "unit": r["unit"],
                        "input_summary": json.loads(r["input_summary"]) if r["input_summary"] else {},
                        "shap_insights": json.loads(r["shap_insights"]) if r["shap_insights"] else {},
                        "created_at": r["created_at"]
                    })
                return result
            finally:
                conn.close()

    # --- Profile & API Key Management Methods ---

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                    SELECT id, full_name, email, district, role, phone, api_key, 
                           farm_size, preferred_soil, primary_crop, external_api_keys,
                           created_at, last_login_at, updated_at
                    FROM users WHERE id = %s
                    """, (user_id,))
                    row = cur.fetchone()
                    if not row:
                        return None
                    profile = dict(row)
                    cur.execute("SELECT COUNT(*) as count FROM user_predictions WHERE user_id = %s", (user_id,))
                    c_row = cur.fetchone()
                    profile["total_predictions"] = c_row["count"] if c_row else 0
                    if not profile.get("api_key"):
                        profile["api_key"] = f"ry_live_{secrets.token_hex(16)}"
                        cur.execute("UPDATE users SET api_key = %s WHERE id = %s", (profile["api_key"], user_id))
                        conn.commit()
                    if isinstance(profile.get("external_api_keys"), str):
                        try:
                            profile["external_api_keys"] = json.loads(profile["external_api_keys"])
                        except Exception:
                            profile["external_api_keys"] = {}
                    return profile
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                SELECT id, full_name, email, district, role, phone, api_key,
                       farm_size, preferred_soil, primary_crop, external_api_keys,
                       created_at, last_login_at, updated_at
                FROM users WHERE id = ?
                """, (user_id,))
                row = cur.fetchone()
                if not row:
                    return None
                profile = dict(row)
                cur.execute("SELECT COUNT(*) as count FROM user_predictions WHERE user_id = ?", (user_id,))
                c_row = cur.fetchone()
                profile["total_predictions"] = c_row["count"] if c_row else 0
                if not profile.get("api_key"):
                    profile["api_key"] = f"ry_live_{secrets.token_hex(16)}"
                    cur.execute("UPDATE users SET api_key = ? WHERE id = ?", (profile["api_key"], user_id))
                    conn.commit()
                if isinstance(profile.get("external_api_keys"), str):
                    try:
                        profile["external_api_keys"] = json.loads(profile["external_api_keys"])
                    except Exception:
                        profile["external_api_keys"] = {}
                return profile
            finally:
                conn.close()

    def update_user_profile(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        now_ts = datetime.datetime.utcnow().isoformat()
        allowed = ["full_name", "phone", "district", "role", "farm_size", "preferred_soil", "primary_crop"]
        data_to_update = {k: v for k, v in updates.items() if k in allowed and v is not None}
        
        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if data_to_update:
                        set_clauses = [f"{k} = %s" for k in data_to_update.keys()]
                        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                        values = list(data_to_update.values()) + [user_id]
                        cur.execute(f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s", values)
                        conn.commit()
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                if data_to_update:
                    set_clauses = [f"{k} = ?" for k in data_to_update.keys()]
                    set_clauses.append("updated_at = ?")
                    values = list(data_to_update.values()) + [now_ts, user_id]
                    cur.execute(f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?", values)
                    conn.commit()
            finally:
                conn.close()

        return self.get_user_profile(user_id) or {}

    def regenerate_api_key(self, user_id: int) -> str:
        new_key = f"ry_live_{secrets.token_hex(16)}"
        now_ts = datetime.datetime.utcnow().isoformat()
        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE users SET api_key = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (new_key, user_id))
                conn.commit()
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE users SET api_key = ?, updated_at = ? WHERE id = ?", (new_key, now_ts, user_id))
                conn.commit()
            finally:
                conn.close()
        return new_key

    def save_external_api_keys(self, user_id: int, external_keys: Dict[str, str]) -> Dict[str, str]:
        keys_json = json.dumps(external_keys)
        now_ts = datetime.datetime.utcnow().isoformat()
        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE users SET external_api_keys = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (keys_json, user_id))
                conn.commit()
            finally:
                conn.close()
        else:
            conn = self._get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE users SET external_api_keys = ?, updated_at = ? WHERE id = ?", (keys_json, now_ts, user_id))
                conn.commit()
            finally:
                conn.close()
        return external_keys

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_neon_configured": bool(self.neon_url),
            "connected_to_neon": self.is_neon,
            "engine": "Neon Cloud PostgreSQL" if self.is_neon else "Local Structured Store (Fallback)",
            "connection_error": self.connection_error,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

# Global Singleton Manager
db_manager = NeonDatabaseManager()
