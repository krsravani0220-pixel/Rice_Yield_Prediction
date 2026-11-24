/**
 * Vercel Serverless Function: /api/crop-health
 * Returns TNAU-compliant targeted crop health advisories in English and Tamil.
 */

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const body = req.body || {};
  const stage = body.growth_stage || "Tillering";
  const pest = body.pest_obs || "none";
  const disease = body.disease_obs || "none";

  const advisories_en = [
    `Stage Action (${stage}): Maintain 2.5–5.0 cm thin water layer during tillering to promote root anchorage and tillering count.`,
    pest !== 'none'
      ? `Pest Advisory: Observed ${pest}. Apply neem oil (3ml/L) or recommended IPM botanical spray. Avoid broad-spectrum pyrethroids.`
      : "Pest Management: Field scouting indicates pest pressure is below economic injury level (EIL). Continue routine pheromone trap monitoring.",
    disease !== 'none'
      ? `Disease Advisory: Observed ${disease}. Spray Tricyclazole 75% WP @ 0.6g/L or Pseudomonas fluorescens @ 2.5kg/ha.`
      : "Disease Management: Foliar canopy is healthy. Maintain balanced potassium (K) nutrition to bolster cell wall resistance."
  ];

  const advisories_ta = [
    `பயிர் வளர்ச்சி நிலை வழிகாட்டல் (${stage}): தூர்கட்டும் பருவத்தில் வயலில் 2.5 முதல் 5.0 செ.மீ வரை சீரான நீர் மட்டம் பராமரிக்கவும்.`,
    pest !== 'none'
      ? `பூச்சி மேலாண்மை: ${pest} பாதிப்பு தென்படுகிறது. வேப்ப எண்ணெய் (3 மி.லி/லி) அல்லது பரிந்துரைக்கப்பட்ட இயற்கை பூச்சிக்கொல்லி தெளிக்கவும்.`
      : "பூச்சி மேலாண்மை: பூச்சி தாக்குதல் பொருளாதார சேத நிலைக்குக் குறைவாக உள்ளது. இனக்கவர்ச்சி பொறிகளைத் தொடர்ந்து கண்காணிக்கவும்.",
    disease !== 'none'
      ? `நோய் மேலாண்மை: ${disease} அறிகுறிகள் உள்ளன. டிரைசைக்ளசோல் 75% WP @ 0.6 கிராம்/லிட்டர் அல்லது சூடோமோனாஸ் தெளிக்கவும்.`
      : "நோய் மேலாண்மை: இலைகள் ஆரோக்கியமாக உள்ளன. பொட்டாஷ் சத்தை பரிந்துரைக்கப்பட்ட அளவில் இட்டு நோய் எதிர்ப்பு சக்தியை அதிகரிக்கவும்."
  ];

  return res.status(200).json({
    status: "success",
    growth_stage: stage,
    advisories_en: advisories_en,
    advisories_ta: advisories_ta
  });
}
