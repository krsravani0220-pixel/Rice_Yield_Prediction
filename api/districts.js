/**
 * Vercel Serverless Function: /api/districts
 * Returns all 38 Tamil Nadu districts and recognized agricultural soil types.
 * Fully self-contained with 0ms cold start and zero external dependencies.
 */

const TAMIL_NADU_DISTRICTS = [
  "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
  "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
  "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
  "Nagapattinam", "Namakkal", "Perambalur", "Pudukkottai", "Ramanathapuram",
  "Ranipet", "Salem", "Sivagangai", "Tenkasi", "Thanjavur",
  "The Nilgiris", "Theni", "Thiruvallur", "Thiruvannamalai", "Thiruvarur",
  "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur",
  "Vellore", "Villupuram", "Virudhunagar"
];

const SOIL_TYPES = [
  "alluvial soil", "black soil", "coastal alluvium", "coastal sandy soil",
  "laterite soil", "red soil", "red loamy soil", "red sandy loam soil",
  "red sandy soil", "sandy soil"
];

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization');
  res.setHeader('Cache-Control', 's-maxage=86400, stale-while-revalidate=604800');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  return res.status(200).json({
    status: "success",
    count: TAMIL_NADU_DISTRICTS.length,
    districts: TAMIL_NADU_DISTRICTS,
    soil_types: SOIL_TYPES
  });
}
