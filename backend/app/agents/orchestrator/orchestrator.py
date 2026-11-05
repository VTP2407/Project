import time
import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.agents.agent_types import AgentExecutionResult
from app.agents.specialized_agents import (
    PatientContextAgent,
    HealthAssessmentAgent,
    KnowledgeAgent,
    LifestyleAdvisorAgent,
    MonitoringAgent,
    SafetyAgent,
    ReportAgent
)
from app.models.entities import AgentExecution

class OrchestratorAgent:
    """
    Central multi-agent coordinator: classifies intent, executes conditional routing,
    gathers agent outputs, synthesizes final clinical education response, and logs execution.
    """
    
    def __init__(self):
        self.patient_context_agent = PatientContextAgent()
        self.health_assessment_agent = HealthAssessmentAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.lifestyle_advisor_agent = LifestyleAdvisorAgent()
        self.monitoring_agent = MonitoringAgent()
        self.safety_agent = SafetyAgent()
        self.report_agent = ReportAgent()

    def classify_intent(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["ngất", "hôn mê", "co giật", "khẩn cấp", "cấp cứu", "khó thở dữ dội"]):
            return "emergency"
        elif any(w in q for w in ["đo", "đường huyết", "mg/dl", "hôm nay", "chỉ số"]):
            return "measurement_concern"
        elif any(w in q for w in ["nguy cơ", "đánh giá", "mắc bệnh", "dự đoán", "hba1c"]):
            return "risk_assessment"
        elif any(w in q for w in ["báo cáo", "tổng hợp", "thống kê", "xu hướng"]):
            return "report_summary"
        elif any(w in q for w in ["ăn", "dinh dưỡng", "thể thao", "tập luyện", "chạy bộ", "lối sống"]):
            return "lifestyle_query"
        else:
            return "general_medical_query"

    def process_request(self, db: Session, user_id: int, query: str, conversation_id: int = None) -> Dict[str, Any]:
        start_overall = time.time()
        intent = self.classify_intent(query)
        
        timeline: List[AgentExecutionResult] = []
        active_agent_ids: List[str] = []
        citations = []
        alerts_triggered = []
        
        context: Dict[str, Any] = {
            "db": db,
            "user_id": user_id,
            "user_query": query,
            "conversation_id": conversation_id
        }
        
        # 1. Step 1: Patient Context Agent (always needed for patient personal context)
        step_ctx = self.patient_context_agent.execute(context)
        timeline.append(step_ctx)
        active_agent_ids.append(self.patient_context_agent.agent_id)
        context["patient_context"] = step_ctx.data
        
        # 2. Step 2: Conditional routing based on intent
        if intent == "emergency":
            # Direct to safety emergency alert
            alerts_triggered.append("Kích hoạt giao thức cấp cứu khẩn cấp.")
            
        elif intent == "measurement_concern":
            # Extract possible glucose number from query
            match = re.search(r"(\d+(\.\d+)?)", query)
            if match:
                context["measurement_value"] = float(match.group(1))
                
            step_mon = self.monitoring_agent.execute(context)
            timeline.append(step_mon)
            active_agent_ids.append(self.monitoring_agent.agent_id)
            if step_mon.data.get("alerts"):
                for a in step_mon.data["alerts"]:
                    alerts_triggered.append(a["message"])
                    
            step_kb = self.knowledge_agent.execute(context)
            timeline.append(step_kb)
            active_agent_ids.append(self.knowledge_agent.agent_id)
            citations = step_kb.data.get("citations", [])
            context["kb_context"] = step_kb.data.get("context_text", "")
            
            step_life = self.lifestyle_advisor_agent.execute(context)
            timeline.append(step_life)
            active_agent_ids.append(self.lifestyle_advisor_agent.agent_id)
            context["lifestyle_tips"] = step_life.data.get("lifestyle_tips", [])
            
        elif intent == "risk_assessment":
            step_assess = self.health_assessment_agent.execute(context)
            timeline.append(step_assess)
            active_agent_ids.append(self.health_assessment_agent.agent_id)
            context["assessment_result"] = step_assess.data
            
            step_kb = self.knowledge_agent.execute(context)
            timeline.append(step_kb)
            active_agent_ids.append(self.knowledge_agent.agent_id)
            citations = step_kb.data.get("citations", [])
            
            step_life = self.lifestyle_advisor_agent.execute(context)
            timeline.append(step_life)
            active_agent_ids.append(self.lifestyle_advisor_agent.agent_id)
            context["lifestyle_tips"] = step_life.data.get("lifestyle_tips", [])
            
        elif intent == "report_summary":
            step_rep = self.report_agent.execute(context)
            timeline.append(step_rep)
            active_agent_ids.append(self.report_agent.agent_id)
            context["report_summary"] = step_rep.data
            
        else: # general_medical_query & lifestyle_query
            step_kb = self.knowledge_agent.execute(context)
            timeline.append(step_kb)
            active_agent_ids.append(self.knowledge_agent.agent_id)
            citations = step_kb.data.get("citations", [])
            context["kb_context"] = step_kb.data.get("context_text", "")
            
            step_life = self.lifestyle_advisor_agent.execute(context)
            timeline.append(step_life)
            active_agent_ids.append(self.lifestyle_advisor_agent.agent_id)
            context["lifestyle_tips"] = step_life.data.get("lifestyle_tips", [])

        # 3. Synthesize Draft Clinical Education Response
        draft_response = self._synthesize_response(intent, query, context)
        context["draft_text"] = draft_response
        
        # 4. Step Final: Safety Agent Validation (Mandatory for ALL pathways)
        step_safety = self.safety_agent.execute(context)
        timeline.append(step_safety)
        active_agent_ids.append(self.safety_agent.agent_id)
        
        final_text = step_safety.data.get("final_validated_text", draft_response)
        if step_safety.data.get("emergency_alert"):
            alerts_triggered.insert(0, step_safety.data["emergency_alert"])
            
        total_duration_ms = round((time.time() - start_overall) * 1000, 2)
        
        # 5. Persist Execution History in DB
        execution_log = AgentExecution(
            user_id=user_id,
            conversation_id=conversation_id,
            user_query=query,
            status="SUCCESS",
            total_duration_ms=total_duration_ms,
            execution_timeline_json=[
                {
                    "agent_id": t.agent_id,
                    "agent_name": t.agent_name,
                    "status": t.status,
                    "duration_ms": t.duration_ms,
                    "action_summary": t.summary
                }
                for t in timeline
            ],
            final_response=final_text
        )
        db.add(execution_log)
        db.commit()
        
        return {
            "reply": final_text,
            "intent_detected": intent,
            "active_agents": active_agent_ids,
            "citations": citations,
            "alerts_triggered": alerts_triggered,
            "timeline": [
                {
                    "agent_id": t.agent_id,
                    "agent_name": t.agent_name,
                    "status": t.status,
                    "duration_ms": t.duration_ms,
                    "action_summary": t.summary,
                    "output_preview": t.summary
                }
                for t in timeline
            ],
            "total_duration_ms": total_duration_ms
        }

    def _synthesize_response(self, intent: str, query: str, context: Dict[str, Any]) -> str:
        pt = context.get("patient_context", {})
        kb = context.get("kb_context", "")
        tips = context.get("lifestyle_tips", [])
        assess = context.get("assessment_result", {})
        rep = context.get("report_summary", {})
        
        sections = []
        
        if intent == "emergency":
            return (
                "🚨 **CẢNH BÁO TÌNH HUỐNG Y TẾ KHẨN CẤP**\n\n"
                "Nếu bạn hoặc người thân đang có dấu hiệu hôn mê, co giật, khó thở dữ dội hoặc mất ý thức:\n"
                "1. **GỌI NGAY CẤP CỨU 115** hoặc đưa đến phòng cấp cứu bệnh viện gần nhất.\n"
                "2. Đặt người bệnh nằm nghiêng an toàn, không cố ép ăn uống khi mất tri giác.\n"
                "3. Mang theo sổ khám bệnh và các loại thuốc đang dùng."
            )
            
        elif intent == "measurement_concern":
            val = context.get("measurement_value") or pt.get("latest_glucose")
            sections.append(f"Chào bạn, hệ thống đã phân tích chỉ số đường huyết được ghi nhận (**{val or 'gần đây'} mg/dL**).")
            if val and float(val) >= 126.0:
                sections.append(
                    "⚠️ **Đánh giá Lâm sàng**: Chỉ số này cao hơn ngưỡng khuyến cáo lúc đói của Hiệp hội Đái tháo đường Hoa Kỳ (ADA >= 126 mg/dL). "
                    "Tình trạng tăng đường huyết kéo dài có thể gây tổn thương mạch máu nhỏ và thận."
                )
            elif val and float(val) < 70.0:
                sections.append("⚠️ **Cảnh báo**: Mức đường huyết dưới 70 mg/dL thuộc tình trạng hạ đường huyết cấp tính.")
            else:
                sections.append("✅ Chỉ số của bạn hiện duy trì trong ngưỡng mục tiêu kiểm soát an toàn.")
                
            if kb:
                sections.append(f"📚 **Tham chiếu Y khoa Chuẩn**:\n{kb}")
            if tips:
                sections.append("💡 **Khuyến nghị Giáo dục Lối sống**:\n" + "\n".join(f"- {t}" for t in tips))
                
        elif intent == "risk_assessment":
            sections.append("📊 **KẾT QUẢ ĐÁNH GIÁ NGUY CƠ ĐÁI THÁO ĐƯỜNG (AI SCREENING)**")
            sections.append(
                f"- **Mô hình**: {assess.get('model_name', 'XGBoost')} (Phiên bản {assess.get('model_version', '1.0.0')})\n"
                f"- **Kết luận dự báo**: {assess.get('predicted_class')}\n"
                f"- **Mức độ rủi ro**: {assess.get('risk_category')}\n"
                f"- **Xác suất ước tính**: {assess.get('probability', 0)*100:.1f}%\n"
                f"- **Giải thích lâm sàng**: {assess.get('clinical_explanation')}"
            )
            if tips:
                sections.append("💡 **Biện pháp can thiệp sớm**:\n" + "\n".join(f"- {t}" for t in tips))
                
        elif intent == "report_summary":
            sections.append("📈 **BÁO CÁO TỔNG HỢP THEO DÕI SỨC KHỎE**")
            sections.append(
                f"- Tổng số lượt đo ghi nhận: **{rep.get('total_measurements', 0)}** lần.\n"
                f"- Đường huyết trung bình: **{rep.get('mean_glucose', 0)} mg/dL**.\n"
                f"- Dao động từ: **{rep.get('min_glucose', 0)} mg/dL** đến **{rep.get('max_glucose', 0)} mg/dL**.\n"
                f"- Số lần vượt ngưỡng cảnh báo: **{rep.get('abnormal_count', 0)}** lần."
            )
            sections.append("Khuyến nghị duy trì ghi nhật ký đều đặn và xuất tệp dữ liệu để bác sĩ chuyên khoa xem xét trong đợt tái khám định kỳ.")
            
        else: # General medical & lifestyle
            sections.append("Cảm ơn bạn đã đặt câu hỏi cho Trợ lý Đa Tác nhân AI.")
            if kb:
                sections.append(f"📚 **Thông tin Tri thức Y khoa (WHO / ADA)**:\n{kb}")
            else:
                sections.append("Đái tháo đường là bệnh rối loạn chuyển hóa mạn tính đặc trưng bởi mức glucose huyết tương cao, do suy giảm tiết insulin hoặc kháng insulin.")
            if tips:
                sections.append("🥗 **Lời khuyên Dinh dưỡng & Vận động**:\n" + "\n".join(f"- {t}" for t in tips))
                
        return "\n\n".join(sections)

orchestrator = OrchestratorAgent()

