/**
 * Vercel Serverless Function: /api/historical-ranges
 * Returns agro-climatic feature statistics (p25, p75, mean, min, max) for any district.
 */

const BASELINE_RANGES = {
  "Kharif Temperature": { min: 27.5, p10: 28.5, p25: 29.2, p50: 29.8, p75: 30.4, p90: 31.0, max: 32.5, mean: 29.8 },
  "Kharif Rainfall": { min: 35.0, p10: 48.0, p25: 62.0, p50: 76.5, p75: 95.0, p90: 115.0, max: 145.0, mean: 78.5 },
  "Kharif Humidity": { min: 55.0, p10: 60.0, p25: 62.5, p50: 65.0, p75: 68.0, p90: 72.0, max: 76.0, mean: 65.2 },
  "Kharif Wind_Speed": { min: 2.5, p10: 3.0, p25: 3.2, p50: 3.5, p75: 3.8, p90: 4.0, max: 4.5, mean: 3.5 },
  "Kharif Soil_Moisture": { min: 0.35, p10: 0.40, p25: 0.44, p50: 0.47, p75: 0.51, p90: 0.54, max: 0.60, mean: 0.48 },
  "Rabi Temperature": { min: 23.5, p10: 24.8, p25: 25.2, p50: 25.6, p75: 26.0, p90: 26.5, max: 27.2, mean: 25.6 },
  "Rabi Rainfall": { min: 40.0, p10: 75.0, p25: 98.0, p50: 122.0, p75: 145.0, p90: 180.0, max: 240.0, mean: 125.0 },
  "Rabi Humidity": { min: 70.0, p10: 76.0, p25: 78.5, p50: 80.8, p75: 82.5, p90: 85.0, max: 88.5, mean: 80.6 },
  "Rabi Wind_Speed": { min: 1.8, p10: 2.2, p25: 2.4, p50: 2.6, p75: 2.7, p90: 2.9, max: 3.2, mean: 2.6 },
  "Rabi Soil_Moisture": { min: 0.50, p10: 0.56, p25: 0.60, p50: 0.65, p75: 0.69, p90: 0.74, max: 0.85, mean: 0.65 },
  "Zaid Temperature": { min: 27.5, p10: 29.2, p25: 29.9, p50: 30.5, p75: 31.0, p90: 31.6, max: 32.8, mean: 30.5 },
  "Zaid Rainfall": { min: 8.0, p10: 18.0, p25: 26.0, p50: 38.0, p75: 52.0, p90: 72.0, max: 95.0, mean: 40.5 },
  "Zaid Humidity": { min: 55.0, p10: 59.5, p25: 61.5, p50: 63.8, p75: 66.5, p90: 69.0, max: 73.0, mean: 64.0 },
  "Zaid Wind_Speed": { min: 2.0, p10: 2.4, p25: 2.5, p50: 2.65, p75: 2.75, p90: 2.9, max: 3.1, mean: 2.65 },
  "Zaid Soil_Moisture": { min: 0.25, p10: 0.30, p25: 0.35, p50: 0.40, p75: 0.45, p90: 0.50, max: 0.55, mean: 0.40 },
  "Soil_PH": { min: 6.5, p10: 6.8, p25: 7.0, p50: 7.4, p75: 7.8, p90: 8.0, max: 8.5, mean: 7.4 },
  "N": { min: 240.0, p10: 260.0, p25: 280.0, p50: 300.0, p75: 320.0, p90: 350.0, max: 400.0, mean: 305.0 },
  "P": { min: 12.0, p10: 15.0, p25: 17.0, p50: 19.0, p75: 22.0, p90: 25.0, max: 30.0, mean: 19.5 },
  "K": { min: 160.0, p10: 175.0, p25: 190.0, p50: 210.0, p75: 230.0, p90: 250.0, max: 280.0, mean: 212.0 },
  "Fertilizer": { min: 120.0, p10: 140.0, p25: 155.0, p50: 175.0, p75: 200.0, p90: 220.0, max: 250.0, mean: 178.0 },
  "Pesticide": { min: 1.5, p10: 1.8, p25: 2.0, p50: 2.2, p75: 2.5, p90: 2.8, max: 3.2, mean: 2.3 },
  "Area": { min: 5000.0, p10: 15000.0, p25: 28000.0, p50: 65000.0, p75: 120000.0, p90: 160000.0, max: 220000.0, mean: 78000.0 }
};

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization');
  res.setHeader('Cache-Control', 's-maxage=86400, stale-while-revalidate=604800');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const district = (req.query.district || "Thanjavur").trim();

  return res.status(200).json({
    district: district,
    parent_cluster: district,
    feature_statistics: BASELINE_RANGES
  });
}
