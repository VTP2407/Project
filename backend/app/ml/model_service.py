import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

# Ensure ml directory and training_scripts are on sys.path for unpickling
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml-training", "training_scripts")))

from app.core.config import settings

class ModelService:
    _instance = None
    
    def __init__(self):
        self.ml_model = None
        self.pipeline = None
        self.feature_config = None
        self.metadata = None
        self.shap_importance = None
        self.load_models()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModelService()
        return cls._instance

    def load_models(self):
        model_path = os.path.join(settings.SAVED_MODELS_DIR, "diabetes_model.pkl")
        pipeline_path = os.path.join(settings.SAVED_MODELS_DIR, "preprocessing_pipeline.pkl")
        config_path = os.path.join(settings.SAVED_MODELS_DIR, "feature_config.json")
        meta_path = os.path.join(settings.SAVED_MODELS_DIR, "model_metadata.json")
        shap_path = os.path.join(settings.SAVED_MODELS_DIR, "shap_feature_importance.json")
        
        if os.path.exists(model_path):
            self.ml_model = joblib.load(model_path)
        if os.path.exists(pipeline_path):
            self.pipeline = joblib.load(pipeline_path)
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.feature_config = json.load(f)
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        if os.path.exists(shap_path):
            with open(shap_path, "r", encoding="utf-8") as f:
                self.shap_importance = json.load(f)

    def predict(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates, pre-processes using the exact fitted pipeline, performs inference,
        and returns structured clinical prediction with SHAP feature importance.
        """
        if self.ml_model is None or self.pipeline is None:
            self.load_models()
            if self.ml_model is None:
                raise RuntimeError("ML model is not loaded in backend.")
                
        # Format single record DataFrame
        df_single = pd.DataFrame([{
            "gender": str(feature_data.get("gender", "Female")),
            "age": float(feature_data.get("age", 40.0)),
            "hypertension": int(feature_data.get("hypertension", 0)),
            "heart_disease": int(feature_data.get("heart_disease", 0)),
            "smoking_history": str(feature_data.get("smoking_history", "never")),
            "bmi": float(feature_data.get("bmi", 25.0)),
            "HbA1c_level": float(feature_data.get("HbA1c_level", 5.5)),
            "blood_glucose_level": float(feature_data.get("blood_glucose_level", 110.0))
        }])
        
        # Transform using exact fitted preprocessing pipeline
        X_scaled = self.pipeline.transform(df_single)
        
        # Inference
        pred = int(self.ml_model.predict(X_scaled)[0])
        if hasattr(self.ml_model, "predict_proba"):
            prob = float(self.ml_model.predict_proba(X_scaled)[0, 1])
        else:
            prob = float(pred)
            
        # Determine clinical risk category
        if prob < 0.20:
            risk_category = "Thấp (Nguy cơ tối thiểu)"
        elif prob < 0.50:
            risk_category = "Trung bình (Tiền đái tháo đường / Cần theo dõi)"
        elif prob < 0.80:
            risk_category = "Cao (Nguy cơ Đái tháo đường rõ rệt)"
        else:
            risk_category = "Rất cao (Khả năng cao mắc Đái tháo đường)"
            
        pred_class = "DƯƠNG TÍNH (Nguy cơ Đái tháo đường)" if pred == 1 or prob >= 0.5 else "ÂM TÍNH (Bình thường)"
        
        # Clinical explanation synthesis
        hba1c = float(feature_data.get("HbA1c_level", 5.5))
        glucose = float(feature_data.get("blood_glucose_level", 110.0))
        bmi = float(feature_data.get("bmi", 25.0))
        
        reasons = []
        if hba1c >= 6.5:
            reasons.append(f"HbA1c ({hba1c}%) vượt ngưỡng chẩn đoán đái tháo đường (>= 6.5%).")
        elif hba1c >= 5.7:
            reasons.append(f"HbA1c ({hba1c}%) nằm trong khoảng tiền đái tháo đường (5.7 - 6.4%).")
            
        if glucose >= 126:
            reasons.append(f"Chỉ số đường huyết ({glucose} mg/dL) vượt ngưỡng chẩn đoán chuẩn ADA.")
        elif glucose >= 100:
            reasons.append(f"Chỉ số đường huyết ({glucose} mg/dL) ở mức rối loạn dung nạp đường đói.")
            
        if bmi >= 25:
            reasons.append(f"BMI ({bmi:.1f} kg/m²) thuộc nhóm thừa cân/béo phì, gia tăng tình trạng kháng insulin.")
            
        explanation = " ".join(reasons) if reasons else "Các chỉ số chuyển hóa và sinh học nằm trong giới hạn kiểm soát bình thường."
        
        return {
            "prediction": pred,
            "predicted_class": pred_class,
            "probability": round(prob, 4),
            "confidence_pct": round(prob * 100, 1) if pred == 1 else round((1 - prob) * 100, 1),
            "risk_category": risk_category,
            "model_name": self.metadata.get("model_name", "XGBoost") if self.metadata else "XGBoost",
            "model_version": self.metadata.get("version", "1.0.0") if self.metadata else "1.0.0",
            "feature_importance": self.shap_importance or (self.feature_config.get("feature_importance", {}) if self.feature_config else {}),
            "clinical_explanation": explanation,
            "limitations": "Mô hình học máy được huấn luyện trên tập dữ liệu hồi cứu (diabetes_prediction_dataset.csv) nhằm mục đích sàng lọc hỗ trợ, KHÔNG thay thế xét nghiệm chẩn đoán lâm sàng của bác sĩ."
        }

model_service = ModelService.get_instance()
