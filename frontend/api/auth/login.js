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
        const { email, password } = body || {};

        if (!email || !password) {
            return res.status(400).json({ detail: "Please provide both email and password." });
        }

        const cleanEmail = String(email).trim().toLowerCase();
        const sql = `SELECT id, full_name, email, password_hash, district, role, phone, api_key, farm_size, preferred_soil, primary_crop FROM users WHERE LOWER(email) = '${escapeSql(cleanEmail)}' LIMIT 1;`;
        
        const data = await queryNeon(sql);
        const rows = data.rows || [];
        if (rows.length === 0) {
            return res.status(401).json({ detail: "No account found with this email. Please check or register." });
        }

        const user = rows[0];
        const pwHash = user.password_hash || '';
        let isValid = false;

        if (pwHash.startsWith('$2') && bcrypt) {
            isValid = bcrypt.compareSync(password, pwHash);
        } else if (pwHash.startsWith('sha256$')) {
            const parts = pwHash.split('$');
            if (parts.length === 3) {
                const salt = parts[1];
                const expected = parts[2];
                const computed = crypto.createHash('sha256').update(salt + password).digest('hex');
                isValid = (computed.toLowerCase() === expected.toLowerCase());
            }
        }

        if (!isValid) {
            return res.status(401).json({ detail: "Incorrect password. Please verify your password and try again." });
        }

        queryNeon(`UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ${user.id};`).catch(() => {});

        const safeUser = { ...user };
        delete safeUser.password_hash;

        const token = "ry_jwt_" + Buffer.from(JSON.stringify({
            sub: String(user.id),
            email: user.email,
            role: user.role,
            exp: Math.floor(Date.now() / 1000) + (7 * 86400)
        })).toString('base64');

        return res.status(200).json({
            status: "success",
            message: "Successfully signed in via Neon Cloud PostgreSQL.",
            token: token,
            user: safeUser
        });
    } catch (err) {
        console.error("Auth login error:", err);
        return res.status(500).json({ detail: "Authentication server error: " + err.message });
    }
};
