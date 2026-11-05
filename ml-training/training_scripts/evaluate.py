import os
import sys
import json
import joblib
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, precision_recall_curve, auc
import shap

sys.path.append(os.path.dirname(__file__))
from data_loader import prepare_splits, SAVED_MODELS_DIR, FEATURE_COLUMNS
from train_dl import DiabetesMLP

def run_evaluation():
    print("Running comprehensive model evaluation and SHAP analysis...")
    data = prepare_splits()
    X_test, y_test = data["X_test"], data["y_test"]
    pipeline = data["pipeline"]
    
    # 1. Load ML Best Model
    ml_model_path = os.path.join(SAVED_MODELS_DIR, "diabetes_model.pkl")
    ml_model = joblib.load(ml_model_path)
    
    # ML predictions
    y_pred_ml = ml_model.predict(X_test)
    y_prob_ml = ml_model.predict_proba(X_test)[:, 1] if hasattr(ml_model, "predict_proba") else y_pred_ml
    
    print("\n=== Machine Learning Model Report ===")
    print(classification_report(y_test, y_pred_ml, target_names=["Non-Diabetic", "Diabetic"]))
    
    # 2. Load PyTorch DL Model
    dl_model_path = os.path.join(SAVED_MODELS_DIR, "diabetes_dl_model.pth")
    dl_model = DiabetesMLP(input_dim=X_test.shape[1])
    dl_model.load_state_dict(torch.load(dl_model_path))
    dl_model.eval()
    
    with torch.no_grad():
        dl_logits = dl_model(torch.tensor(X_test, dtype=torch.float32))
        y_prob_dl = torch.sigmoid(dl_logits).numpy().flatten()
        y_pred_dl = (y_prob_dl >= 0.5).astype(int)
        
    print("\n=== PyTorch Deep Learning Model Report ===")
    print(classification_report(y_test, y_pred_dl, target_names=["Non-Diabetic", "Diabetic"]))
    
    # 3. SHAP Explainability on ML model (TreeExplainer or LinearExplainer or KernelExplainer)
    print("\nComputing SHAP values for model explainability...")
    sample_size = min(500, len(X_test))
    X_sample = X_test[:sample_size]
    
    try:
        explainer = shap.TreeExplainer(ml_model)
        shap_values = explainer.shap_values(X_sample)
        # TreeExplainer might return list for multi-class [class 0, class 1]
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]
    except Exception as e:
        print(f"TreeExplainer fallback to Explainer: {e}")
        explainer = shap.Explainer(ml_model.predict, X_sample)
        shap_values = explainer(X_sample).values

    mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
    shap_importance = {col: float(val) for col, val in zip(FEATURE_COLUMNS, mean_abs_shap)}
    sorted_shap = dict(sorted(shap_importance.items(), key=lambda item: item[1], reverse=True))
    
    print("SHAP Global Feature Importance:")
    for feat, imp in sorted_shap.items():
        print(f"  {feat}: {imp:.4f}")
        
    shap_summary_path = os.path.join(SAVED_MODELS_DIR, "shap_feature_importance.json")
    with open(shap_summary_path, "w", encoding="utf-8") as f:
        json.dump(sorted_shap, f, indent=2)

    return {
        "ml_report": classification_report(y_test, y_pred_ml, output_dict=True),
        "dl_report": classification_report(y_test, y_pred_dl, output_dict=True),
        "shap_importance": sorted_shap
    }

if __name__ == "__main__":
    run_evaluation()
