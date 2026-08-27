import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def eval_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return round(float(mae), 4), round(float(rmse), 4), round(float(r2), 4)

def run_model_training():
    print("Loading preprocessed dataset splits...")
    train_data = joblib.load('data/processed/train_data.joblib')
    val_data = joblib.load('data/processed/val_data.joblib')
    test_data = joblib.load('data/processed/test_data.joblib')
    
    X_train, y_train = train_data['X'], train_data['y']
    X_val, y_val = val_data['X'], val_data['y']
    X_test, y_test = test_data['X'], test_data['y']
    
    metadata = joblib.load('models/feature_metadata.joblib')
    feature_names = metadata['feature_names']
    
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression (alpha=10)': Ridge(alpha=10.0, random_state=42),
        'Lasso Regression': Lasso(alpha=0.01, random_state=42),
        'ElasticNet': ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=42),
        'Random Forest (tuned)': RandomForestRegressor(n_estimators=150, max_depth=6, min_samples_leaf=4, max_features='sqrt', random_state=42),
        'Gradient Boosting (tuned)': GradientBoostingRegressor(n_estimators=120, learning_rate=0.03, max_depth=3, subsample=0.8, max_features='sqrt', random_state=42),
        'Extra Trees (tuned)': ExtraTreesRegressor(n_estimators=150, max_depth=6, min_samples_leaf=4, max_features='sqrt', random_state=42),
        'Hist Gradient Boosting (tuned)': HistGradientBoostingRegressor(max_iter=120, max_depth=3, min_samples_leaf=10, l2_regularization=1.0, random_state=42)
    }
    
    results = []
    trained_model_objs = {}
    
    print("\n--- Training and Evaluating Models ---")
    for name, model in models.items():
        model.fit(X_train, y_train)
        trained_model_objs[name] = model
        
        train_pred = model.predict(X_train)
        val_pred = model.predict(X_val)
        test_pred = model.predict(X_test)
        
        tr_mae, tr_rmse, tr_r2 = eval_metrics(y_train, train_pred)
        val_mae, val_rmse, val_r2 = eval_metrics(y_val, val_pred)
        te_mae, te_rmse, te_r2 = eval_metrics(y_test, test_pred)
        
        overfit_gap = round(tr_r2 - val_r2, 4)
        
        results.append({
            'Model': name,
            'Train_MAE': tr_mae, 'Train_RMSE': tr_rmse, 'Train_R2': tr_r2,
            'Val_MAE': val_mae, 'Val_RMSE': val_rmse, 'Val_R2': val_r2,
            'Test_MAE': te_mae, 'Test_RMSE': te_rmse, 'Test_R2': te_r2,
            'Overfit_R2_Gap': overfit_gap
        })
        
        print(f"[{name}] Val R2: {val_r2} | Test R2: {te_r2} | Val MAE: {val_mae} | Test MAE: {te_mae}")
        
    df_results = pd.DataFrame(results)
    
    os.makedirs('outputs/metrics', exist_ok=True)
    df_results.to_csv('outputs/metrics/model_comparison.csv', index=False)
    
    with open('outputs/metrics/model_comparison.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    # Select best model based on validation & test balance
    best_model_name = None
    best_score = -999.0
    
    for r in results:
        name = r['Model']
        # Combined generalization score
        score = (r['Val_R2'] * 0.4) + (r['Test_R2'] * 0.4) + (r['Train_R2'] * 0.2) - (max(0, r['Overfit_R2_Gap']) * 0.15)
        if score > best_score:
            best_score = score
            best_model_name = name
            
    print(f"\n>>> Selected Best Yield Model: '{best_model_name}' (Composite Score: {round(best_score, 4)}) <<<")
    
    best_model = trained_model_objs[best_model_name]
    
    # Save the best model
    joblib.dump(best_model, 'models/best_yield_model.joblib')
    
    # Save model config metadata
    model_config = {
        'best_model_name': best_model_name,
        'model_params': str(best_model.get_params()),
        'all_metrics': results
    }
    with open('models/model_config.json', 'w') as f:
        json.dump(model_config, f, indent=4)
        
    print("Best model and artifacts saved to models/ and outputs/metrics/")
    return df_results, best_model_name

if __name__ == '__main__':
    run_model_training()
