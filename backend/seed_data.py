import os
import json
from datetime import datetime, timedelta
from app.database.session import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.entities import (
    User, HealthProfile, GlucoseMeasurement, HealthAssessment, HealthAlert,
    RuleModel, KnowledgeDocument, KnowledgeChunk, ModelVersion, RLExperiment
)
from app.rule_engine.engine import DEFAULT_CLINICAL_RULES
from app.rag.engine import RAGEngine
from app.reinforcement_learning.ql_simulator import run_simulation

INITIAL_KB_DOCS = [
    {
        "doc_id": "KB_ADA_001",
        "title": "Tiêu Chuẩn Chẩn Đoán & Phân Loại Đái Tháo Đường ADA",
        "category": "Diagnostic Tests",
        "source": "Hiệp hội Đái tháo đường Hoa Kỳ (ADA)",
        "content": "Tiêu chuẩn chẩn đoán đái tháo đường của Hiệp hội Đái tháo đường Hoa Kỳ (ADA) bao gồm: 1) Glucose huyết tương lúc đói (FPG) >= 126 mg/dL (7.0 mmol/L) sau ít nhất 8 giờ nhịn đói; 2) Chỉ số HbA1c >= 6.5% (48 mmol/mol) thực hiện bằng phương pháp chuẩn hóa NGSP; 3) Glucose huyết tương 2 giờ sau nghiệm pháp dung nạp 75g glucose đường uống (OGTT) >= 200 mg/dL (11.1 mmol/L); hoặc 4) Bệnh nhân có triệu chứng kinh điển của tăng đường huyết kèm glucose huyết tương ngẫu nhiên >= 200 mg/dL. Tiền đái tháo đường được định nghĩa khi FPG từ 100 đến 125 mg/dL (rối loạn đường huyết đói) hoặc HbA1c từ 5.7% đến 6.4%."
    },
    {
        "doc_id": "KB_WHO_002",
        "title": "Khuyến Nghị Dinh Dưỡng & Hoạt Động Thể Lực Phòng Ngừa Bệnh Đái Tháo Đường",
        "category": "Nutrition",
        "source": "Tổ chức Y tế Thế giới (WHO)",
        "content": "Tổ chức Y tế Thế giới (WHO) khuyến cáo lối sống lành mạnh là biện pháp can thiệp cốt lõi để phòng ngừa và kiểm soát đái tháo đường type 2. Khuyến nghị bao gồm: 1) Đạt và duy trì chỉ số khối cơ thể (BMI) khỏe mạnh từ 18.5 đến 22.9 kg/m2 đối với người châu Á; 2) Duy trì hoạt động thể lực đều đặn ít nhất 150 phút mỗi tuần với cường độ trung bình (đi bộ nhanh, chạy bộ, bơi lội); 3) Giảm thiểu lượng chất béo bão hòa dưới 10% tổng năng lượng khẩu phần; 4) Tăng cường hấp thụ chất xơ tối thiểu 20-35g mỗi ngày thông qua ngũ cốc nguyên hạt, các loại đậu và rau xanh tươi; 5) Giới hạn lượng đường tự do dưới 5% tổng năng lượng nạp vào."
    },
    {
        "doc_id": "KB_CDC_003",
        "title": "Hướng Dẫn Nhận Diện & Xử Trí Khẩn Cấp Hạ Đường Huyết (Hypoglycemia)",
        "category": "Symptoms",
        "source": "Trung tâm Kiểm soát và Phòng ngừa Dịch bệnh Hoa Kỳ (CDC)",
        "content": "Hạ đường huyết xảy ra khi nồng độ glucose trong máu giảm xuống dưới 70 mg/dL (3.9 mmol/L). Triệu chứng lâm sàng điển hình gồm: run rẩy, vã mồ hôi lạnh, tim đập nhanh, chóng mặt, đói cồn cào, nhìn mờ, lú lẫn và cáu gắt. Xử trí theo 'Quy tắc 15-15': Nạp ngay 15 gam carbohydrate tác dụng nhanh (1/2 cốc nước ép trái cây, 1/2 lon nước ngọt thông thường hoặc 3-4 viên đường glucose). Nghỉ ngơi và kiểm tra lại đường huyết sau 15 phút. Nếu vẫn dưới 70 mg/dL, lặp lại thêm 15 gam đường. Khi bệnh nhân mất tri giác, co giật hoặc không thể nuốt, KHÔNG cho ăn uống qua đường miệng, tiêm glucagon nếu có và gọi cấp cứu 115 ngay lập tức."
    },
    {
        "doc_id": "KB_NIDDK_004",
        "title": "Mối Liên Hệ Giữa Chỉ Số Khối Cơ Thể BMI, Tăng Huyết Áp và Kháng Insulin",
        "category": "Risk Factors",
        "source": "Viện Quốc gia về Bệnh Tiểu đường, Tiêu hóa và Bệnh Thận (NIDDK)",
        "content": "Thừa cân béo phì (đặc biệt là tích tụ mỡ nội tạng) giải phóng các acid béo tự do và cytokine gây viêm (TNF-alpha, IL-6), làm suy giảm tín hiệu thụ thể insulin tại cơ vân và mô gan, dẫn đến tình trạng kháng insulin. Tăng huyết áp đi kèm làm gia tăng áp lực mạch máu, tổn thương nội mô và thúc đẩy biến chứng vi mạch ở cầu thận và võng mạc. Việc kiểm soát đồng thời chỉ số huyết áp dưới 130/80 mmHg và đưa BMI về ngưỡng tối ưu giúp giảm hơn 40% nguy cơ biến chứng tim mạch ở người có nguy cơ đái tháo đường."
    }
]

def seed_database():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Admin Account
        admin = db.query(User).filter(User.email == "admin@diabetes.ai").first()
        if not admin:
            admin = User(
                email="admin@diabetes.ai",
                hashed_password=get_password_hash("Admin@123456"),
                full_name="Quản Trị Viên Hệ Thống (Dr. Admin)",
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Created Admin: admin@diabetes.ai / Admin@123456")

        # 2. Patient Demo Account
        patient = db.query(User).filter(User.email == "patient@diabetes.ai").first()
        if not patient:
            patient = User(
                email="patient@diabetes.ai",
                hashed_password=get_password_hash("Patient@123456"),
                full_name="Nguyễn Văn An (Demo Patient)",
                role="patient"
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            print("Created Demo Patient: patient@diabetes.ai / Patient@123456")

            # Patient profile
            profile = HealthProfile(
                user_id=patient.id,
                date_of_birth="1980-05-15",
                gender="Male",
                height_cm=170.0,
                weight_kg=75.0,
                bmi=25.95,
                hypertension=1,
                heart_disease=0,
                smoking_history="former",
                target_glucose_min=70.0,
                target_glucose_max=130.0,
                health_goals="Giữ đường huyết đói dưới 110 mg/dL, giảm 3kg trong 2 tháng."
            )
            db.add(profile)
            
            # Synthetic demonstration glucose measurements
            base_time = datetime.utcnow() - timedelta(days=7)
            measurements_data = [
                (108.0, "fasting", "Sáng thứ Hai"),
                (142.0, "postprandial", "Sau bữa trưa"),
                (115.0, "fasting", "Sáng thứ Ba"),
                (135.0, "postprandial", "Sau bữa tối"),
                (128.0, "fasting", "Sáng thứ Tư"),
                (160.0, "postprandial", "Sau tiệc cưới"),
                (95.0, "fasting", "Sáng thứ Năm"),
                (120.0, "postprandial", "Sau bữa trưa nhẹ"),
                (110.0, "fasting", "Sáng thứ Sáu"),
                (130.0, "fasting", "Sáng thứ Bảy")
            ]
            for i, (val, m_type, note) in enumerate(measurements_data):
                m_time = base_time + timedelta(days=i * 0.7)
                m = GlucoseMeasurement(
                    user_id=patient.id,
                    value=val,
                    measurement_type=m_type,
                    measured_at=m_time,
                    notes=note,
                    is_abnormal=(val >= 126.0 if m_type == "fasting" else val >= 140.0),
                    alert_level="PREDIABETES" if 100 <= val < 126 else ("DIABETES" if val >= 126 else "NORMAL")
                )
                db.add(m)

            # Sample assessment
            assessment = HealthAssessment(
                user_id=patient.id,
                gender="Male",
                age=44.0,
                hypertension=1,
                heart_disease=0,
                smoking_history="former",
                bmi=25.95,
                HbA1c_level=6.1,
                blood_glucose_level=125.0,
                prediction=0,
                predicted_class="ÂM TÍNH (Nguy cơ Tiền đái tháo đường)",
                probability=0.38,
                risk_category="Trung bình (Tiền đái tháo đường / Cần theo dõi)",
                model_name="XGBoost",
                model_version="1.0.0",
                feature_importance_json={"HbA1c_level": 2.50, "blood_glucose_level": 2.04, "age": 0.55, "bmi": 0.25},
                limitations="Mô hình sàng lọc hỗ trợ, không thay thế chẩn đoán lâm sàng."
            )
            db.add(assessment)
            db.commit()

        # 3. Seed Clinical Rules
        for r_data in DEFAULT_CLINICAL_RULES:
            existing = db.query(RuleModel).filter(RuleModel.rule_id == r_data["rule_id"]).first()
            if not existing:
                rule = RuleModel(
                    rule_id=r_data["rule_id"],
                    rule_name=r_data["rule_name"],
                    category=r_data["category"],
                    description=r_data["description"],
                    conditions_json=r_data["conditions_json"],
                    actions_json=r_data["actions_json"],
                    priority=r_data["priority"],
                    is_enabled=True,
                    is_immutable=r_data.get("is_immutable", False),
                    version="1.0.0"
                )
                db.add(rule)
        db.commit()
        print(f"Verified {len(DEFAULT_CLINICAL_RULES)} clinical rules.")

        # 4. Seed Knowledge Documents & Chunks
        for doc_info in INITIAL_KB_DOCS:
            existing_doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.doc_id == doc_info["doc_id"]).first()
            if not existing_doc:
                chunks = RAGEngine.chunk_text(doc_info["content"])
                doc = KnowledgeDocument(
                    doc_id=doc_info["doc_id"],
                    title=doc_info["title"],
                    category=doc_info["category"],
                    source=doc_info["source"],
                    content=doc_info["content"],
                    chunk_count=len(chunks)
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
                for idx, c_text in enumerate(chunks):
                    vec = RAGEngine.compute_embedding(c_text)
                    chunk_obj = KnowledgeChunk(
                        document_id=doc.id,
                        chunk_index=idx,
                        content=c_text,
                        embedding_json=vec
                    )
                    db.add(chunk_obj)
                db.commit()
        print(f"Verified {len(INITIAL_KB_DOCS)} Knowledge Base medical reference documents.")

        # 5. Seed Model Versions
        models_to_register = [
            {
                "model_name": "XGBoost Classifier",
                "model_type": "Gradient Boosted Trees",
                "version": "1.0.0",
                "is_active": True,
                "accuracy": 0.9725,
                "precision": 0.9848,
                "recall": 0.6871,
                "f1_score": 0.8094,
                "roc_auc": 0.9797
            },
            {
                "model_name": "PyTorch MLP",
                "model_type": "Deep Neural Network",
                "version": "1.0.0",
                "is_active": False,
                "accuracy": 0.8966,
                "precision": 0.4475,
                "recall": 0.9229,
                "f1_score": 0.6028,
                "roc_auc": 0.9766
            }
        ]
        for m_data in models_to_register:
            existing_m = db.query(ModelVersion).filter(ModelVersion.model_name == m_data["model_name"]).first()
            if not existing_m:
                mv = ModelVersion(
                    model_name=m_data["model_name"],
                    model_type=m_data["model_type"],
                    version=m_data["version"],
                    is_active=m_data["is_active"],
                    accuracy=m_data["accuracy"],
                    precision=m_data["precision"],
                    recall=m_data["recall"],
                    f1_score=m_data["f1_score"],
                    roc_auc=m_data["roc_auc"]
                )
                db.add(mv)
        db.commit()

        # 6. Seed RL Simulation Experiment
        existing_rl = db.query(RLExperiment).first()
        if not existing_rl:
            print("Seeding baseline Q-Learning education policy (100 episodes)...")
            sim_res = run_simulation(episodes=100)
            exp = RLExperiment(
                name="Baseline Q-Learning Health Education Policy",
                algorithm="Q-Learning",
                total_episodes=100,
                epsilon=0.1,
                alpha=0.1,
                gamma=0.95,
                learning_metrics_json={
                    "reward_history": sim_res["reward_history"],
                    "moving_average": sim_res["moving_average"],
                    "final_average_reward": sim_res["final_average_reward"]
                },
                q_table_json={"policy_summary": sim_res["policy_summary"]},
                status="COMPLETED"
            )
            db.add(exp)
            db.commit()
            print("Seeded RL Experiment successfully.")

        print("Database seeding completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

