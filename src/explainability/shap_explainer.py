import os
import json
import joblib
import numpy as np
import pandas as pd
import shap

class YieldShapExplainer:
    def __init__(self, model_path='models/best_yield_model.joblib', metadata_path='models/feature_metadata.joblib'):
        self.model = joblib.load(model_path)
        self.metadata = joblib.load(metadata_path)
        self.feature_names = self.metadata['feature_names']
        
        # Initialize SHAP explainer
        if hasattr(self.model, 'predict'):
            try:
                self.explainer = shap.TreeExplainer(self.model)
            except Exception:
                train_data = joblib.load('data/processed/train_data.joblib')
                self.explainer = shap.Explainer(self.model.predict, train_data['X'])

    def _format_feature_name(self, raw_name):
        if raw_name.startswith('District_'):
            dist = raw_name.replace('District_', '')
            return f"District: {dist}"
        elif raw_name.startswith('Soil_Type_'):
            st = raw_name.replace('Soil_Type_', '')
            return f"Soil Type: {st.title()}"
        else:
            name_map = {
                'Soil_PH': 'Soil pH',
                'N': 'Nitrogen (N)',
                'P': 'Phosphorus (P)',
                'K': 'Potassium (K)',
                'Area': 'Cultivated Area',
                'Fertilizer': 'Fertilizer Application',
                'Pesticide': 'Pesticide Application'
            }
            if raw_name in name_map:
                return name_map[raw_name]
            return raw_name.replace('_', ' ')

    def explain_instance(self, X_instance_trans, raw_feature_dict=None):
        """
        Explains a single prediction vector.
        X_instance_trans: 2D numpy array (1, num_features)
        """
        shap_vals = self.explainer(X_instance_trans)
        
        if hasattr(shap_vals, 'values'):
            vals = shap_vals.values[0]
            base_val = float(shap_vals.base_values[0]) if hasattr(shap_vals.base_values, '__len__') else float(shap_vals.base_values)
        else:
            vals = shap_vals[0]
            base_val = float(self.explainer.expected_value)
            
        predicted_val = base_val + float(np.sum(vals))
        x_row = X_instance_trans[0]
        
        contributions = []
        for idx, (feat_name, val) in enumerate(zip(self.feature_names, vals)):
            x_v = x_row[idx]
            
            # Root Cause Fix: Filter out unactivated OHE baseline zero categories
            if feat_name.startswith('District_') and x_v == 0:
                continue
            if feat_name.startswith('Soil_Type_') and x_v == 0:
                continue

            clean_label = self._format_feature_name(feat_name)
            raw_v = raw_feature_dict.get(feat_name, None) if raw_feature_dict else None
            
            contributions.append({
                'feature': clean_label,
                'raw_feature_name': feat_name,
                'shap_value': round(float(val), 4),
                'direction': 'positive' if val > 0 else 'negative',
                'magnitude': round(float(abs(val)), 4),
                'feature_value': raw_v
            })
            
        # Separate positive and negative contributors
        positive_contributors = sorted([c for c in contributions if c['shap_value'] > 0], key=lambda x: x['shap_value'], reverse=True)
        negative_contributors = sorted([c for c in contributions if c['shap_value'] < 0], key=lambda x: x['shap_value'])
        
        return {
            'base_value': round(base_val, 4),
            'predicted_yield': round(predicted_val, 4),
            'top_positive_contributors': positive_contributors[:5],
            'top_negative_contributors': negative_contributors[:5],
            'all_contributions': contributions
        }

    def compute_global_importance(self):
        train_data = joblib.load('data/processed/train_data.joblib')
        X_train = train_data['X']
        
        shap_vals = self.explainer(X_train)
        values = shap_vals.values if hasattr(shap_vals, 'values') else shap_vals
        
        mean_abs_shap = np.abs(values).mean(axis=0)
        
        importance_list = []
        for name, score in zip(self.feature_names, mean_abs_shap):
            importance_list.append({
                'feature': self._format_feature_name(name),
                'mean_abs_shap': round(float(score), 4)
            })
            
        importance_list.sort(key=lambda x: x['mean_abs_shap'], reverse=True)
        
        os.makedirs('outputs/metrics', exist_ok=True)
        with open('outputs/metrics/shap_global_summary.json', 'w') as f:
            json.dump(importance_list, f, indent=4)
            
        return importance_list

if __name__ == '__main__':
    explainer = YieldShapExplainer()
    sample_trans = np.zeros((1, len(explainer.feature_names)))
    sample_trans[0, explainer.feature_names.index('District_Chennai')] = 1.0
    res = explainer.explain_instance(sample_trans)
    print("Filtered SHAP explanation for Chennai:")
    print("Top Positive:", res['top_positive_contributors'])
    print("Top Negative:", res['top_negative_contributors'])

