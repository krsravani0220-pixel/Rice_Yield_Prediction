import sys
import os
import json
import pandas as pd
import numpy as np

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class HistoricalInsightsEngine:
    def __init__(self, excel_path='DS_Final_1997_2023(1).xlsx'):
        if os.path.exists(excel_path):
            self.df = pd.read_excel(excel_path)
        elif os.path.exists(os.path.join('data', 'raw', 'DS_Final_1997_2023(1).xlsx')):
            self.df = pd.read_excel(os.path.join('data', 'raw', 'DS_Final_1997_2023(1).xlsx'))
        elif os.path.exists('data/processed/rice_yield_processed.csv'):
            self.df = pd.read_csv('data/processed/rice_yield_processed.csv')
        else:
            raise FileNotFoundError("Could not locate historical dataset Excel file.")
        self.df['District'] = self.df['District'].astype(str).str.strip()
        self.df = self.df[self.df['District'].str.title() != 'Chennai'].copy()

        self.districts = sorted(self.df['District'].dropna().unique().tolist())
        self._compute_district_stats()
        
    def _compute_district_stats(self):
        """
        Computes 10th, 25th, 50th, 75th, 90th percentiles for every numerical feature
        grouped by District.
        """
        num_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if 'Year' in num_cols:
            num_cols.remove('Year')
            
        self.district_stats = {}
        self.district_avg_yield = {}
        for d in self.districts:
            d_df = self.df[self.df['District'] == d]
            self.district_stats[d] = {}

            # Calculate historical district mean yield
            if 'Yield' in d_df.columns:
                y_vals = d_df['Yield'].dropna()
                self.district_avg_yield[d] = round(float(y_vals.mean()), 2) if len(y_vals) > 0 else 3.53
            else:
                self.district_avg_yield[d] = 3.53

            for col in num_cols:
                vals = d_df[col].dropna()
                if len(vals) > 0:
                    self.district_stats[d][col] = {
                        'min': float(vals.min()),
                        'p10': float(vals.quantile(0.10)),
                        'p25': float(vals.quantile(0.25)),
                        'p50': float(vals.median()),
                        'p75': float(vals.quantile(0.75)),
                        'p90': float(vals.quantile(0.90)),
                        'max': float(vals.max()),
                        'mean': float(vals.mean()),
                        'std': float(vals.std())
                    }
                    
    def evaluate_feature_condition(self, district, feature_name, value):
        """
        Classifies feature input relative to historical district distribution.
        """
        if district not in self.district_stats or feature_name not in self.district_stats[district]:
            return {
                'status': 'Unknown',
                'status_ta': 'தெரியவில்லை',
                'message': 'No historical statistics available for this district.',
                'message_ta': 'இந்த மாவட்டத்திற்கான வரலாற்று புள்ளிவிவரங்கள் இல்லை.'
            }
            
        stats = self.district_stats[district][feature_name]
        v = float(value)
        
        if v < stats['p10']:
            category = 'Extremely Low'
            category_ta = 'மிகக் குறைவு'
        elif v < stats['p25']:
            category = 'Lower than Typical'
            category_ta = 'சாதாரணத்தை விட குறைவு'
        elif v <= stats['p75']:
            category = 'Within Typical Range'
            category_ta = 'சாதாரண வரம்பிற்குள்'
        elif v <= stats['p90']:
            category = 'Higher than Typical'
            category_ta = 'சாதாரணத்தை விட அதிகம்'
        else:
            category = 'Extremely High'
            category_ta = 'மிக அதிகளவு'
            
        advice = self._get_agricultural_advice(feature_name, category, category_ta, v, stats)
        
        return {
            'feature': feature_name,
            'district': district,
            'user_value': round(v, 2),
            'historical_median': round(stats['p50'], 2),
            'typical_range': [round(stats['p25'], 2), round(stats['p75'], 2)],
            'status': category,
            'status_ta': category_ta,
            'insight_en': advice['en'],
            'insight_ta': advice['ta']
        }
        
    def _get_agricultural_advice(self, feature_name, category, category_ta, val, stats):
        if category == 'Within Typical Range':
            return {
                'en': f"{feature_name} is within typical historical range ({round(stats['p25'], 1)} - {round(stats['p75'], 1)}) for this district.",
                'ta': f"{feature_name} இந்த மாவட்டத்தின் சாதாரண வரலாற்று வரம்பிற்குள் உள்ளது."
            }
            
        if 'Rainfall' in feature_name:
            if category in ['Extremely High', 'Higher than Typical']:
                return {
                    'en': f"High seasonal rainfall ({val} mm) recorded. Ensure adequate drainage to prevent field submergence and root rot in rice crops.",
                    'ta': f"அதிக மழைப்பொழிவு ({val} மி.மீ) பதிவாகியுள்ளது. நெற்பயிரில் தண்ணீர் தேங்கி வேர் அழுகல் ஏற்படுவதைத் தடுக்க வடிகால் வசதியை உறுதி செய்யவும்."
                }
            else:
                return {
                    'en': f"Low rainfall ({val} mm) detected. Supplemental irrigation is strongly advised during critical flowering/tillering stages.",
                    'ta': f"குறைந்த மழைப்பொழிவு ({val} மி.மீ) கண்டறியப்பட்டது. பூக்கும் மற்றும் தூர் கட்டும் கட்டங்களில் துணைப் பாசனம் செய்ய அறிவுறுத்தப்படுகிறது."
                }
                
        elif 'Temperature' in feature_name:
            if category in ['Extremely High', 'Higher than Typical']:
                return {
                    'en': f"Higher seasonal temperature ({val}°C). Heat stress may shorten grain filling duration; maintain shallow standing water for cooling.",
                    'ta': f"அதிக வெப்பநிலை ({val}°C). வெப்ப அழுத்தத்தைக் குறைக்க வயலில் லேசான நீர் மட்டத்தைப் பராமரிக்கவும்."
                }
            else:
                return {
                    'en': f"Lower seasonal temperature ({val}°C). Crop maturation might be slightly delayed.",
                    'ta': f"குறைந்த வெப்பநிலை ({val}°C). பயிர் முதிர்ச்சி சற்று தாமதமாகலாம்."
                }
                
        elif 'Soil_Moisture' in feature_name:
            if category in ['Extremely Low', 'Lower than Typical']:
                return {
                    'en': f"Soil moisture ({val}) is below typical level. Risk of moisture deficit stress during panicle initiation.",
                    'ta': f"மண் ஈரப்பதம் ({val}) குறைவாக உள்ளது. கதிர் உருவாகும் தருணத்தில் நீர் பற்றாக்குறை ஆபத்து உள்ளது."
                }
            else:
                return {
                    'en': f"Optimal to high soil moisture ({val}) maintained for rice root zone.",
                    'ta': f"நெல் வேர் மண்டலத்திற்கு உகந்த மண் ஈரப்பதம் ({val}) பராமரிக்கப்படுகிறது."
                }
                
        elif 'Soil_PH' in feature_name:
            if val < 6.0:
                return {
                    'en': f"Acidic soil pH ({val}). Agricultural lime application recommended to optimize nutrient availability.",
                    'ta': f"அமில மண் pH ({val}). விவசாய சுண்ணம் இடவும்."
                }
            elif val > 8.0:
                return {
                    'en': f"Alkaline soil pH ({val}). Gypsum application recommended to mitigate salinity stress.",
                    'ta': f"கார மண் pH ({val}). ஜிப்சம் இட அறிவுறுத்தப்படுகிறது."
                }
                
        elif feature_name in ['N', 'P', 'K', 'Fertilizer']:
            if category in ['Extremely Low', 'Lower than Typical']:
                return {
                    'en': f"Nutrient level ({val}) is lower than district average. Balanced NPK top-dressing suggested.",
                    'ta': f"ஊட்டச்சத்து அளவு ({val}) மாவட்ட சராசரியை விட குறைவு. சமச்சீர் NPK உரம் இடவும்."
                }
            else:
                return {
                    'en': f"High nutrient/fertilizer application ({val}). Avoid excessive nitrogen to prevent vegetative lodging and pest buildup.",
                    'ta': f"அதிக உர பயன்பாடு ({val}). பயிர் சாய்வதைத் தடுக்க அதிக நைட்ரஜனைத் தவிர்க்கவும்."
                }
                
        return {
            'en': f"{feature_name} is {category.lower()} compared to historical norms.",
            'ta': f"{feature_name} வரலாற்று அளவை விட {category_ta}."
        }

    def generate_full_insights(self, district, user_input_dict):
        results = []
        for feature_name, value in user_input_dict.items():
            if feature_name in ['District', 'Year', 'Soil_Type', 'Yield']:
                continue
            if isinstance(value, (int, float, np.number)):
                res = self.evaluate_feature_condition(district, feature_name, value)
                results.append(res)
        
        # Sort so features with deviations (Extremely High/Low, Higher/Lower) appear first
        results.sort(key=lambda x: 0 if x['status'] != 'Within Typical Range' else 1)
        return results[:5]

def run_insights_demo():
    print("Running Phase 8 Historical Condition Insights Engine...")
    engine = HistoricalInsightsEngine()
    
    sample_input = {
        'Kharif Rainfall': 180.0,
        'Kharif Temperature': 31.5,
        'Kharif Soil_Moisture': 0.35,
        'Soil_PH': 5.8
    }
    
    insights = engine.generate_full_insights('Thanjavur', sample_input)
    
    print("\n--- Sample Insights for Thanjavur ---")
    for ins in insights:
        print(f"Feature: {ins['feature']} | Status: {ins['status']}")
        print(f"  EN: {ins['insight_en']}")
        print(f"  TA: {ins['insight_ta']}\n")
        
    return insights

if __name__ == '__main__':
    run_insights_demo()
