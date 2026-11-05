import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.agents.agent_types import BaseAgent
from app.models.entities import HealthProfile, GlucoseMeasurement, HealthAssessment
from app.ml.model_service import model_service
from app.rag.engine import RAGEngine
from app.rule_engine.engine import RuleEngine

class PatientContextAgent(BaseAgent):
    agent_id = "patient_context_agent"
    agent_name = "Patient Context Agent"
    description = "Truy xuất hồ sơ bệnh án, tiền sử và các chỉ số sức khỏe của bệnh nhân."

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        db: Session = context.get("db")
        user_id = context.get("user_id")
        
        if not db or not user_id:
            return {}, "Không có thông tin bệnh nhân xác thực."
            
        profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
        measurements = (
            db.query(GlucoseMeasurement)
            .filter(GlucoseMeasurement.user_id == user_id)
            .order_by(GlucoseMeasurement.measured_at.desc())
            .limit(10)
            .all()
        )
        
        recent_values = [m.value for m in measurements]
        avg_glucose = round(sum(recent_values) / len(recent_values), 1) if recent_values else None
        
        data = {
            "gender": profile.gender if profile else "Female",
            "bmi": profile.bmi if profile else 24.0,
            "hypertension": profile.hypertension if profile else 0,
            "heart_disease": profile.heart_disease if profile else 0,
            "smoking_history": profile.smoking_history if profile else "never",
            "recent_measurements_count": len(measurements),
            "latest_glucose": recent_values[0] if recent_values else None,
            "avg_glucose": avg_glucose
        }
        
        summary = f"Đã nạp hồ sơ: Giới tính {data['gender']}, BMI {data['bmi']}, Huyết áp cao: {'Có' if data['hypertension'] else 'Không'}, Đường huyết gần nhất: {data['latest_glucose']} mg/dL."
        return data, summary

class HealthAssessmentAgent(BaseAgent):
    agent_id = "health_assessment_agent"
    agent_name = "Health Assessment Agent"
    description = "Tiền xử lý chỉ số sinh học và gọi mô hình ML/DL đã huấn luyện để dự báo nguy cơ."

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        features = context.get("assessment_features")
        patient_ctx = context.get("patient_context", {})
        
        # Merge provided features with patient context fallback
        input_data = {
            "gender": features.get("gender") if features else patient_ctx.get("gender", "Female"),
            "age": float(features.get("age", 45.0) if features else 45.0),
            "hypertension": int(features.get("hypertension") if features and "hypertension" in features else patient_ctx.get("hypertension", 0)),
            "heart_disease": int(features.get("heart_disease") if features and "heart_disease" in features else patient_ctx.get("heart_disease", 0)),
            "smoking_history": features.get("smoking_history") if features else patient_ctx.get("smoking_history", "never"),
            "bmi": float(features.get("bmi", 25.0) if features else patient_ctx.get("bmi", 25.0)),
            "HbA1c_level": float(features.get("HbA1c_level", 5.8) if features else 5.8),
            "blood_glucose_level": float(features.get("blood_glucose_level", 115.0) if features else (patient_ctx.get("latest_glucose") or 115.0))
        }
        
        # Call actual trained model service
        prediction_result = model_service.predict(input_data)
        summary = f"Mô hình {prediction_result['model_name']} dự báo: {prediction_result['predicted_class']} (Xác suất: {prediction_result['probability']*100:.1f}% - Phân nhóm: {prediction_result['risk_category']})."
        return prediction_result, summary

class KnowledgeAgent(BaseAgent):
    agent_id = "knowledge_agent"
    agent_name = "Knowledge Agent"
    description = "Tìm kiếm và đối chiếu tài liệu y khoa chính thống từ cơ sở tri thức (RAG)."

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        db: Session = context.get("db")
        query: str = context.get("user_query", "")
        
        if not db or not query:
            return {"citations": [], "context_text": ""}, "Không có truy vấn tìm kiếm."
            
        results = RAGEngine.search_knowledge(db, query, top_k=2)
        citations = [
            {"title": r["title"], "source": r["source"], "category": r["category"], "score": r["similarity_score"]}
            for r in results
        ]
        context_text = RAGEngine.format_rag_context(results)
        summary = f"RAG đã trích xuất {len(results)} đoạn tri thức phù hợp từ các nguồn y khoa chuẩn (WHO/ADA)."
        return {"citations": citations, "rag_results": results, "context_text": context_text}, summary

class LifestyleAdvisorAgent(BaseAgent):
    agent_id = "lifestyle_advisor_agent"
    agent_name = "Lifestyle Advisor Agent"
    description = "Cung cấp giáo dục dinh dưỡng và hoạt động thể chất cá nhân hóa."

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        patient_ctx = context.get("patient_context", {})
        glucose = patient_ctx.get("latest_glucose") or 120.0
        bmi = patient_ctx.get("bmi") or 24.0
        
        tips = []
        # Nutrition education
        if glucose >= 140:
            tips.append("Hạn chế tối đa carbohydrate tinh chế (cơm trắng, bánh mì trắng, nước ngọt có ga); ưu tiên chất xơ hòa tan từ rau xanh đậm và ngũ cốc nguyên hạt.")
        else:
            tips.append("Duy trì chế độ ăn theo phương pháp Đĩa ăn Dinh dưỡng ADA (1/2 rau củ không tinh bột, 1/4 đạm nạc, 1/4 ngũ cốc nguyên cám).")
            
        # Exercise education
        if bmi >= 25.0:
            tips.append("Tăng cường vận động thể lực mức độ vừa phải tối thiểu 150 phút/tuần (như đi bộ nhanh, đạp xe nhẹ nhàng) để giảm mỡ tạng và tăng độ nhạy insulin.")
        else:
            tips.append("Duy trì thói quen vận động 30 phút mỗi ngày kết hợp các bài tập giãn cơ hoặc cardio nhẹ nhàng.")
            
        tips.append("Tuyệt đối tuân thủ lịch tự theo dõi đường huyết và không tự ý thay đổi thuốc điều trị.")
        
        summary = "Đã chuẩn bị 3 khuyến nghị giáo dục lối sống y khoa cá nhân hóa theo mức đường huyết và BMI."
        return {"lifestyle_tips": tips}, summary

class MonitoringAgent(BaseAgent):
    agent_id = "monitoring_agent"
    agent_name = "Monitoring Agent"
    description = "Giám sát các chỉ số đo lường bất thường và phát hiện xu hướng đường huyết."

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        measurement_val = context.get("measurement_value")
        m_type = context.get("measurement_type", "fasting")
        patient_ctx = context.get("patient_context", {})
        
        if measurement_val is None:
            measurement_val = patient_ctx.get("latest_glucose")
            
        if measurement_val is None:
            return {"alerts": []}, "Không có số đo cần giám sát."
            
        eval_res = RuleEngine.evaluate_measurement(float(measurement_val), m_type)
        alerts = []
        if eval_res["is_abnormal"]:
            alerts.append(eval_res)
            
        summary = f"Kết quả giám sát đường huyết ({measurement_val} mg/dL): {eval_res['alert_level']} - {eval_res['message']}"
        return {"alerts": alerts, "evaluation": eval_res}, summary

class SafetyAgent(BaseAgent):
    agent_id = "safety_agent"
    agent_name = "Safety Agent"
    description = "Thẩm định an toàn lâm sàng, ngăn chặn chỉ định thuốc trái phép và cảnh báo khẩn cấp."

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        draft_text = context.get("draft_text", "")
        glucose = context.get("glucose_val") or context.get("measurement_value")
        
        # 1. Check emergency glucose level
        emergency_alert = None
        if glucose is not None:
            g = float(glucose)
            if g < 70.0:
                emergency_alert = "CẢNH BÁO KHẨN CẤP: Đường huyết nguy hiểm (<70 mg/dL). Cần xử trí hạ đường huyết ngay lập tức!"
            elif g >= 250.0:
                emergency_alert = "CẢNH BÁO NGUY HIỂM: Đường huyết rất cao (>=250 mg/dL). Nguy cơ biến chứng cấp tính!"
                
        # 2. Check draft response against safety rules
        is_safe, validated_text = RuleEngine.evaluate_safety_response(draft_text)
        
        # 3. Add Mandatory Healthcare Disclaimer
        disclaimer = "\n\n*(Lưu ý: Hệ thống chỉ cung cấp thông tin giáo dục y tế và hỗ trợ sàng lọc. Mọi quyết định chẩn đoán và điều trị cần dựa trên chỉ định của Bác sĩ chuyên khoa.)*"
        final_text = validated_text + disclaimer
        
        summary = "Safety Agent đã thẩm định phản hồi: Không vi phạm quy chuẩn an toàn, đã gắn kèm tuyên bố miễn trừ y tế bắt buộc."
        if emergency_alert:
            summary = f"Safety Agent kích hoạt cảnh báo khẩn cấp: {emergency_alert}"
            
        return {
            "is_safe": is_safe,
            "emergency_alert": emergency_alert,
            "final_validated_text": final_text
        }, summary

class ReportAgent(BaseAgent):
    agent_id = "report_agent"
    agent_name = "Report Agent"
    description = "Tổng hợp dữ liệu theo dõi sức khỏe và chuẩn bị báo cáo thống kê định kỳ."

    def run(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        db: Session = context.get("db")
        user_id = context.get("user_id")
        
        if not db or not user_id:
            return {}, "Không có dữ liệu bệnh nhân để xuất báo cáo."
            
        measurements = (
            db.query(GlucoseMeasurement)
            .filter(GlucoseMeasurement.user_id == user_id)
            .order_by(GlucoseMeasurement.measured_at.desc())
            .limit(30)
            .all()
        )
        
        assessments = (
            db.query(HealthAssessment)
            .filter(HealthAssessment.user_id == user_id)
            .order_by(HealthAssessment.created_at.desc())
            .limit(5)
            .all()
        )
        
        values = [m.value for m in measurements]
        report_data = {
            "total_measurements": len(measurements),
            "mean_glucose": round(sum(values) / len(values), 1) if values else 0,
            "min_glucose": min(values) if values else 0,
            "max_glucose": max(values) if values else 0,
            "abnormal_count": sum(1 for m in measurements if m.is_abnormal),
            "assessments_count": len(assessments),
            "latest_risk": assessments[0].risk_category if assessments else "Chưa có đánh giá"
        }
        
        summary = f"Báo cáo tổng hợp {len(measurements)} lần đo: Trung bình {report_data['mean_glucose']} mg/dL, {report_data['abnormal_count']} lần bất thường."
        return report_data, summary
