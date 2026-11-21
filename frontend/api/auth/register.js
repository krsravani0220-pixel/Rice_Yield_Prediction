const crypto = require('crypto');
let bcrypt = null;
try {
    bcrypt = require('bcryptjs');
} catch (e) {
    console.warn("bcryptjs not preloaded");
}

const NEON_SQL_URL = "https://ep-curly-queen-a13l2ioi.ap-southeast-1.aws.neon.tech/sql";
const NEON_CONN_STRING = "postgresql://neondb_owner:npg_EscR6lNWUSy0@ep-curly-queen-a13l2ioi-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require";

async function queryNeon(sql) {
    const res = await fetch(NEON_SQL_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Neon-Connection-String': NEON_CONN_STRING
        },
        body: JSON.stringify({ query: sql })
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Neon DB Error (${res.status}): ${text}`);
    }
    return await res.json();
}

function escapeSql(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "''").replace(/\\/g, "\\\\");
}

module.exports = async (req, res) => {
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ detail: "Method Not Allowed" });
    }

    try {
        let body = req.body;
        if (typeof body === 'string') {
            try { body = JSON.parse(body); } catch(e) {}
        }
        const { full_name, email, password, district, role, phone } = body || {};

        if (!full_name || !email || !password) {
            return res.status(400).json({ detail: "Please provide full name, email, and password." });
        }

        const cleanEmail = String(email).trim().toLowerCase();
        const checkSql = `SELECT id FROM users WHERE LOWER(email) = '${escapeSql(cleanEmail)}' LIMIT 1;`;
        const checkData = await queryNeon(checkSql);

        if (checkData.rows && checkData.rows.length > 0) {
            return res.status(400).json({ detail: "An account with this email is already registered. Please sign in." });
        }

        let pwHash = "";
        if (bcrypt) {
            pwHash = bcrypt.hashSync(password, 10);
        } else {
            const salt = crypto.randomBytes(16).toString('hex');
            const hashed = crypto.createHash('sha256').update(salt + password).digest('hex');
            pwHash = `sha256$${salt}$${hashed}`;
        }

        const apiKey = `ry_live_${crypto.randomBytes(16).toString('hex')}`;
        const userDistrict = district || 'Thanjavur';
        const userRole = role || 'Farmer';
        const userPhone = phone || '';

        const insertSql = `
            INSERT INTO users (full_name, email, password_hash, district, role, phone, api_key, farm_size, preferred_soil, primary_crop, created_at, last_login_at, updated_at)
            VALUES ('${escapeSql(full_name)}', '${escapeSql(cleanEmail)}', '${pwHash}', '${escapeSql(userDistrict)}', '${escapeSql(userRole)}', '${escapeSql(userPhone)}', '${apiKey}', 5.0, 'Clayey', 'Rice (Paddy)', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, full_name, email, district, role, phone, api_key, farm_size, preferred_soil, primary_crop, created_at;
        `;

        const insertData = await queryNeon(insertSql);
        const newUser = (insertData.rows && insertData.rows[0]) ? insertData.rows[0] : null;

        if (!newUser) {
            return res.status(500).json({ detail: "Failed to persist user in Neon Cloud database." });
        }

        const token = "ry_jwt_" + Buffer.from(JSON.stringify({
            sub: String(newUser.id),
            email: newUser.email,
            role: newUser.role,
            exp: Math.floor(Date.now() / 1000) + (7 * 86400)
        })).toString('base64');

        return res.status(200).json({
            status: "success",
            message: "Account created successfully in Neon Cloud database.",
            token: token,
            user: newUser
        });
    } catch (err) {
        console.error("Auth register error:", err);
        return res.status(500).json({ detail: "Registration server error: " + err.message });
    }
};
