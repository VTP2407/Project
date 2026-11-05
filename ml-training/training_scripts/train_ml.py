import os
import sys
import json
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add training_scripts to path
sys.path.append(os.path.dirname(__file__))
from data_loader import prepare_splits, SAVED_MODELS_DIR, FEATURE_COLUMNS, TARGET_COLUMN

BACKEND_SAVED_MODELS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app", "ml", "saved_models")
)

def train_and_evaluate_ml():
    print("Preparing dataset splits from diabetes_prediction_dataset.csv...")
    data = prepare_splits()
    
    pipeline = data["pipeline"]
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    X_test, y_test = data["X_test"], data["y_test"]
    
    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, eval_metric="logloss"
        ),
    }
    
    results = {}
    fitted_models = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        fitted_models[name] = model
        
        # Predict on validation
        y_val_pred = model.predict(X_val)
        y_val_prob = model.predict_proba(X_val)[:, 1] if hasattr(model, "predict_proba") else y_val_pred
        
        acc = float(accuracy_score(y_val, y_val_pred))
        prec = float(precision_score(y_val, y_val_pred, zero_division=0))
        rec = float(recall_score(y_val, y_val_pred))
        f1 = float(f1_score(y_val, y_val_pred))
        auc = float(roc_auc_score(y_val, y_val_prob))
        
        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": auc,
        }
        print(f"  {name} -> Acc: {acc:.4f}, Prec: {prec:.4f}, Rec: {rec:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}")

    # Select best model based on F1-score on minority class
    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best_model = fitted_models[best_name]
    print(f"\nBest Model selected: {best_name} (F1: {results[best_name]['f1_score']:.4f})")
    
    # Evaluate best model on Test set
    y_test_pred = best_model.predict(X_test)
    y_test_prob = best_model.predict_proba(X_test)[:, 1] if hasattr(best_model, "predict_proba") else y_test_pred
    
    test_metrics = {
        "accuracy": float(accuracy_score(y_test, y_test_pred)),
        "precision": float(precision_score(y_test, y_test_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_test_pred)),
        "f1_score": float(f1_score(y_test, y_test_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_test_prob)),
    }
    print(f"Test Set Performance of {best_name}: {test_metrics}")

    # Feature Importance (if tree-based)
    feature_importance = {}
    if hasattr(best_model, "feature_importances_"):
        for col, imp in zip(FEATURE_COLUMNS, best_model.feature_importances_):
            feature_importance[col] = float(imp)
    elif hasattr(best_model, "coef_"):
        for col, imp in zip(FEATURE_COLUMNS, best_model.coef_[0]):
            feature_importance[col] = float(abs(imp))

    feature_config = {
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "categorical_columns": ["gender", "smoking_history"],
        "numerical_columns": ["age", "hypertension", "heart_disease", "bmi", "HbA1c_level", "blood_glucose_level"],
        "gender_classes": list(pipeline.le_gender.classes_),
        "smoking_classes": list(pipeline.le_smoke.classes_),
        "feature_importance": feature_importance
    }

    model_metadata = {
        "model_name": best_name,
        "model_type": "scikit-learn / ensemble",
        "version": "1.0.0",
        "dataset_name": "diabetes_prediction_dataset.csv",
        "dataset_sha256": "F233FC470E904201F35310D061CB46CA0A6BC7CA5C3E428B769FB4F87F69929B",
        "trained_date": "2026-11-05",
        "best_hyperparameters": str(best_model.get_params()),
        "validation_comparison": results,
        "test_metrics": test_metrics
    }

    # Save artifacts to both ml-training/saved_models and backend/app/ml/saved_models
    for out_dir in [SAVED_MODELS_DIR, BACKEND_SAVED_MODELS_DIR]:
        os.makedirs(out_dir, exist_ok=True)
        joblib.dump(best_model, os.path.join(out_dir, "diabetes_model.pkl"))
        pipeline.save(os.path.join(out_dir, "preprocessing_pipeline.pkl"))
        with open(os.path.join(out_dir, "feature_config.json"), "w", encoding="utf-8") as f:
            json.dump(feature_config, f, indent=2)
        with open(os.path.join(out_dir, "model_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(model_metadata, f, indent=2)
        with open(os.path.join(out_dir, "evaluation_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(test_metrics, f, indent=2)

    print(f"Saved artifacts to {SAVED_MODELS_DIR} and {BACKEND_SAVED_MODELS_DIR}")
    return best_model, pipeline, model_metadata, test_metrics

if __name__ == "__main__":
    train_and_evaluate_ml()

