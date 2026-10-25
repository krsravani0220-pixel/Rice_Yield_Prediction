const API_BASE = (typeof window !== 'undefined' && window.location.origin.includes(':8000')) ? "" : "http://127.0.0.1:8000";

let currentLang = 'en';
let currentDistrictStats = {};
let lastManualResult = null;
let lastForecastResult = null;
let lastLiveResult = null;

let showManualShap = false;
let showManualInsights = false;
let showForecastShap = false;
let showForecastInsights = false;

// Broad, realistic agricultural domain boundaries (Prevents false positive unusual warnings)
const DOMAIN_VALIDATION_BOUNDS = {
    'Temperature': {
        normalMin: 10.0, normalMax: 45.0,
        physMin: 0.0, physMax: 55.0,
        unit: '°C',
        err: 'Temperature must be between 0.0°C and 55.0°C.',
        warn: '⚠️ Extreme Condition: Heatwave / Extreme Temperature — prediction allowed.'
    },
    'Rainfall': {
        normalMin: 0.0, normalMax: 750.0,
        physMin: 0.0, physMax: 2500.0,
        unit: 'mm',
        err: 'Rainfall must be between 0.0 mm and 2500.0 mm.',
        warn: '⚠️ Extreme Condition: Exceptional Heavy Rainfall — prediction allowed.'
    },
    'Humidity': {
        normalMin: 10.0, normalMax: 98.0,
        physMin: 0.0, physMax: 100.0,
        unit: '%',
        err: 'Humidity must be between 0.0% and 100.0%.',
        warn: '⚠️ Extreme Condition: Near Saturation Humidity — prediction allowed.'
    },
    'Wind_Speed': {
        normalMin: 0.0, normalMax: 20.0,
        physMin: 0.0, physMax: 45.0,
        unit: 'm/s',
        err: 'Wind Speed must be between 0.0 m/s and 45.0 m/s.',
        warn: '⚠️ Extreme Condition: High Storm Wind Speed — prediction allowed.'
    },
    'Soil_Moisture': {
        normalMin: 0.05, normalMax: 0.92,
        physMin: 0.0, physMax: 1.0,
        unit: 'ratio',
        err: 'Soil Moisture must be between 0.00 and 1.00.',
        warn: '⚠️ Extreme Condition: Severe Drought/Waterlogging — prediction allowed.'
    },
    'Soil_PH': {
        normalMin: 4.8, normalMax: 9.2,
        physMin: 1.0, physMax: 11.5,
        unit: 'pH',
        err: 'Soil pH must be between 1.0 and 11.5.',
        warn: '⚠️ Extreme Condition: Severe Acidity/Alkalinity — prediction allowed.'
    },
    'N': {
        normalMin: 0.0, normalMax: 600.0,
        physMin: 0.0, physMax: 1500.0,
        unit: 'kg/ha',
        err: 'Nitrogen (N) must be between 0 and 1500 kg/ha.',
        warn: '⚠️ Extreme Condition: High Nitrogen Input — prediction allowed.'
    },
    'P': {
        normalMin: 0.0, normalMax: 300.0,
        physMin: 0.0, physMax: 800.0,
        unit: 'kg/ha',
        err: 'Phosphorus (P) must be between 0 and 800 kg/ha.',
        warn: '⚠️ Extreme Condition: High Phosphorus Input — prediction allowed.'
    },
    'K': {
        normalMin: 0.0, normalMax: 500.0,
        physMin: 0.0, physMax: 1200.0,
        unit: 'kg/ha',
        err: 'Potassium (K) must be between 0 and 1200 kg/ha.',
        warn: '⚠️ Extreme Condition: High Potassium Input — prediction allowed.'
    },
    'Fertilizer': {
        normalMin: 0.0, normalMax: 500.0,
        physMin: 0.0, physMax: 1500.0,
        unit: 'kg/ha',
        err: 'Fertilizer must be between 0 and 1500 kg/ha.',
        warn: '⚠️ Extreme Condition: High Fertilizer Application — prediction allowed.'
    },
    'Pesticide': {
        normalMin: 0.0, normalMax: 10.0,
        physMin: 0.0, physMax: 35.0,
        unit: 'kg/ha',
        err: 'Pesticide must be between 0.0 and 35.0 kg/ha.',
        warn: '⚠️ Extreme Condition: High Pesticide Application — prediction allowed.'
    },
    'Area': {
        normalMin: 1.0, normalMax: 350000.0,
        physMin: 0.1, physMax: 800000.0,
        unit: 'ha',
        err: 'Cultivated Area must be between 0.1 ha and 800,000 ha.',
        warn: '⚠️ Extreme Condition: Exceptional Cultivated Area — prediction allowed.'
    }
};

// Initialize App on DOM load
document.addEventListener('DOMContentLoaded', async () => {
    await fetchDistrictsAndSoils();
});

// Responsive Mobile Menu Drawer Toggle
function toggleMobileMenu() {
    const sidebar = document.getElementById('app-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
}

// Language Switcher
function setLanguage(lang) {
    currentLang = lang;
    document.getElementById('lang-en').classList.toggle('active', lang === 'en');
    document.getElementById('lang-ta').classList.toggle('active', lang === 'ta');

    document.querySelectorAll('[data-en]').forEach(el => {
        const text = el.getAttribute(`data-${lang}`);
        if (text) el.textContent = text;
    });

    if (lastManualResult) {
        renderManualPredictionResults(lastManualResult);
    }
    if (lastForecastResult) {
        renderForecastPredictionResults(lastForecastResult);
    }
    if (lastLiveResult) {
        renderLivePredictionResults(lastLiveResult);
    }
}

// Navigation Tab Switcher (Strict View Isolation)
function switchTab(tabId) {
    const sidebar = document.getElementById('app-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    }

    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));

    const navBtn = document.getElementById(`nav-${tabId}`);
    if (navBtn) navBtn.classList.add('active');

    const panel = document.getElementById(`panel-${tabId}`);
    if (panel) panel.classList.add('active');

    const titleEl = document.getElementById('page-title');
    const subtitleEl = document.getElementById('page-subtitle');

    hideValidationBanner();

    const titles = {
        'dashboard': { en: 'Dashboard', ta: 'முகப்பு', subEn: 'Explainable Agricultural Decision Support & Forecasting', subTa: 'விளக்கக்கூடிய விவசாய முடிவு ஆதரவு மற்றும் முன்கணிப்பு' },
        'live': { en: 'Live Satellite & Weather Yield Prediction', ta: 'நேரடி செயற்கைக்கோள் & வானிலை நெல் மகசூல் கணிப்பு', subEn: 'Select any of 30 Tamil Nadu districts to fetch live Sentinel-2 satellite passes from Copernicus and ECMWF ERA5-Land reanalysis from Open-Meteo across a 12-month lookback period.', subTa: '12 மாத கால இடைவெளியில் கோப்பர்நிகஸ் சென்டினல்-2 மற்றும் ஓபன்-மீட்டியோ வானிலை தரவுகளைப் பெற்று துல்லியமான நெல் மகசூலைக் கணக்கிடுங்கள்.' },
        'manual': { en: 'Rice Yield Prediction', ta: 'நெல் மகசூல் கணக்கீடு', subEn: 'Enter observed agricultural and environmental conditions to estimate annual rice yield.', subTa: 'ஆண்டு நெல் மகசூலைக் கணக்கிட அவதானிக்கப்பட்ட சூழ்நிலைகளை உள்ளிடவும்.' },
        'forecast': { en: 'Forecast Mode', ta: 'முன்கணிப்பு முறை', subEn: 'Estimate future environmental conditions and use them to predict rice yield.', subTa: 'எதிர்கால வானிலையைக் கணித்து நெல் மகசூலை மதிப்பிடவும்.' },
        'health': { en: 'Crop Health Advisor', ta: 'பயிர் ஆரோக்கிய ஆலோசகர்', subEn: 'Enter field observations to receive targeted agricultural guidance.', subTa: 'பூச்சி மற்றும் நோய் மேலாண்மை வழிகாட்டுதலைப் பெற உங்கள் வயல் நிலவரத்தை உள்ளிடவும்.' }
    };

    if (titles[tabId]) {
        titleEl.textContent = currentLang === 'ta' ? titles[tabId].ta : titles[tabId].en;
        subtitleEl.textContent = currentLang === 'ta' ? titles[tabId].subTa : titles[tabId].subEn;
    }
}

// Show/Hide Validation Banner
function showValidationBanner(msgEn, msgTa, type = 'err') {
    const banner = document.getElementById('validation-banner');
    const textEl = document.getElementById('val-msg-text');
    textEl.setAttribute('data-en', msgEn);
    textEl.setAttribute('data-ta', msgTa);
    textEl.textContent = currentLang === 'ta' ? msgTa : msgEn;

    banner.classList.remove('hidden', 'banner-err', 'banner-warn');
    if (type === 'warn') {
        banner.classList.add('banner-warn');
    } else {
        banner.classList.add('banner-err');
    }
}

function hideValidationBanner() {
    const banner = document.getElementById('validation-banner');
    banner.classList.add('hidden');
}

// Fetch Districts & Soil Types
async function fetchDistrictsAndSoils() {
    try {
        const res = await fetch(`${API_BASE}/api/districts`);
        const data = await res.json();

        const distSelect = document.getElementById('input-district');
        const fcDistSelect = document.getElementById('forecast-district');
        const liveDistSelect = document.getElementById('live-district-select');
        const soilSelect = document.getElementById('Soil_Type');

        distSelect.innerHTML = '<option value="" disabled selected>-- Select District --</option>';
        fcDistSelect.innerHTML = '<option value="" disabled selected>-- Select District --</option>';
        soilSelect.innerHTML = '<option value="" disabled selected>-- Select Soil Type --</option>';

        // Manual Prediction & Forecast dropdowns: ALL 30 districts (UNCHANGED)
        data.districts.forEach(d => {
            distSelect.add(new Option(d, d));
            fcDistSelect.add(new Option(d, d));
        });

        // Satellite Prediction dropdown: EXACTLY the 5 pilot districts
        const pilotDistricts = ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"];
        if (liveDistSelect) {
            liveDistSelect.innerHTML = '<option value="" disabled selected>-- Select Pilot District --</option>';
            pilotDistricts.forEach(d => {
                liveDistSelect.add(new Option(d, d));
            });
        }

        data.soil_types.forEach(s => {
            soilSelect.add(new Option(s, s));
        });
    } catch (err) {
        console.error("Error fetching districts:", err);
    }
}

function formatValWithUnit(feat, val) {
    if (val === undefined || val === null || isNaN(val)) return '--';
    const num = Number(val);
    if (feat.includes('Temperature')) return `${num.toFixed(1)} °C`;
    if (feat.includes('Rainfall')) return `${num.toFixed(1)} mm`;
    if (feat.includes('Humidity')) return `${num.toFixed(1)} %`;
    if (feat.includes('Wind_Speed')) return `${num.toFixed(1)} m/s`;
    if (feat.includes('Soil_Moisture')) return `${num.toFixed(2)}`;
    if (feat === 'Soil_PH') return `${num.toFixed(1)}`;
    if (['N', 'P', 'K'].includes(feat)) return `${Math.round(num)}`;
    if (feat === 'Fertilizer') return `${num.toFixed(1)} kg/ha`;
    if (feat === 'Pesticide') return `${num.toFixed(1)} kg/ha`;
    if (feat === 'Area') return `${Math.round(num).toLocaleString()} ha`;
    return `${num.toFixed(1)}`;
}

function formatRefText(feat, p25, p75) {
    const minStr = formatValWithUnit(feat, p25);
    const maxStr = formatValWithUnit(feat, p75);
    if (minStr === maxStr) return `Ref: ${minStr}`;
    const unitMatch = minStr.match(/ [a-zA-Z°%]+(\/ha)?$/);
    if (unitMatch) {
        const unit = unitMatch[0];
        const v1 = minStr.replace(unit, '');
        const v2 = maxStr.replace(unit, '');
        return `Ref: ${v1} – ${v2}${unit}`;
    }
    return `Ref: ${minStr} – ${maxStr}`;
}

function getFeatureBoundKey(featId) {
    for (const k of Object.keys(DOMAIN_VALIDATION_BOUNDS)) {
        if (featId.includes(k)) return k;
    }
    return null;
}

// 3-State Domain Validation System
// State 1: Normal (No warning)
// State 2: Extreme Condition (⚠️ Warning, prediction ALLOWED)
// State 3: Clearly Invalid (❌ Error, prediction BLOCKED)
function validateManualInputs() {
    const featureIds = [
        'Kharif Temperature', 'Kharif Rainfall', 'Kharif Humidity', 'Kharif Wind_Speed', 'Kharif Soil_Moisture',
        'Rabi Temperature', 'Rabi Rainfall', 'Rabi Humidity', 'Rabi Wind_Speed', 'Rabi Soil_Moisture',
        'Zaid Temperature', 'Zaid Rainfall', 'Zaid Humidity', 'Zaid Wind_Speed', 'Zaid Soil_Moisture',
        'Soil_PH', 'N', 'P', 'K', 'Fertilizer', 'Pesticide', 'Area'
    ];

    let invalidCount = 0;
    let unusualCount = 0;
    const invalidMessages = [];
    const unusualMessages = [];

    featureIds.forEach(id => {
        const el = document.getElementById(id);
        const msgEl = document.getElementById(`msg-${id}`);
        if (!el || !msgEl) return;

        el.classList.remove('input-warn', 'input-err');
        msgEl.className = 'input-validation-msg';
        msgEl.textContent = '';

        const rawVal = el.value.trim();
        if (rawVal === '') return;

        const val = parseFloat(rawVal);
        const boundKey = getFeatureBoundKey(id);
        const bound = boundKey ? DOMAIN_VALIDATION_BOUNDS[boundKey] : null;

        if (isNaN(val)) {
            invalidCount++;
            el.classList.add('input-err');
            msgEl.className = 'input-validation-msg val-err';
            msgEl.textContent = `❌ Invalid Entry: Please enter a valid number.`;
            invalidMessages.push(`${id}: Not a number`);
            return;
        }

        if (bound) {
            // STATE 3: CLEARLY INVALID ENTRY (Typing mistake / Extra Zeroes) -> BLOCKED
            if (val < bound.physMin || val > bound.physMax) {
                invalidCount++;
                el.classList.add('input-err');
                msgEl.className = 'input-validation-msg val-err';
                msgEl.textContent = `❌ Invalid Entry: ${bound.err}`;
                invalidMessages.push(`${id} (${val}) is physically impossible.`);
                return;
            }

            // STATE 2: EXTREME CONDITION (Genuinely extreme weather/inputs) -> WARNING ALLOWED
            if (val < bound.normalMin || val > bound.normalMax) {
                unusualCount++;
                el.classList.add('input-warn');
                msgEl.className = 'input-validation-msg val-warn';
                msgEl.textContent = bound.warn;
                unusualMessages.push(`${id}: ${val} (Extreme Condition)`);
                return;
            }

            // STATE 1: NORMAL REALISTIC VALUE -> NO WARNING!
        }
    });

    return { invalidCount, unusualCount, invalidMessages, unusualMessages };
}

// Handle District & Target Year Selection Change in Manual Prediction Mode
// Per requirement: DO NOT automatically populate inputs from historical Excel dataset
async function handleManualDistrictYearChange() {
    const dist = document.getElementById('input-district').value;
    if (!dist) return;

    // Fetch historical reference ranges for selected district (Displayed as Reference Info ONLY)
    try {
        const resStats = await fetch(`${API_BASE}/api/historical-ranges?district=${encodeURIComponent(dist)}`);
        const dataStats = await resStats.json();
        currentDistrictStats = dataStats.feature_statistics;

        for (const [feat, stats] of Object.entries(currentDistrictStats)) {
            const refEl = document.getElementById(`ref-${feat}`);
            if (refEl) {
                refEl.textContent = formatRefText(feat, stats.p25, stats.p75);
            }
        }
    } catch (err) {
        console.error("Error fetching historical ranges:", err);
    }

    const statusEl = document.getElementById('manual-load-status');
    if (statusEl) {
        statusEl.textContent = `Historical baseline loaded for ${dist}. Click 'Load Historical Dataset Record' to auto-fill inputs if desired.`;
    }
}

// Explicit button action: User clicks "Load Historical Dataset Record" to populate inputs
async function loadHistoricalDatasetRecord() {
    const dist = document.getElementById('input-district').value;
    const yr = document.getElementById('input-year').value;

    if (!dist) {
        alert("Please select a District first.");
        return;
    }
    if (!yr) {
        alert("Please select a Target Year first.");
        return;
    }

    try {
        const resParams = await fetch(`${API_BASE}/api/district-year-params?district=${encodeURIComponent(dist)}&year=${yr}`);
        if (!resParams.ok) {
            alert(`No historical dataset record found for ${dist} (${yr}).`);
            return;
        }

        const dataParams = await resParams.json();
        const params = dataParams.params;
        const sourceType = dataParams.source_type;

        // Update climate source badge indicator
        const badgeEl = document.getElementById('climate-source-badge');
        if (badgeEl) {
            badgeEl.textContent = `${sourceType} (${yr})`;
            badgeEl.style.backgroundColor = sourceType === 'Forecasted Value' ? '#eff6ff' : '#e8f5e9';
            badgeEl.style.color = sourceType === 'Forecasted Value' ? '#1d4ed8' : '#2d6a4f';
        }

        // Auto-populate all 15 seasonal climate parameters + soil/farm inputs
        const featureIds = [
            'Kharif Temperature', 'Kharif Rainfall', 'Kharif Humidity', 'Kharif Wind_Speed', 'Kharif Soil_Moisture',
            'Rabi Temperature', 'Rabi Rainfall', 'Rabi Humidity', 'Rabi Wind_Speed', 'Rabi Soil_Moisture',
            'Zaid Temperature', 'Zaid Rainfall', 'Zaid Humidity', 'Zaid Wind_Speed', 'Zaid Soil_Moisture',
            'Soil_PH', 'N', 'P', 'K', 'Fertilizer', 'Pesticide', 'Area'
        ];

        featureIds.forEach(id => {
            const el = document.getElementById(id);
            if (el && params[id] !== undefined && params[id] !== null) {
                if (typeof params[id] === 'number') {
                    if (id.includes('Moisture') || id === 'Pesticide' || id === 'Soil_PH') {
                        el.value = Number(params[id]).toFixed(2);
                    } else if (id.includes('Temperature') || id.includes('Rainfall') || id.includes('Humidity') || id.includes('Wind_Speed')) {
                        el.value = Number(params[id]).toFixed(1);
                    } else {
                        el.value = Math.round(Number(params[id]));
                    }
                } else {
                    el.value = params[id];
                }
            }
        });

        if (params['Soil_Type']) {
            const soilEl = document.getElementById('Soil_Type');
            if (soilEl) soilEl.value = params['Soil_Type'];
        }

        const statusEl = document.getElementById('manual-load-status');
        if (statusEl) {
            statusEl.textContent = `✅ Successfully loaded historical dataset record for ${dist} (${yr}).`;
        }

        validateManualInputs();
    } catch (err) {
        console.error("Error loading historical record:", err);
        alert("Failed to load historical record: " + err.message);
    }
}

const handleDistrictChange = handleManualDistrictYearChange;

// Manual Form Submission with Domain Validation
async function handleManualSubmit(e) {
    e.preventDefault();
    hideValidationBanner();

    const district = document.getElementById('input-district').value;
    const yearVal = document.getElementById('input-year').value;
    const soilType = document.getElementById('Soil_Type').value;

    const featureIds = [
        'Kharif Temperature', 'Kharif Rainfall', 'Kharif Humidity', 'Kharif Wind_Speed', 'Kharif Soil_Moisture',
        'Rabi Temperature', 'Rabi Rainfall', 'Rabi Humidity', 'Rabi Wind_Speed', 'Rabi Soil_Moisture',
        'Zaid Temperature', 'Zaid Rainfall', 'Zaid Humidity', 'Zaid Wind_Speed', 'Zaid Soil_Moisture',
        'Soil_PH', 'N', 'P', 'K', 'Fertilizer', 'Pesticide', 'Area'
    ];

    const missingFields = [];
    if (!district) missingFields.push('District');
    if (!yearVal) missingFields.push('Target Year');
    if (!soilType) missingFields.push('Soil Type');

    // Run domain validation
    const valResult = validateManualInputs();

    // If ANY physically invalid entries exist (STATE 3), BLOCK PREDICTION!
    if (valResult.invalidCount > 0) {
        showValidationBanner(
            `❌ Invalid Entry Detected (${valResult.invalidCount} field(s)). Please correct the highlighted entries before predicting.`,
            `❌ தவறான உள்ளீடு கண்டறியப்பட்டது (${valResult.invalidCount} புலம்). கணிப்பதற்கு முன் சரிசெய்யவும்.`,
            'err'
        );
        document.getElementById('manual-yield-output-section').classList.add('hidden');
        document.getElementById('manual-empty-state').classList.remove('hidden');
        return;
    }

    // If ONLY extreme conditions exist (STATE 2), SHOW WARNING SUMMARY BUT ALLOW PREDICTION!
    if (valResult.unusualCount > 0) {
        showValidationBanner(
            `⚠️ ${valResult.unusualCount} extreme condition(s) detected — values are usable for prediction.`,
            `⚠️ ${valResult.unusualCount} தீவிர சூழ்நிலைகள் கண்டறியப்பட்டன — மதிப்புகள் கணிப்புக்கு பயன்படுத்தக்கூடியவை.`,
            'warn'
        );
    } else {
        hideValidationBanner();
    }

    const payload = {
        District: district,
        Year: parseInt(yearVal) || null,
        Soil_Type: soilType
    };

    featureIds.forEach(id => {
        const el = document.getElementById(id);
        if (!el || el.value === "" || el.value === null) {
            missingFields.push(id);
        } else {
            const val = parseFloat(el.value);
            if (isNaN(val)) missingFields.push(id);
            else payload[id] = val;
        }
    });

    if (missingFields.length > 0) {
        showValidationBanner(
            "Please enter all required values before predicting.",
            "தயவுசெய்து கணிப்பதற்கு முன் தேவையான அனைத்து மதிப்புகளையும் உள்ளிடவும்.",
            'err'
        );
        document.getElementById('manual-yield-output-section').classList.add('hidden');
        document.getElementById('manual-empty-state').classList.remove('hidden');
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/predict-yield`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Validation Error");
        }

        const result = await res.json();
        lastManualResult = result;
        renderManualPredictionResults(result);

        document.getElementById('manual-empty-state').classList.add('hidden');
        document.getElementById('manual-yield-output-section').classList.remove('hidden');
    } catch (err) {
        showValidationBanner(
            `Validation Error: ${err.message}`,
            `சரிபார்ப்பு பிழை: ${err.message}`,
            'err'
        );
        document.getElementById('manual-yield-output-section').classList.add('hidden');
        document.getElementById('manual-empty-state').classList.remove('hidden');
    }
}

// Forecast Form Submission
async function handleForecastSubmit(e) {
    e.preventDefault();
    hideValidationBanner();

    const district = document.getElementById('forecast-district').value;
    const target_year = parseInt(document.getElementById('forecast-year').value);
    const method = document.getElementById('forecast-method').value;

    if (!district || !target_year || !method) {
        showValidationBanner(
            "Please select a district and future year before generating forecast.",
            "முன்கணிப்பை உருவாக்குவதற்கு முன் மாவட்டம் மற்றும் எதிர்கால ஆண்டைத் தேர்ந்தெடுக்கவும்.",
            'err'
        );
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/forecast`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ district, target_year, method })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Server error");
        }

        const result = await res.json();
        lastForecastResult = result;
        renderForecastPredictionResults(result);

        document.getElementById('forecast-empty-state').classList.add('hidden');
        document.getElementById('forecast-yield-output-section').classList.remove('hidden');
    } catch (err) {
        showValidationBanner(
            `Forecast Error: ${err.message}`,
            `முன்கணிப்பு பிழை: ${err.message}`,
            'err'
        );
    }
}

// Crop Health Form Submission
async function handleHealthSubmit(e) {
    e.preventDefault();
    const payload = {
        growth_stage: document.getElementById('health-stage').value,
        leaf_condition: document.getElementById('health-leaf').value,
        water_status: document.getElementById('health-water').value,
        pest_obs: document.getElementById('health-pest').value,
        disease_obs: document.getElementById('health-disease').value
    };

    try {
        const res = await fetch(`${API_BASE}/api/crop-health`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();

        const advisoryBox = document.getElementById('crop-health-advisory-box');
        const advisoryList = document.getElementById('health-advisory-list');
        advisoryList.innerHTML = '';

        const list = currentLang === 'ta' ? result.advisories_ta : result.advisories_en;
        list.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            advisoryList.appendChild(li);
        });

        advisoryBox.classList.remove('hidden');
    } catch (err) {
        alert("Crop Health API Error: " + err.message);
    }
}

// On-Demand Toggles for SHAP & Insights
function toggleShapView(mode) {
    if (mode === 'manual') {
        showManualShap = !showManualShap;
        const panel = document.getElementById('manual-shap-panel');
        const btn = document.getElementById('btn-manual-shap');
        panel.classList.toggle('hidden', !showManualShap);
        btn.classList.toggle('active', showManualShap);
    } else {
        showForecastShap = !showForecastShap;
        const panel = document.getElementById('forecast-shap-panel');
        const btn = document.getElementById('btn-forecast-shap');
        panel.classList.toggle('hidden', !showForecastShap);
        btn.classList.toggle('active', showForecastShap);
    }
}

function toggleHistoricalInsights(mode) {
    if (mode === 'manual') {
        showManualInsights = !showManualInsights;
        const panel = document.getElementById('manual-insights-panel');
        const btn = document.getElementById('btn-manual-insights');
        panel.classList.toggle('hidden', !showManualInsights);
        btn.classList.toggle('active', showManualInsights);
    } else {
        showForecastInsights = !showForecastInsights;
        const panel = document.getElementById('forecast-insights-panel');
        const btn = document.getElementById('btn-forecast-insights');
        panel.classList.toggle('hidden', !showForecastInsights);
        btn.classList.toggle('active', showForecastInsights);
    }
}

// Render Manual Prediction Results
function renderManualPredictionResults(data) {
    document.getElementById('manual-res-yield').textContent = Number(data.predicted_yield).toFixed(2);
    document.getElementById('manual-res-district').textContent = data.district || "--";
    document.getElementById('manual-res-hist-avg').textContent = data.historical_district_avg_yield ? Number(data.historical_district_avg_yield).toFixed(2) : "--";

    // SHAP Positive
    const posList = document.getElementById('manual-shap-positive-list');
    posList.innerHTML = '';
    if (data.shap_explanation && data.shap_explanation.top_positive && data.shap_explanation.top_positive.length > 0) {
        data.shap_explanation.top_positive.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${item.feature}</span> <strong style="color: #166534">+${item.shap_value}</strong>`;
            posList.appendChild(li);
        });
    } else {
        posList.innerHTML = '<li>No positive feature contributions.</li>';
    }

    // SHAP Negative
    const negList = document.getElementById('manual-shap-negative-list');
    negList.innerHTML = '';
    if (data.shap_explanation && data.shap_explanation.top_negative && data.shap_explanation.top_negative.length > 0) {
        data.shap_explanation.top_negative.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${item.feature}</span> <strong style="color: #991b1b">${item.shap_value}</strong>`;
            negList.appendChild(li);
        });
    } else {
        negList.innerHTML = '<li>No negative feature contributions.</li>';
    }

    // Insights Grid
    const insightsContainer = document.getElementById('manual-insights-list');
    insightsContainer.innerHTML = '';
    if (data.historical_insights && data.historical_insights.length > 0) {
        data.historical_insights.forEach(ins => {
            const card = document.createElement('div');
            const statusClass = ins.status ? ins.status.toLowerCase().replace(/ /g, '-') : 'within-typical-range';
            card.className = `insight-card ${statusClass}`;

            const statusText = currentLang === 'ta' ? (ins.status_ta || ins.status) : ins.status;
            const msgText = currentLang === 'ta' ? (ins.insight_ta || ins.insight_en) : ins.insight_en;

            card.innerHTML = `
                <div class="insight-header">
                    <span>${ins.feature} (${ins.user_value})</span>
                    <span class="status-tag">${statusText}</span>
                </div>
                <div>${msgText}</div>
            `;
            insightsContainer.appendChild(card);
        });
    }

    // Suggestions List
    const suggCard = document.getElementById('manual-suggestions-card');
    const suggestionsList = document.getElementById('manual-suggestions-list');
    suggestionsList.innerHTML = '';
    const suggs = currentLang === 'ta' ? (data.suggestions_ta || data.suggestions_en) : data.suggestions_en;
    if (suggs && suggs.length > 0) {
        suggs.forEach(sugg => {
            const li = document.createElement('li');
            li.textContent = sugg;
            suggestionsList.appendChild(li);
        });
        suggCard.classList.remove('hidden');
    } else {
        suggCard.classList.add('hidden');
    }
}

// Render Forecast Results
function renderForecastPredictionResults(data) {
    document.getElementById('forecast-res-badge').textContent = data.mode || "Forecast Mode";
    document.getElementById('forecast-res-yield').textContent = Number(data.predicted_yield).toFixed(2);
    document.getElementById('forecast-res-district').textContent = data.district || "--";
    document.getElementById('forecast-res-hist-avg').textContent = data.historical_district_avg_yield ? Number(data.historical_district_avg_yield).toFixed(2) : "--";

    // 3 Independent Methods Grid
    const comparisonGrid = document.getElementById('forecast-methods-comparison-grid');
    comparisonGrid.innerHTML = '';

    if (data.all_methods_forecasts) {
        const methodsOrder = [
            { name: 'Exponential Smoothing', label: 'Exponential Smoothing (alpha=0.3)' },
            { name: '5-Year Moving Average', label: '5-Year Moving Average' },
            { name: 'Linear Trend', label: 'Linear Trend Model' }
        ];

        methodsOrder.forEach(m => {
            const fcData = data.all_methods_forecasts[m.name] || data.all_methods_forecasts[m.label];
            if (!fcData) return;

            const isSelected = data.selected_method && (data.selected_method === m.name || data.selected_method === m.label || (data.selected_method.includes('Exponential') && m.name.includes('Exponential')) || (data.selected_method.includes('Moving') && m.name.includes('Moving')) || (data.selected_method.includes('Linear') && m.name.includes('Linear')));

            const card = document.createElement('div');
            card.className = `method-card ${isSelected ? 'selected' : ''}`;

            let itemsHtml = '';
            const displayKeys = ['Kharif Temperature', 'Kharif Rainfall', 'Rabi Temperature', 'Rabi Rainfall', 'Zaid Temperature', 'Zaid Rainfall', 'Fertilizer', 'Area'];
            displayKeys.forEach(k => {
                if (fcData[k] !== undefined) {
                    itemsHtml += `<div style="font-size:0.8rem; color:var(--text-muted); display:flex; justify-content:space-between; margin-bottom:4px">
                        <span>${k}:</span> <strong style="color:var(--text-primary)">${formatValWithUnit(k, fcData[k])}</strong>
                    </div>`;
                }
            });

            card.innerHTML = `
                <div class="method-card-header">
                    <h4>${m.label}</h4>
                    <span class="${isSelected ? 'active-method-tag' : 'passive-method-tag'}">
                        ${isSelected ? 'Used for Yield Estimation' : 'Calculated'}
                    </span>
                </div>
                <div>${itemsHtml}</div>
            `;
            comparisonGrid.appendChild(card);
        });
    }

    // SHAP Positive
    const posList = document.getElementById('forecast-shap-positive-list');
    posList.innerHTML = '';
    if (data.shap_explanation && data.shap_explanation.top_positive && data.shap_explanation.top_positive.length > 0) {
        data.shap_explanation.top_positive.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${item.feature}</span> <strong style="color: #166534">+${item.shap_value}</strong>`;
            posList.appendChild(li);
        });
    } else {
        posList.innerHTML = '<li>No positive feature contributions.</li>';
    }

    // SHAP Negative
    const negList = document.getElementById('forecast-shap-negative-list');
    negList.innerHTML = '';
    if (data.shap_explanation && data.shap_explanation.top_negative && data.shap_explanation.top_negative.length > 0) {
        data.shap_explanation.top_negative.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${item.feature}</span> <strong style="color: #991b1b">${item.shap_value}</strong>`;
            negList.appendChild(li);
        });
    } else {
        negList.innerHTML = '<li>No negative feature contributions.</li>';
    }

    // Insights List
    const insightsContainer = document.getElementById('forecast-insights-list');
    insightsContainer.innerHTML = '';
    if (data.historical_insights && data.historical_insights.length > 0) {
        data.historical_insights.forEach(ins => {
            const card = document.createElement('div');
            const statusClass = ins.status ? ins.status.toLowerCase().replace(/ /g, '-') : 'within-typical-range';
            card.className = `insight-card ${statusClass}`;

            const statusText = currentLang === 'ta' ? (ins.status_ta || ins.status) : ins.status;
            const msgText = currentLang === 'ta' ? (ins.insight_ta || ins.insight_en) : ins.insight_en;

            card.innerHTML = `
                <div class="insight-header">
                    <span>${ins.feature} (${ins.user_value})</span>
                    <span class="status-tag">${statusText}</span>
                </div>
                <div>${msgText}</div>
            `;
            insightsContainer.appendChild(card);
        });
    }

    // Suggestions List
    const suggCard = document.getElementById('forecast-suggestions-card');
    const suggestionsList = document.getElementById('forecast-suggestions-list');
    suggestionsList.innerHTML = '';
    const suggs = currentLang === 'ta' ? (data.suggestions_ta || data.suggestions_en) : data.suggestions_en;
    if (suggs && suggs.length > 0) {
        suggs.forEach(sugg => {
            const li = document.createElement('li');
            li.textContent = sugg;
            suggestionsList.appendChild(li);
        });
        suggCard.classList.remove('hidden');
    } else {
        suggCard.classList.add('hidden');
    }
}

// Tamil Speech Synthesis (TTS)
function speakTamilExplanation(mode) {
    if (!('speechSynthesis' in window)) {
        alert("Text-to-Speech is not supported in this browser.");
        return;
    }

    const data = mode === 'manual' ? lastManualResult : lastForecastResult;

    if (!data) {
        alert("Please run a yield prediction first!");
        return;
    }

    window.speechSynthesis.cancel();

    const district = data.district;
    const yieldVal = data.predicted_yield;

    let text = `${district} மாவட்டத்திற்கான கணக்கிடப்பட்ட நெல் மகசூல் எக்டேருக்கு ${yieldVal} டன்கள் ஆகும். `;

    if (data.suggestions_ta && data.suggestions_ta.length > 0) {
        text += "விவசாய ஆலோசனை: " + data.suggestions_ta[0];
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ta-IN';
    utterance.rate = 0.9;

    const voices = window.speechSynthesis.getVoices();
    const taVoice = voices.find(v => v.lang.includes('ta'));
    if (taVoice) utterance.voice = taVoice;

    window.speechSynthesis.speak(utterance);
}

// ==========================================================================
// LIVE SATELLITE & WEATHER PREDICTION HANDLERS
// ==========================================================================

async function handleLiveDistrictChange() {
    const dist = document.getElementById('live-district-select').value;
    const refDate = document.getElementById('live-ref-date').value || new Date().toISOString().slice(0, 10);
    if (!dist) return;

    const dRef = new Date(refDate);
    const dStart = new Date(dRef);
    dStart.setFullYear(dStart.getFullYear() - 1);
    const windowStr = `${dStart.toISOString().slice(0, 10)} to ${refDate}`;

    document.getElementById('live-status-district').textContent = dist;
    document.getElementById('live-status-window').textContent = `${windowStr} (365 Days)`;

    const badge = document.getElementById('live-status-badge');
    badge.className = 'badge-status-neutral';
    badge.textContent = 'Ready to fetch observations';

    try {
        const res = await fetch(`${API_BASE}/api/district-profile?district=${encodeURIComponent(dist)}`);
        if (res.ok) {
            const p = await res.json();
            document.getElementById('live-status-zone').textContent = p.agro_climatic_zone || '--';
            document.getElementById('live-status-coords').textContent = `[${p.centroid.latitude.toFixed(4)}°N, ${p.centroid.longitude.toFixed(4)}°E]`;
            document.getElementById('live-status-tile').textContent = p.primary_sentinel2_tile || '--';
        }
    } catch (e) {
        console.error("Error fetching district profile:", e);
    }
}

async function handleLivePredictSubmit() {
    hideValidationBanner();
    const dist = document.getElementById('live-district-select').value;

    if (!dist) {
        showValidationBanner(
            "Please select a pilot district to proceed with live satellite data retrieval.",
            "செயற்கைக்கோள் தரவைப் பெற தயவுசெய்து ஒரு விமான சோதனை மாவட்டத்தைத் தேர்ந்தெடுக்கவும்.",
            'err'
        );
        return;
    }

    const progressCard = document.getElementById('live-progress-card');
    const resultsContainer = document.getElementById('live-results-container');
    const badge = document.getElementById('live-status-badge');
    const btn = document.getElementById('btn-live-predict');

    // UI loading state
    btn.disabled = true;
    progressCard.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    badge.className = 'badge-status-loading';
    badge.textContent = 'Querying Copernicus CDSE & processing raster pixels...';

    // Animate progress steps
    const steps = ['pstep-1', 'pstep-2', 'pstep-3', 'pstep-4', 'pstep-5'];
    steps.forEach((s, idx) => {
        const el = document.getElementById(s);
        if (el) {
            el.className = idx === 0 ? 'pstep active' : 'pstep';
        }
    });

    let stepTimer = 1;
    const stepInterval = setInterval(() => {
        if (stepTimer < steps.length) {
            const prev = document.getElementById(steps[stepTimer - 1]);
            const cur = document.getElementById(steps[stepTimer]);
            if (prev) prev.className = 'pstep completed';
            if (cur) cur.className = 'pstep active';
            stepTimer++;
        }
    }, 1000);

    try {
        const payload = {
            district: dist
        };

        const res = await fetch(`${API_BASE}/api/satellite-predict-live`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        clearInterval(stepInterval);
        steps.forEach(s => {
            const el = document.getElementById(s);
            if (el) el.className = 'pstep completed';
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `Server returned error status ${res.status}`);
        }

        const data = await res.json();

        lastLiveResult = data;
        renderLivePredictionResults(data);

        badge.className = 'badge-status-success';
        badge.textContent = `Completed (${data.retrieval_status} | ${data.cache_status})`;

        progressCard.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        // Smooth scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
        clearInterval(stepInterval);
        progressCard.classList.add('hidden');
        badge.className = 'badge-status-error';
        badge.textContent = 'Retrieval failed';
        showValidationBanner(
            `Live Satellite Retrieval Failed: ${err.message}`,
            `நேரடி செயற்கைக்கோள் தரவு மீட்பு தோல்வியடைந்தது: ${err.message}`,
            'err'
        );
    } finally {
        btn.disabled = false;
    }
}

function renderLivePredictionResults(data) {
    if (!data) return;

    // 1. Hero Result Card
    document.getElementById('live-res-district-title').textContent = data.district;
    const yVal = data.predicted_yield_t_ha !== undefined ? Number(data.predicted_yield_t_ha) : Number(data.predicted_yield || 0);
    document.getElementById('live-yield-val').textContent = yVal.toFixed(2);

    // kg / acre conversion: 1 tonne = 1000 kg, 1 hectare = 2.47105 acres
    const kgPerAcre = Math.round(yVal * 1000 / 2.47105);
    document.getElementById('live-yield-kg-acre').textContent = `≈ ${kgPerAcre.toLocaleString()} kg / acre`;

    const baseAvg = (data.baseline_yield_t_ha !== undefined) ? Number(data.baseline_yield_t_ha).toFixed(2) : (data.historical_district_avg_yield ? Number(data.historical_district_avg_yield).toFixed(2) : '3.53');
    document.getElementById('live-baseline-comp-badge').textContent = `District Baseline: ${baseAvg} t/ha | Model: ${data.model_name || 'Extra Trees'}`;

    // 2. Copernicus Satellite Observation Provenance
    const veg = (data.vegetation_indices && data.vegetation_indices.ndvi) ? data.vegetation_indices : (data.satellite_data ? data.satellite_data.vegetation_indices : {});
    const cacheLabel = data.cache_status === 'live_streamed_cdse'
        ? 'Copernicus CDSE (Live Streamed BOA)'
        : (data.cache_status ? `Verified Level-2A Cache (${data.cache_status})` : 'Copernicus CDSE');

    document.getElementById('live-sat-source-tag').textContent = cacheLabel;
    document.getElementById('live-sat-tile-val').textContent = data.tile ? `Tile ${data.tile} (S2 Level-2A BOA)` : (data.coordinates ? `BBox: [${data.coordinates.join(', ')}]` : '--');

    const usableDate = data.latest_usable_date || (data.acquisition_dates ? data.acquisition_dates[0] : '--');
    const catDate = data.latest_catalogue_date || (data.acquisition_dates && data.acquisition_dates.length > 1 ? data.acquisition_dates[1] : usableDate);
    document.getElementById('live-sat-window-val').textContent = `Sensed: ${usableDate} (Latest Discovery: ${catDate})`;

    document.getElementById('live-sat-obs-count').textContent = `${data.observation_count || 1} recent CDSE products discovered`;

    const cloudPct = veg.cloud_invalid_pct !== undefined ? veg.cloud_invalid_pct : (data.satellite_data && data.satellite_data.cloud_filtering ? data.satellite_data.cloud_filtering.mean_cloud_cover_pct : 0.0);
    document.getElementById('live-sat-cloud-val').textContent = `${cloudPct}% cloud/invalid pixels`;
    document.getElementById('live-sat-season-val').textContent = data.season || (data.satellite_data ? data.satellite_data.dominant_season : '--');

    // Multi-spectral vegetation indicators
    const ndviMean = veg.ndvi ? veg.ndvi.mean : (veg.ndvi_mean !== undefined ? veg.ndvi_mean : null);
    const ndviMed = veg.ndvi ? veg.ndvi.median : (veg.ndvi_max !== undefined ? veg.ndvi_max : null);
    const ndreMean = veg.ndre ? veg.ndre.mean : (veg.ndre_mean !== undefined ? veg.ndre_mean : null);
    const eviMean = veg.evi ? veg.evi.mean : null;
    const ndwiMean = veg.ndwi ? veg.ndwi.mean : null;
    const validPx = veg.valid_pixels !== undefined ? veg.valid_pixels : null;

    document.getElementById('live-veg-ndvi-mean').textContent = ndviMean !== null ? Number(ndviMean).toFixed(3) : '--';
    document.getElementById('live-veg-ndvi-max').textContent = ndviMed !== null ? Number(ndviMed).toFixed(3) : '--';
    document.getElementById('live-veg-ndre-mean').textContent = ndreMean !== null ? Number(ndreMean).toFixed(3) : 'N/A (10m bands)';

    const elEvi = document.getElementById('live-veg-evi-mean');
    if (elEvi) elEvi.textContent = eviMean !== null ? Number(eviMean).toFixed(3) : '--';

    const elNdwi = document.getElementById('live-veg-ndwi-mean');
    if (elNdwi) elNdwi.textContent = ndwiMean !== null ? Number(ndwiMean).toFixed(3) : '--';

    const elValidPx = document.getElementById('live-veg-valid-px');
    if (elValidPx) elValidPx.textContent = validPx !== null ? Number(validPx).toLocaleString() : '--';

    // Data sufficiency & model notice
    const suffText = document.getElementById('live-data-sufficiency-text');
    if (suffText && data.data_sufficiency) {
        suffText.textContent = data.data_sufficiency.details || data.data_sufficiency.status || '--';
    }
    const modelText = document.getElementById('live-model-name-text');
    if (modelText) {
        modelText.textContent = `Model: ${data.model_name || 'Tuned Extra Trees Regressor + Sentinel-2 Level-2A Canopy Calibration'}`;
    }

    // Meteorological Observations (if returned or fallback)
    const wx = data.weather_data || {};
    const annual = wx.annual_summary || {};
    const seasonal = wx.seasonal_breakdown || {};

    const wxTag = document.getElementById('live-weather-source-tag');
    if (wxTag) wxTag.textContent = wx.source ? (wx.is_cached ? `${wx.source} (Cached)` : `${wx.source} (Live)`) : 'ECMWF ERA5-Land Baseline';
    const totRain = document.getElementById('live-wx-tot-rain');
    if (totRain) totRain.textContent = annual.total_rainfall_mm !== undefined ? `${annual.total_rainfall_mm.toFixed(1)} mm` : '850.0 mm';
    const meanTemp = document.getElementById('live-wx-mean-temp');
    if (meanTemp) meanTemp.textContent = annual.mean_temperature_c !== undefined ? `${annual.mean_temperature_c.toFixed(1)} °C` : '28.5 °C';
    const meanHum = document.getElementById('live-wx-mean-humidity');
    if (meanHum) meanHum.textContent = annual.mean_humidity_pct !== undefined ? `${annual.mean_humidity_pct.toFixed(1)} %` : '74.0 %';
    const soilM = document.getElementById('live-wx-soil-m');
    if (soilM) soilM.textContent = annual.mean_soil_moisture !== undefined ? `${annual.mean_soil_moisture.toFixed(2)}` : '0.27';

    // Seasonal Breakdown Table
    const tableBody = document.getElementById('live-seasonal-table-body');
    if (tableBody) {
        tableBody.innerHTML = '';
        const seasonRows = [
            { name: 'Kharif (Jun–Sep)', key: 'kharif' },
            { name: 'Rabi (Oct–Feb)', key: 'rabi' },
            { name: 'Zaid (Mar–May)', key: 'zaid' }
        ];

        seasonRows.forEach(sr => {
            const sData = seasonal[sr.key];
            if (!sData) return;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${sr.name}</strong></td>
                <td><strong>${sData.total_rainfall_mm.toFixed(1)} mm</strong></td>
                <td>${sData.mean_monthly_rainfall_mm.toFixed(1)} mm/mo</td>
                <td>${sData.mean_temperature_c.toFixed(1)} °C</td>
                <td>${sData.mean_humidity_pct.toFixed(1)} %</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // 4. SHAP Waterfall Decomposition
    const shap = data.shap_explanation || {};
    const shapBase = document.getElementById('live-shap-base-val');
    if (shapBase) shapBase.textContent = `${Number(shap.base_value || 3.53).toFixed(2)} t/ha`;

    const posList = document.getElementById('live-shap-positive-list');
    posList.innerHTML = '';
    if (shap.top_positive && shap.top_positive.length > 0) {
        shap.top_positive.forEach(item => {
            const row = document.createElement('div');
            row.className = 'shap-item-row';
            row.innerHTML = `
                <span>${item.feature}</span>
                <span class="shap-val-pos">+${Number(item.shap_value).toFixed(3)} t/ha</span>
            `;
            posList.appendChild(row);
        });
    } else {
        posList.innerHTML = '<div class="shap-item-row">No positive feature contributions.</div>';
    }

    const negList = document.getElementById('live-shap-negative-list');
    negList.innerHTML = '';
    if (shap.top_negative && shap.top_negative.length > 0) {
        shap.top_negative.forEach(item => {
            const row = document.createElement('div');
            row.className = 'shap-item-row';
            row.innerHTML = `
                <span>${item.feature}</span>
                <span class="shap-val-neg">${Number(item.shap_value).toFixed(3)} t/ha</span>
            `;
            negList.appendChild(row);
        });
    } else {
        negList.innerHTML = '<div class="shap-item-row">No negative feature contributions.</div>';
    }

    // 5. Historical Condition Quantile Insights
    const insContainer = document.getElementById('live-insights-container');
    insContainer.innerHTML = '';
    if (data.historical_insights && data.historical_insights.length > 0) {
        data.historical_insights.forEach(ins => {
            const card = document.createElement('div');
            const statusClass = ins.status ? ins.status.toLowerCase().replace(/ /g, '-') : 'within-typical-range';
            card.className = `insight-card ${statusClass}`;

            const statusText = currentLang === 'ta' ? (ins.status_ta || ins.status) : ins.status;
            const msgText = currentLang === 'ta' ? (ins.insight_ta || ins.insight_en) : ins.insight_en;

            card.innerHTML = `
                <div class="insight-header">
                    <span>${ins.feature} (${ins.user_value})</span>
                    <span class="status-tag">${statusText}</span>
                </div>
                <div style="font-size: 0.84rem; line-height: 1.45;">${msgText}</div>
            `;
            insContainer.appendChild(card);
        });
    }

    // 6. Data Quality Warnings & Disclaimer
    const warnList = document.getElementById('live-warnings-list');
    warnList.innerHTML = '';
    const warnings = data.data_quality_warnings || [];
    warnings.forEach(w => {
        const li = document.createElement('li');
        li.textContent = w;
        warnList.appendChild(li);
    });
}

// Tamil Speech Synthesis for Live Prediction
function playLiveTamilVoice() {
    if (!('speechSynthesis' in window)) {
        alert("Text-to-Speech is not supported in this browser.");
        return;
    }

    if (!lastLiveResult) {
        alert("Please run a live prediction first!");
        return;
    }

    window.speechSynthesis.cancel();

    const d = lastLiveResult;
    let text = `${d.district} மாவட்டத்திற்கான நேரடி செயற்கைக்கோள் மற்றும் வானிலை அடிப்படையில் கணக்கிடப்பட்ட நெல் மகசூல் எக்டேருக்கு ${d.predicted_yield} டன்கள் ஆகும். `;

    if (d.suggestions_ta && d.suggestions_ta.length > 0) {
        text += "விவசாய ஆலோசனை: " + d.suggestions_ta[0];
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ta-IN';
    utterance.rate = 0.9;

    const voices = window.speechSynthesis.getVoices();
    const taVoice = voices.find(v => v.lang.includes('ta') || v.lang.includes('ta-IN'));
    if (taVoice) utterance.voice = taVoice;

    window.speechSynthesis.speak(utterance);
}
