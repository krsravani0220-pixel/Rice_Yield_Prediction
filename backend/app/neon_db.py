import os
import sys
import json
import datetime
from typing import Optional, Dict, Any, List
import bcrypt
import jwt

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
                return
            except Exception as e:
                self.connection_error = str(e)
                print(f"⚠️ Neon connection attempt failed: {e}. Falling back to local storage.")
        
        # Fallback to local SQLite
        self.is_neon = False
        self._create_tables_sqlite()
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

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                    if cur.fetchone():
                        raise ValueError("An account with this email address already exists. Please Sign In.")
                    
                    cur.execute("""
                    INSERT INTO users (full_name, email, password_hash, district, role, phone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, full_name, email, district, role, phone, created_at;
                    """, (full_name, email, hashed, district, role, phone))
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
                INSERT INTO users (full_name, email, password_hash, district, role, phone)
                VALUES (?, ?, ?, ?, ?, ?);
                """, (full_name, email, hashed, district, role, phone))
                user_id = cur.lastrowid
                conn.commit()
                return {
                    "id": user_id,
                    "full_name": full_name,
                    "email": email,
                    "district": district,
                    "role": role,
                    "phone": phone,
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
            finally:
                conn.close()

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        email = email.strip().lower()

        if self.is_neon:
            conn = self._get_pg_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()
                    if not user:
                        raise ValueError("No account found with this email. Please check or register.")
                    
                    pw_hash = user['password_hash']
                    if not bcrypt.checkpw(password.encode('utf-8'), pw_hash.encode('utf-8')):
                        raise ValueError("Incorrect password. Please try again.")

                    user_dict = dict(user)
                    user_dict.pop('password_hash', None)
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
                if not bcrypt.checkpw(password.encode('utf-8'), pw_hash.encode('utf-8')):
                    raise ValueError("Incorrect password. Please try again.")

                return {
                    "id": row['id'],
                    "full_name": row['full_name'],
                    "email": row['email'],
                    "district": row['district'],
                    "role": row['role'],
                    "phone": row['phone'],
                    "created_at": row['created_at']
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
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
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
