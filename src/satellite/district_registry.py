"""
Tamil Nadu 30 Districts Geospatial & Agronomic Registry
======================================================
Provides verified geographic boundaries, representative agricultural coordinates,
bounding boxes, Copernicus Sentinel-2 MGRS tiles, agro-climatic zones, and
established static soil properties for all 30 districts of Tamil Nadu.
"""

from typing import Dict, Any, List, Optional

TAMIL_NADU_DISTRICTS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Chennai": {
        "lat": 13.0827, "lon": 80.2707,
        "bbox": [80.15, 12.95, 80.35, 13.20],
        "primary_tile": "T44VNR",
        "agro_climatic_zone": "North-Eastern Zone (Metropolitan)",
        "is_agricultural": False,
        "soil_type": "coastal alluvium",
        "soil_ph": 7.8, "n": 280.0, "p": 18.0, "k": 190.0,
        "fertilizer": 150.0, "pesticide": 2.0, "area": 121.0,
        "notes": "Metropolitan urban center; commercial paddy cultivation is minimal or non-existent."
    },
    "Coimbatore": {
        "lat": 11.0168, "lon": 76.9558,
        "bbox": [76.70, 10.75, 77.30, 11.40],
        "primary_tile": "T43QGF",
        "agro_climatic_zone": "Western Zone",
        "is_agricultural": True,
        "soil_type": "black soil",
        "soil_ph": 7.7, "n": 310.0, "p": 20.0, "k": 220.0,
        "fertilizer": 170.0, "pesticide": 2.4, "area": 1169.0,
        "notes": "Western semi-arid tract; predominantly Noyyal river basin and tank irrigation."
    },
    "Cuddalore": {
        "lat": 11.7480, "lon": 79.7714,
        "bbox": [79.20, 11.20, 79.95, 11.90],
        "primary_tile": "T44PNV",
        "agro_climatic_zone": "North-Eastern Coastal Zone",
        "is_agricultural": True,
        "soil_type": "coastal alluvium",
        "soil_ph": 7.8, "n": 270.0, "p": 17.0, "k": 185.0,
        "fertilizer": 160.0, "pesticide": 2.2, "area": 138837.0,
        "notes": "Major paddy cultivating district fed by Veeranam lake, Coleroon, and Gadilam rivers."
    },
    "Dharmapuri": {
        "lat": 12.1211, "lon": 78.1582,
        "bbox": [77.70, 11.80, 78.60, 12.45],
        "primary_tile": "T44PKS",
        "agro_climatic_zone": "North-Western Zone",
        "is_agricultural": True,
        "soil_type": "red sandy soil",
        "soil_ph": 7.4, "n": 290.0, "p": 18.0, "k": 200.0,
        "fertilizer": 150.0, "pesticide": 2.0, "area": 27923.0,
        "notes": "Plateau dryland agricultural tract with well and tank irrigation."
    },
    "Dindigul": {
        "lat": 10.3673, "lon": 77.9803,
        "bbox": [77.30, 10.05, 78.35, 10.75],
        "primary_tile": "T44PMA",
        "agro_climatic_zone": "Southern Zone",
        "is_agricultural": True,
        "soil_type": "red soil",
        "soil_ph": 7.4, "n": 295.0, "p": 19.0, "k": 205.0,
        "fertilizer": 160.0, "pesticide": 2.3, "area": 13547.0,
        "notes": "Foothill agro-climatic region; river basin agriculture along Vaigai and Amaravathi tributaries."
    },
    "Erode": {
        "lat": 11.3410, "lon": 77.7172,
        "bbox": [76.85, 11.00, 77.95, 11.85],
        "primary_tile": "T43QHE",
        "agro_climatic_zone": "Western Zone",
        "is_agricultural": True,
        "soil_type": "black soil",
        "soil_ph": 8.0, "n": 320.0, "p": 22.0, "k": 230.0,
        "fertilizer": 180.0, "pesticide": 2.7, "area": 31062.0,
        "notes": "Intensive canal irrigation zone along Lower Bhavani Project (LBP) and Cauvery."
    },
    "Kancheepuram": {
        "lat": 12.8342, "lon": 79.7036,
        "bbox": [79.40, 12.50, 80.15, 13.10],
        "primary_tile": "T44PNU",
        "agro_climatic_zone": "North-Eastern Zone",
        "is_agricultural": True,
        "soil_type": "red sandy loam soil",
        "soil_ph": 7.5, "n": 285.0, "p": 18.0, "k": 195.0,
        "fertilizer": 160.0, "pesticide": 2.1, "area": 87814.0,
        "notes": "Traditional 'district of a thousand tanks' with Palar river basin paddy cultivation."
    },
    "Kanyakumari": {
        "lat": 8.0883, "lon": 77.5385,
        "bbox": [77.10, 8.05, 77.65, 8.55],
        "primary_tile": "T43QPE",
        "agro_climatic_zone": "High Rainfall / Southern Zone",
        "is_agricultural": True,
        "soil_type": "laterite soil",
        "soil_ph": 6.8, "n": 260.0, "p": 15.0, "k": 170.0,
        "fertilizer": 140.0, "pesticide": 1.8, "area": 10521.0,
        "notes": "High rainfall coastal humid zone with dual monsoon exposure (Southwest & Northeast)."
    },
    "Karur": {
        "lat": 10.9601, "lon": 78.0766,
        "bbox": [77.80, 10.60, 78.40, 11.15],
        "primary_tile": "T44PKA",
        "agro_climatic_zone": "Cauvery Basin Zone",
        "is_agricultural": True,
        "soil_type": "alluvial soil",
        "soil_ph": 7.9, "n": 305.0, "p": 20.0, "k": 215.0,
        "fertilizer": 170.0, "pesticide": 2.4, "area": 10793.0,
        "notes": "Upper Cauvery delta riparian tract irrigated by Amaravathi and Cauvery river canals."
    },
    "Krishnagiri": {
        "lat": 12.5186, "lon": 78.2137,
        "bbox": [77.50, 12.15, 78.65, 12.90],
        "primary_tile": "T44PLS",
        "agro_climatic_zone": "North-Western Zone",
        "is_agricultural": True,
        "soil_type": "red sandy soil",
        "soil_ph": 7.3, "n": 290.0, "p": 18.0, "k": 200.0,
        "fertilizer": 150.0, "pesticide": 2.0, "area": 31393.0,
        "notes": "Plateau dryland agriculture; partitioned from Dharmapuri district in 2004."
    },
    "Madurai": {
        "lat": 9.9252, "lon": 78.1198,
        "bbox": [77.80, 9.60, 78.50, 10.25],
        "primary_tile": "T44PNA",
        "agro_climatic_zone": "Southern Zone",
        "is_agricultural": True,
        "soil_type": "red soil",
        "soil_ph": 7.6, "n": 300.0, "p": 19.0, "k": 210.0,
        "fertilizer": 165.0, "pesticide": 2.3, "area": 44781.0,
        "notes": "Double crop paddy area under Periyar-Vaigai irrigation project."
    },
    "Nagapattinam": {
        "lat": 10.7672, "lon": 79.8436,
        "bbox": [79.60, 10.30, 79.95, 11.25],
        "primary_tile": "T44PMU",
        "agro_climatic_zone": "Cauvery Delta Zone",
        "is_agricultural": True,
        "soil_type": "coastal alluvium",
        "soil_ph": 7.9, "n": 275.0, "p": 17.0, "k": 180.0,
        "fertilizer": 155.0, "pesticide": 2.1, "area": 149372.0,
        "notes": "Tail-end Cauvery delta coastal rice bowl with heavy reliance on Northeast monsoon."
    },
    "Namakkal": {
        "lat": 11.2189, "lon": 78.1674,
        "bbox": [77.70, 11.00, 78.50, 11.60],
        "primary_tile": "T44PKT",
        "agro_climatic_zone": "North-Western Zone",
        "is_agricultural": True,
        "soil_type": "red loamy soil",
        "soil_ph": 7.5, "n": 300.0, "p": 19.0, "k": 205.0,
        "fertilizer": 160.0, "pesticide": 2.2, "area": 7323.0,
        "notes": "Dry semi-arid zone with Cauvery river canal command area on southern boundary."
    },
    "Perambalur": {
        "lat": 11.2342, "lon": 78.8820,
        "bbox": [78.60, 11.05, 79.25, 11.45],
        "primary_tile": "T44PNT",
        "agro_climatic_zone": "Cauvery Basin Dry Tract",
        "is_agricultural": True,
        "soil_type": "black soil",
        "soil_ph": 7.8, "n": 295.0, "p": 18.0, "k": 200.0,
        "fertilizer": 155.0, "pesticide": 2.1, "area": 11840.0,
        "notes": "Central rainfed dry farming tract with seasonal tank irrigation."
    },
    "Pudukkottai": {
        "lat": 10.3797, "lon": 78.8208,
        "bbox": [78.40, 9.85, 79.25, 10.65],
        "primary_tile": "T44PMB",
        "agro_climatic_zone": "Southern / Coastal Zone",
        "is_agricultural": True,
        "soil_type": "red sandy loam soil",
        "soil_ph": 7.3, "n": 280.0, "p": 17.0, "k": 190.0,
        "fertilizer": 150.0, "pesticide": 2.0, "area": 88310.0,
        "notes": "Rainfed tank irrigation tract in lower Vellar and Agniyar river basins."
    },
    "Ramanathapuram": {
        "lat": 9.3639, "lon": 78.8395,
        "bbox": [78.20, 9.10, 79.40, 9.85],
        "primary_tile": "T44PMC",
        "agro_climatic_zone": "Southern Coastal Dry Zone",
        "is_agricultural": True,
        "soil_type": "coastal sandy soil",
        "soil_ph": 8.1, "n": 265.0, "p": 16.0, "k": 175.0,
        "fertilizer": 140.0, "pesticide": 1.9, "area": 121849.0,
        "notes": "Dry drought-prone direct-seeded paddy tract; highly vulnerable to Northeast monsoon failure."
    },
    "Salem": {
        "lat": 11.6643, "lon": 78.1460,
        "bbox": [77.75, 11.40, 78.80, 12.05],
        "primary_tile": "T44PKT",
        "agro_climatic_zone": "North-Western Zone",
        "is_agricultural": True,
        "soil_type": "red loamy soil",
        "soil_ph": 7.5, "n": 305.0, "p": 20.0, "k": 210.0,
        "fertilizer": 165.0, "pesticide": 2.3, "area": 12408.0,
        "notes": "North-western undulating terrain irrigated by Mettur dam canal system and borewells."
    },
    "Sivagangai": {
        "lat": 9.8433, "lon": 78.4809,
        "bbox": [78.10, 9.50, 79.00, 10.25],
        "primary_tile": "T44PNB",
        "agro_climatic_zone": "Southern Zone",
        "is_agricultural": True,
        "soil_type": "red soil",
        "soil_ph": 7.4, "n": 285.0, "p": 17.0, "k": 195.0,
        "fertilizer": 150.0, "pesticide": 2.0, "area": 73236.0,
        "notes": "Traditional cascade tank system (Ooranis/Eris) fed by Vaigai and Sarugani rivers."
    },
    "Thanjavur": {
        "lat": 10.7870, "lon": 79.1378,
        "bbox": [78.80, 10.15, 79.45, 11.20],
        "primary_tile": "T44PMU",
        "agro_climatic_zone": "Cauvery Delta Heartland",
        "is_agricultural": True,
        "soil_type": "alluvial soil",
        "soil_ph": 7.7, "n": 315.0, "p": 21.0, "k": 225.0,
        "fertilizer": 175.0, "pesticide": 2.5, "area": 170997.0,
        "notes": "Primary rice bowl of Tamil Nadu with extensive canal network of Vennar and Grand Anicut Canal."
    },
    "The Nilgiris": {
        "lat": 11.4102, "lon": 76.6950,
        "bbox": [76.35, 11.15, 77.05, 11.75],
        "primary_tile": "T43QGE",
        "agro_climatic_zone": "Hilly / High Altitude Zone",
        "is_agricultural": False,
        "soil_type": "laterite soil",
        "soil_ph": 6.5, "n": 250.0, "p": 15.0, "k": 160.0,
        "fertilizer": 130.0, "pesticide": 1.6, "area": 420.0,
        "notes": "High altitude Western Ghats plateau; predominantly plantation crops (tea) with terrace paddy."
    },
    "Theni": {
        "lat": 10.0104, "lon": 77.4768,
        "bbox": [77.15, 9.60, 77.75, 10.30],
        "primary_tile": "T43QPF",
        "agro_climatic_zone": "Southern Western Ghats Zone",
        "is_agricultural": True,
        "soil_type": "red soil",
        "soil_ph": 7.3, "n": 310.0, "p": 20.0, "k": 220.0,
        "fertilizer": 170.0, "pesticide": 2.4, "area": 14781.0,
        "notes": "Fertile Cumbum valley irrigated by Mullaperiyar and Vaigai river waters."
    },
    "Thiruvallur": {
        "lat": 13.1432, "lon": 79.9083,
        "bbox": [79.50, 12.95, 80.35, 13.55],
        "primary_tile": "T44VNR",
        "agro_climatic_zone": "North-Eastern Zone",
        "is_agricultural": True,
        "soil_type": "coastal alluvium",
        "soil_ph": 7.6, "n": 285.0, "p": 18.0, "k": 195.0,
        "fertilizer": 160.0, "pesticide": 2.2, "area": 106093.0,
        "notes": "Major paddy producer in northern Tamil Nadu with Araniyar and Kusasthalaiyar basins."
    },
    "Thiruvannamalai": {
        "lat": 12.2253, "lon": 79.0747,
        "bbox": [78.60, 11.95, 79.75, 12.75],
        "primary_tile": "T44PMV",
        "agro_climatic_zone": "North-Eastern Zone",
        "is_agricultural": True,
        "soil_type": "red sandy loam soil",
        "soil_ph": 7.4, "n": 295.0, "p": 19.0, "k": 205.0,
        "fertilizer": 165.0, "pesticide": 2.3, "area": 139151.0,
        "notes": "Large paddy producing district irrigated by Sathanur reservoir and Cheyyar river."
    },
    "Thiruvarur": {
        "lat": 10.7725, "lon": 79.6365,
        "bbox": [79.40, 10.30, 79.85, 11.05],
        "primary_tile": "T44PMU",
        "agro_climatic_zone": "Cauvery Delta Heartland",
        "is_agricultural": True,
        "soil_type": "alluvial soil",
        "soil_ph": 7.8, "n": 310.0, "p": 20.0, "k": 220.0,
        "fertilizer": 170.0, "pesticide": 2.4, "area": 154247.0,
        "notes": "Intensive deltaic rice monoculture zone traversed by Vennar, Vettar, and Koraiyar rivers."
    },
    "Thoothukudi": {
        "lat": 8.7642, "lon": 78.1348,
        "bbox": [77.70, 8.40, 78.35, 9.25],
        "primary_tile": "T43QQB",
        "agro_climatic_zone": "Southern Coastal Zone",
        "is_agricultural": True,
        "soil_type": "black soil",
        "soil_ph": 8.1, "n": 275.0, "p": 17.0, "k": 185.0,
        "fertilizer": 145.0, "pesticide": 2.0, "area": 11308.0,
        "notes": "Riparian paddy along Thamirabarani delta canal system; dry rainfed tracts elsewhere."
    },
    "Tiruchirappalli": {
        "lat": 10.7905, "lon": 78.7047,
        "bbox": [78.30, 10.45, 79.10, 11.25],
        "primary_tile": "T44PKT",
        "agro_climatic_zone": "Cauvery Delta Apex",
        "is_agricultural": True,
        "soil_type": "alluvial soil",
        "soil_ph": 7.7, "n": 305.0, "p": 20.0, "k": 215.0,
        "fertilizer": 165.0, "pesticide": 2.3, "area": 57422.0,
        "notes": "Apex of the Cauvery delta where the river bifurcates into Coleroon and Cauvery."
    },
    "Tirunelveli": {
        "lat": 8.7139, "lon": 77.7567,
        "bbox": [77.20, 8.25, 78.00, 9.20],
        "primary_tile": "T43QPB",
        "agro_climatic_zone": "Southern Thamirabarani Basin",
        "is_agricultural": True,
        "soil_type": "red soil",
        "soil_ph": 7.6, "n": 310.0, "p": 21.0, "k": 220.0,
        "fertilizer": 170.0, "pesticide": 2.4, "area": 78152.0,
        "notes": "Perennial river basin rice cultivation under the Thamirabarani canal system (Kar and Pishanam seasons)."
    },
    "Vellore": {
        "lat": 12.9165, "lon": 79.1325,
        "bbox": [78.60, 12.50, 79.50, 13.25],
        "primary_tile": "T44PNU",
        "agro_climatic_zone": "North-Eastern Zone",
        "is_agricultural": True,
        "soil_type": "red sandy loam soil",
        "soil_ph": 7.5, "n": 290.0, "p": 18.0, "k": 200.0,
        "fertilizer": 155.0, "pesticide": 2.1, "area": 39498.0,
        "notes": "Palar river basin dry agricultural zone with well irrigation."
    },
    "Villupuram": {
        "lat": 11.9401, "lon": 79.4861,
        "bbox": [78.90, 11.60, 80.05, 12.45],
        "primary_tile": "T44PNV",
        "agro_climatic_zone": "North-Eastern Zone",
        "is_agricultural": True,
        "soil_type": "coastal alluvium",
        "soil_ph": 7.6, "n": 290.0, "p": 18.0, "k": 200.0,
        "fertilizer": 160.0, "pesticide": 2.2, "area": 141973.0,
        "notes": "High rice acreage district irrigated by Thenpennai river and Sathanur canal network."
    },
    "Virudhunagar": {
        "lat": 9.5872, "lon": 77.9514,
        "bbox": [77.40, 9.30, 78.30, 9.85],
        "primary_tile": "T43QQF",
        "agro_climatic_zone": "Southern Semi-Arid Zone",
        "is_agricultural": True,
        "soil_type": "black soil",
        "soil_ph": 7.9, "n": 280.0, "p": 17.0, "k": 190.0,
        "fertilizer": 150.0, "pesticide": 2.0, "area": 25418.0,
        "notes": "Semi-arid black soil tract with Gundar river basin tank irrigation."
    }
}


def get_all_districts() -> List[str]:
    """Returns sorted list of all 30 Tamil Nadu districts."""
    return sorted(list(TAMIL_NADU_DISTRICTS_REGISTRY.keys()))


def get_district_profile(district_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves full geospatial, agro-climatic, and soil profile for a district."""
    clean_name = district_name.strip().title()
    for name, data in TAMIL_NADU_DISTRICTS_REGISTRY.items():
        if name.lower() == clean_name.lower():
            return {
                "district": name,
                "centroid": {"latitude": data["lat"], "longitude": data["lon"]},
                "primary_sentinel2_tile": data["primary_tile"],
                **data
            }
    return None


def get_district_polygon_wkt(district_name: str) -> Optional[str]:
    """Generates WKT Polygon from district bounding box for STAC / OData query."""
    prof = get_district_profile(district_name)
    if not prof:
        return None
    min_lon, min_lat, max_lon, max_lat = prof["bbox"]
    # Closed polygon in counter-clockwise order
    return f"POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat}, {max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))"
