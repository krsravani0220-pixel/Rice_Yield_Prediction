import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class CropHealthEngine:
    def __init__(self):
        pass

    def diagnose_crop_health(self, observations):
        """
        observations dict:
        - leaf_condition: 'Normal', 'Yellowing', 'Browning', 'Spotting'
        - water_status: 'Adequate', 'Drought Stress', 'Waterlogged'
        - pest_obs: 'None', 'Stem Borer', 'Leaf Folder', 'BPH (Brown Plant Hopper)'
        - disease_obs: 'None', 'Blast', 'Sheath Blight', 'Bacterial Blight'
        - growth_stage: 'Vegetative', 'Tillering', 'Panicle Initiation', 'Flowering'
        """
        leaf = observations.get('leaf_condition', 'Normal')
        water = observations.get('water_status', 'Adequate')
        pest = observations.get('pest_obs', 'None')
        disease = observations.get('disease_obs', 'None')
        stage = observations.get('growth_stage', 'Tillering')
        
        advisories_en = []
        advisories_ta = []
        
        # Leaf condition advice
        if leaf == 'Yellowing':
            advisories_en.append("Nitrogen deficiency or root asphyxiation suspected. Apply top-dressing of Neem Coated Urea (25 kg/acre) or spray 1% Foliar Urea.")
            advisories_ta.append("நைட்ரஜன் குறைபாடு அல்லது வேர் மூச்சுத்திணறல் இருக்கலாம். வேப்ப எண்ணெய் பூசிய யூரியா (ஏக்கருக்கு 25 கிலோ) அல்லது 1% யூரியா தெளிக்கவும்.")
        elif leaf == 'Browning':
            advisories_en.append("Potash deficiency or leaf tip burn detected. Apply Mop (Muriate of Potash) 15 kg/acre.")
            advisories_ta.append("பொட்டாஷ் குறைபாடு கண்டறியப்பட்டது. ஏக்கருக்கு 15 கிலோ பொட்டாஷ் (MOP) இடவும்.")
            
        # Water status advice
        if water == 'Drought Stress':
            advisories_en.append(f"Drought stress at {stage} stage can reduce panicle fertility. Practice Alternate Wetting and Drying (AWD) to maximize water efficiency.")
            advisories_ta.append(f"{stage} நிலையில் வறட்சி அழுத்தம் மகசூல் குறைப்பை ஏற்படுத்தும். மாற்று நனைத்தல் மற்றும் உலர்த்தல் (AWD) முறையைப் பின்பற்றி நீரைப் பாசனத்திற்குப் பயன்படுத்தவும்.")
        elif water == 'Waterlogged':
            advisories_en.append("Excess waterlogging. Drain excess water immediately to encourage soil aeration and prevent sheath rot.")
            advisories_ta.append("அதிக தண்ணீர் தேக்கம். மண் காற்றோட்டத்தை அதிகரிக்கவும் தண்டு அழுகலைத் தடுக்கவும் உபரி நீரை உடனடியாக வடித்துவிடவும்.")
            
        # Pest advice
        if pest == 'Stem Borer':
            advisories_en.append("Stem Borer infestation detected ('Dead Heart' symptoms). Install Pheromone traps (5/acre) and apply Cartap Hydrochloride 4G (10 kg/acre).")
            advisories_ta.append("குருத்து பூச்சி தாக்குதல் கண்டறியப்பட்டது. இனக்கவர்ச்சி பொறி (ஏக்கருக்கு 5) வைத்து கார்டாப் ஹைட்ரோகுளோரைடு 4G (ஏக்கருக்கு 10 கிலோ) இடவும்.")
        elif pest == 'Leaf Folder':
            advisories_en.append("Leaf Folder detected. Release Trichogramma chilonis egg parasitoids (2 cc/acre) or spray Chlorantraniliprole 18.5% SC.")
            advisories_ta.append("இலை சுருட்டுப் புழு கண்டறியப்பட்டது. டிரைகோகிரம்மா ஒட்டுண்ணிகளை வெளியிடவும் அல்லது குளோரான்ட்ரனிலிப்ரோல் தெளிக்கவும்.")
        elif pest == 'BPH (Brown Plant Hopper)':
            advisories_en.append("Brown Plant Hopper (BPH) notice at base. Drain water, avoid excess Nitrogen, and spray Triflumezopyrim 10% SC.")
            advisories_ta.append("புகையான் பூச்சி கண்டறியப்பட்டது. தண்ணீரை வடித்து, அதிக நைட்ரஜனைத் தவிர்த்து, டிரைப்ளூமிஸோபைரிம் தெளிக்கவும்.")
            
        # Disease advice
        if disease == 'Blast':
            advisories_en.append("Rice Blast symptoms observed. Avoid excess Nitrogen fertilizer and spray Tricyclazole 75% WP (0.6 g/L).")
            advisories_ta.append("குலை நோய் அறிகுறிகள். அதிக நைட்ரஜன் உரத்தைத் தவிர்த்து, டிரைசைக்ளசோல் 75% WP (லிட்டருக்கு 0.6 கிராம்) தெளிக்கவும்.")
        elif disease == 'Sheath Blight':
            advisories_en.append("Sheath Blight symptoms. Maintain wider plant spacing and spray Hexaconazole 5% EC (2 mL/L).")
            advisories_ta.append("தண்டு அழுகல் நோய். ஹெக்ஸாகோனசோல் 5% EC (லிட்டருக்கு 2 மி.லி) தெளிக்கவும்.")
        elif disease == 'Bacterial Blight':
            advisories_en.append("Bacterial Leaf Blight detected. Spray Copper Hydroxide 77% WP (2 g/L) + Streptocycline (0.1 g/L).")
            advisories_ta.append("பாக்டீரியா இலை கருகல் நோய். தாமிர ஹைட்ராக்சைடு + ஸ்ட்ரெப்டோமைசின் தெளிக்கவும்.")
            
        if len(advisories_en) == 0:
            advisories_en.append("Crop visual condition appears healthy and vigorous. Maintain standard package of practices.")
            advisories_ta.append("பயிர் ஆரோக்கியமாக உள்ளது. வழக்கமான விவசாய முறைகளைப் பராமரிக்கவும்.")
            
        return {
            'growth_stage': stage,
            'observations_summary': observations,
            'advisories_en': advisories_en,
            'advisories_ta': advisories_ta
        }

def run_crop_health_demo():
    print("Running Phase 13 Crop Health Module...")
    engine = CropHealthEngine()
    obs = {
        'growth_stage': 'Panicle Initiation',
        'leaf_condition': 'Yellowing',
        'water_status': 'Drought Stress',
        'pest_obs': 'Stem Borer',
        'disease_obs': 'None'
    }
    diag = engine.diagnose_crop_health(obs)
    print("\n--- Diagnostic Advisories ---")
    for en, ta in zip(diag['advisories_en'], diag['advisories_ta']):
        print(f"• EN: {en}")
        print(f"  TA: {ta}\n")
    return diag

if __name__ == '__main__':
    run_crop_health_demo()
