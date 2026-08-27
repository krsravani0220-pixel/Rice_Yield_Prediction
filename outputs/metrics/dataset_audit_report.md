# Phase 1: Dataset Audit Report

- **Dataset Location:** `data/raw/DS_Final_1997_2023(1).xlsx`
- **Sheets Found:** ['ML_Dataset']
- **Shape:** 810 rows × 26 columns
- **Duplicate Rows:** 0
- **Year Range:** 1997 – 2023 (27 years)
- **Districts (30):** Chennai, Coimbatore, Cuddalore, Dharmapuri, Dindigul, Erode, Kancheepuram, Kanyakumari, Karur, Krishnagiri, Madurai, Nagapattinam, Namakkal, Perambalur, Pudukkottai, Ramanathapuram, Salem, Sivagangai, Thanjavur, The Nilgiris, Theni, Thiruvallur, Thiruvannamalai, Thiruvarur, Thoothukudi, Tiruchirappalli, Tirunelveli, Vellore, Villupuram, Virudhunagar

## Missing Values Analysis

| Column Name | Data Type | Null Count | Null % |
|---|---|---|---|
| `District` | str | 0 | 0.0% |
| `Year` | int64 | 0 | 0.0% |
| `Kharif Temperature` | float64 | 15 | 1.85% |
| `Kharif Rainfall` | float64 | 0 | 0.0% |
| `Kharif Humidity` | float64 | 15 | 1.85% |
| `Kharif Wind_Speed` | float64 | 15 | 1.85% |
| `Kharif Soil_Moisture` | float64 | 15 | 1.85% |
| `Rabi Temperature` | float64 | 11 | 1.36% |
| `Rabi Rainfall` | float64 | 0 | 0.0% |
| `Rabi Humidity` | float64 | 11 | 1.36% |
| `Rabi Wind_Speed` | float64 | 11 | 1.36% |
| `Rabi Soil_Moisture` | float64 | 11 | 1.36% |
| `Zaid Temperature` | float64 | 15 | 1.85% |
| `Zaid Rainfall` | float64 | 0 | 0.0% |
| `Zaid Humidity` | float64 | 15 | 1.85% |
| `Zaid Wind_Speed` | float64 | 12 | 1.48% |
| `Zaid Soil_Moisture` | float64 | 15 | 1.85% |
| `Soil_PH` | float64 | 0 | 0.0% |
| `Soil_Type` | str | 0 | 0.0% |
| `N` | int64 | 0 | 0.0% |
| `P` | int64 | 0 | 0.0% |
| `K` | int64 | 0 | 0.0% |
| `Fertilizer` | int64 | 0 | 0.0% |
| `Pesticide` | float64 | 0 | 0.0% |
| `Area` | float64 | 23 | 2.84% |
| `Yield` | float64 | 25 | 3.09% |

## Yield Statistics (Target Variable)

- **count:** 785.0
- **mean:** 3.5728407643312106
- **std:** 1.005216473979928
- **min:** 0.0
- **25%:** 3.12
- **50%:** 3.62
- **75%:** 4.16
- **max:** 9.89
- **null_count:** 25

## Key Data Quality Observations

1. Target `Yield` has 25 missing values that require target-filtering during training.
2. Seasonal features (Kharif, Rabi, Zaid) contain missing values in earlier years (e.g. 1997-2000).
3. All features keep separate Kharif, Rabi, and Zaid seasonal averages without re-aggregation.
