import re
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.entities import RuleModel, RuleExecutionLog

DEFAULT_CLINICAL_RULES = [
    {
        "rule_id": "RULE_SAFE_001",
        "rule_name": "Emergency Hypoglycemia Detection",
        "category": "safety",
        "priority": 1,
        "is_immutable": True,
        "description": "Trigger urgent alert when blood glucose is below 70 mg/dL (severe risk of hypoglycemia shock).",
        "conditions_json": {"field": "blood_glucose_level", "operator": "<", "value": 70.0},
        "actions_json": {
            "severity": "EMERGENCY",
            "action": "TRIGGER_ALERT",
            "message": "CẢNH BÁO KHẨN CẤP: Đường huyết dưới 70 mg/dL (Hạ đường huyết). Hãy nạp ngay 15g carbohydrate tác dụng nhanh (1/2 ly nước trái cây hoặc 3-4 viên đường) và kiểm tra lại sau 15 phút. Nếu hôn mê hoặc lú lẫn, gọi cấp cứu 115 ngay lập tức!"
        }
    },
    {
        "rule_id": "RULE_SAFE_002",
        "rule_name": "Emergency Hyperglycemia / Ketoacidosis Warning",
        "category": "safety",
        "priority": 1,
        "is_immutable": True,
        "description": "Trigger urgent alert when blood glucose exceeds 250 mg/dL (risk of DKA or HHS).",
        "conditions_json": {"field": "blood_glucose_level", "operator": ">=", "value": 250.0},
        "actions_json": {
            "severity": "EMERGENCY",
            "action": "TRIGGER_ALERT",
            "message": "CẢNH BÁO NGUY HIỂM: Đường huyết rất cao (>= 250 mg/dL). Nguy cơ nhiễm toan ceton đái tháo đường (DKA) hoặc tăng áp lực thẩm thấu. Hãy uống nhiều nước, kiểm tra ceton niệu và đến ngay cơ sở y tế gần nhất!"
        }
    },
    {
        "rule_id": "RULE_MON_001",
        "rule_name": "ADA Fasting Glucose Diagnostic Screening",
        "category": "monitoring",
        "priority": 3,
        "is_immutable": False,
        "description": "Evaluate fasting blood glucose threshold based on ADA clinical standards.",
        "conditions_json": {"field": "blood_glucose_level", "operator": ">=", "value": 126.0},
        "actions_json": {
            "severity": "WARNING",
            "action": "NOTIFY",
            "message": "Đường huyết đói >= 126 mg/dL nằm trong ngưỡng chẩn đoán đái tháo đường của Hiệp hội Đái tháo đường Hoa Kỳ (ADA). Cần làm xét nghiệm lặp lại để xác nhận."
        }
    },
    {
        "rule_id": "RULE_MON_002",
        "rule_name": "ADA HbA1c Diabetic Threshold",
        "category": "monitoring",
        "priority": 3,
        "is_immutable": False,
        "description": "Evaluate HbA1c >= 6.5% standard.",
        "conditions_json": {"field": "HbA1c_level", "operator": ">=", "value": 6.5},
        "actions_json": {
            "severity": "WARNING",
            "action": "NOTIFY",
            "message": "Chỉ số HbA1c >= 6.5% phản ánh nồng độ đường huyết trung bình 3 tháng qua ở ngưỡng đái tháo đường. Khuyến nghị thăm khám bác sĩ chuyên khoa nội tiết."
        }
    },
    {
        "rule_id": "RULE_MON_003",
        "rule_name": "ADA Impaired Fasting Glucose (Prediabetes)",
        "category": "monitoring",
        "priority": 5,
        "is_immutable": False,
        "description": "Detect prediabetes fasting glucose 100 - 125 mg/dL.",
        "conditions_json": {"field": "blood_glucose_level", "operator": "range", "min": 100.0, "max": 125.0},
        "actions_json": {
            "severity": "INFO",
            "action": "NOTIFY",
            "message": "Chỉ số đường huyết đói 100-125 mg/dL thuộc mức tiền đái tháo đường (Rối loạn dung nạp đường huyết đói). Thay đổi lối sống và dinh dưỡng có thể đẩy lùi tiến triển thành bệnh."
        }
    },
    {
        "rule_id": "RULE_SAFE_PRESCRIPTION",
        "rule_name": "Block Prohibited Medication Prescription",
        "category": "safety",
        "priority": 1,
        "is_immutable": True,
        "description": "Strictly block any agent or LLM from prescribing drug dosages (e.g. insulin units, metformin milligrams).",
        "conditions_json": {"field": "response_text", "operator": "regex", "pattern": r"(uống|tiêm|dùng|liều)\s+\d+\s*(viên|mg|đơn vị|units|ml)"},
        "actions_json": {
            "severity": "CRITICAL",
            "action": "BLOCK_RESPONSE",
            "message": "Hệ thống AI từ chối chỉ định đơn thuốc hoặc điều chỉnh liều lượng thuốc. Việc kê đơn chỉ được thực hiện bởi bác sĩ điều trị có chứng chỉ hành nghề."
        }
    }
]

class RuleEngine:
    """Deterministic, auditable clinical rule evaluation engine."""
    
    @staticmethod
    def evaluate_measurement(value: float, measurement_type: str = "fasting") -> Dict[str, Any]:
        """Direct deterministic check for blood glucose value."""
        if value < 70.0:
            return {
                "triggered": True,
                "alert_level": "HYPO",
                "severity": "EMERGENCY",
                "is_abnormal": True,
                "message": "HẠ ĐƯỜNG HUYẾT NGUY HIỂM (< 70 mg/dL). Cần bổ sung 15g đường nhanh ngay lập tức!"
            }
        elif value >= 250.0:
            return {
                "triggered": True,
                "alert_level": "HYPER_EMERGENCY",
                "severity": "EMERGENCY",
                "is_abnormal": True,
                "message": "TĂNG ĐƯỜNG HUYẾT NẶNG (>= 250 mg/dL). Nguy cơ biến chứng cấp tính! Cần đến bệnh viện."
            }
        elif value >= 126.0 and measurement_type == "fasting":
            return {
                "triggered": True,
                "alert_level": "DIABETES",
                "severity": "WARNING",
                "is_abnormal": True,
                "message": "Đường huyết đói cao (>= 126 mg/dL - Ngưỡng Đái tháo đường theo ADA)."
            }
        elif 100.0 <= value < 126.0 and measurement_type == "fasting":
            return {
                "triggered": True,
                "alert_level": "PREDIABETES",
                "severity": "INFO",
                "is_abnormal": True,
                "message": "Đường huyết đói mức Tiền đái tháo đường (100 - 125 mg/dL)."
            }
        elif value > 140.0 and measurement_type == "postprandial":
            return {
                "triggered": True,
                "alert_level": "WARNING",
                "severity": "WARNING",
                "is_abnormal": True,
                "message": "Đường huyết sau ăn cao hơn mục tiêu chuẩn (> 140 mg/dL)."
            }
        return {
            "triggered": False,
            "alert_level": "NORMAL",
            "severity": "NORMAL",
            "is_abnormal": False,
            "message": "Chỉ số đường huyết trong giới hạn bình thường."
        }

    @staticmethod
    def evaluate_safety_response(text: str) -> Tuple[bool, str]:
        """Validate agent draft responses against safety and non-prescription rules."""
        # 1. Prohibit prescription/dosage modifications
        prohibited_patterns = [
            r"tiêm\s+\d+\s*(unit|đơn vị)",
            r"uống\s+\d+\s*mg\s+(insulin|metformin|glucophage)",
            r"tăng\s+liều\s+\d+",
            r"giảm\s+liều\s+\d+",
            r"ngưng\s+uống\s+thuốc"
        ]
        for pattern in prohibited_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "CẢNH BÁO AN TOÀN: Hệ thống phát hiện chỉ định điều chỉnh liều thuốc trái quy định. Nội dung đã bị ngăn chặn để bảo vệ an toàn người bệnh."
        
        return True, text

    @staticmethod
    def evaluate_rules_db(db: Session, context_data: Dict[str, Any], user_id: int = None) -> List[Dict[str, Any]]:
        """Evaluate all active rules stored in database."""
        rules = db.query(RuleModel).filter(RuleModel.is_enabled == True).order_by(RuleModel.priority.asc()).all()
        triggered_actions = []
        
        for rule in rules:
            cond = rule.conditions_json
            field = cond.get("field")
            op = cond.get("operator")
            target_val = cond.get("value")
            
            if field not in context_data:
                continue
                
            actual_val = context_data[field]
            triggered = False
            
            if op == "<" and actual_val < target_val:
                triggered = True
            elif op == "<=" and actual_val <= target_val:
                triggered = True
            elif op == ">" and actual_val > target_val:
                triggered = True
            elif op == ">=" and actual_val >= target_val:
                triggered = True
            elif op == "==" and actual_val == target_val:
                triggered = True
            elif op == "range":
                min_v = cond.get("min", float("-inf"))
                max_v = cond.get("max", float("inf"))
                if min_v <= actual_val <= max_v:
                    triggered = True
                    
            if triggered:
                action = rule.actions_json.copy()
                action["rule_id"] = rule.rule_id
                action["rule_name"] = rule.rule_name
                triggered_actions.append(action)
                
                # Log execution
                log_entry = RuleExecutionLog(
                    rule_id=rule.rule_id,
                    user_id=user_id,
                    triggered=True,
                    input_data_json={field: actual_val},
                    result_json=action
                )
                db.add(log_entry)
                
        db.commit()
        return triggered_actions
