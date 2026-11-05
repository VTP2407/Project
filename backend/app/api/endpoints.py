from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.database.session import get_db
from app.models.entities import (
    User, HealthProfile, GlucoseMeasurement, HealthAssessment, HealthAlert,
    Conversation, Message, AgentExecution, RuleModel, KnowledgeDocument,
    KnowledgeChunk, RLExperiment, ModelVersion, AIProviderConfig
)
from app.schemas.schemas import (
    UserCreate, UserLogin, Token, UserResponse,
    HealthProfileUpdate, HealthProfileResponse,
    MeasurementCreate, MeasurementResponse,
    PredictionRequest, PredictionResponse,
    ChatRequest, ChatResponse, ConversationResponse, MessageResponse,
    RuleCreate, RuleUpdate, RuleResponse,
    DocumentCreate, DocumentResponse, KnowledgeSearchRequest, KnowledgeSearchResult,
    RLTrainRequest, RLExperimentResponse, ModelVersionResponse
)
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user, require_admin
from app.ml.model_service import model_service
from app.rag.engine import RAGEngine
from app.rule_engine.engine import RuleEngine
from app.agents.orchestrator.orchestrator import orchestrator
from app.reinforcement_learning.ql_simulator import run_simulation

router = APIRouter()

# ================= AUTHENTICATION =================
@router.post("/auth/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký trên hệ thống.")
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role or "patient"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Initialize blank health profile
    profile = HealthProfile(user_id=user.id, gender="Female", bmi=24.0)
    db.add(profile)
    db.commit()
    
    return user

@router.post("/auth/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")
        
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }

@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ================= PATIENT PROFILE & DASHBOARD =================
@router.get("/patients/profile", response_model=HealthProfileResponse)
def get_patient_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/patients/profile", response_model=HealthProfileResponse)
def update_patient_profile(profile_in: HealthProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
        
    for k, v in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)
        
    if profile.height_cm and profile.weight_kg and profile.height_cm > 0:
        h_m = profile.height_cm / 100.0
        profile.bmi = round(profile.weight_kg / (h_m * h_m), 2)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/patients/dashboard")
def get_patient_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    measurements = (
        db.query(GlucoseMeasurement)
        .filter(GlucoseMeasurement.user_id == current_user.id)
        .order_by(GlucoseMeasurement.measured_at.asc())
        .limit(20)
        .all()
    )
    assessments = (
        db.query(HealthAssessment)
        .filter(HealthAssessment.user_id == current_user.id)
        .order_by(HealthAssessment.created_at.desc())
        .limit(5)
        .all()
    )
    alerts = (
        db.query(HealthAlert)
        .filter(HealthAlert.user_id == current_user.id, HealthAlert.is_read == False)
        .order_by(HealthAlert.created_at.desc())
        .all()
    )
    
    values = [m.value for m in measurements]
    mean_val = round(sum(values) / len(values), 1) if values else None
    
    return {
        "profile": profile,
        "metrics_summary": {
            "total_measurements": len(measurements),
            "latest_glucose": values[-1] if values else None,
            "average_glucose": mean_val,
            "unread_alerts": len(alerts),
            "latest_risk": assessments[0].risk_category if assessments else "Chưa có đánh giá"
        },
        "measurements_chart": [
            {
                "id": m.id,
                "value": m.value,
                "type": m.measurement_type,
                "date": m.measured_at.strftime("%d/%m %H:%M"),
                "is_abnormal": m.is_abnormal
            }
            for m in measurements
        ],
        "recent_assessments": assessments,
        "active_alerts": alerts
    }

# ================= BLOOD GLUCOSE TRACKING =================
@router.post("/measurements/glucose", response_model=MeasurementResponse)
def add_measurement(m_in: MeasurementCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rule_res = RuleEngine.evaluate_measurement(m_in.value, m_in.measurement_type)
    
    m = GlucoseMeasurement(
        user_id=current_user.id,
        value=m_in.value,
        measurement_type=m_in.measurement_type,
        measured_at=m_in.measured_at or datetime.utcnow(),
        notes=m_in.notes,
        is_abnormal=rule_res["is_abnormal"],
        alert_level=rule_res["alert_level"]
    )
    db.add(m)
    
    # If abnormal, create automated alert
    if rule_res["is_abnormal"]:
        alert = HealthAlert(
            user_id=current_user.id,
            title=f"Cảnh báo chỉ số: {rule_res['alert_level']}",
            message=rule_res["message"],
            severity=rule_res["severity"]
        )
        db.add(alert)
        
    db.commit()
    db.refresh(m)
    return m

@router.get("/measurements/glucose", response_model=List[MeasurementResponse])
def get_measurements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(GlucoseMeasurement)
        .filter(GlucoseMeasurement.user_id == current_user.id)
        .order_by(GlucoseMeasurement.measured_at.desc())
        .limit(100)
        .all()
    )

@router.delete("/measurements/glucose/{m_id}")
def delete_measurement(m_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(GlucoseMeasurement).filter(GlucoseMeasurement.id == m_id, GlucoseMeasurement.user_id == current_user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi đo.")
    db.delete(m)
    db.commit()
    return {"success": True, "message": "Đã xóa bản ghi thành công."}

# ================= AI ASSESSMENTS (ML/DL) =================
@router.post("/ai/predictions", response_model=PredictionResponse)
def predict_diabetes_risk(req: PredictionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Inference using trained model service
    res = model_service.predict(req.model_dump())
    
    # Save assessment history in DB
    assessment = HealthAssessment(
        user_id=current_user.id,
        gender=req.gender,
        age=req.age,
        hypertension=req.hypertension,
        heart_disease=req.heart_disease,
        smoking_history=req.smoking_history,
        bmi=req.bmi,
        HbA1c_level=req.HbA1c_level,
        blood_glucose_level=req.blood_glucose_level,
        prediction=res["prediction"],
        predicted_class=res["predicted_class"],
        probability=res["probability"],
        risk_category=res["risk_category"],
        model_name=res["model_name"],
        model_version=res["model_version"],
        feature_importance_json=res["feature_importance"],
        limitations=res["limitations"]
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    res["assessment_id"] = assessment.id
    return res

@router.get("/ai/predictions/history")
def get_prediction_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(HealthAssessment)
        .filter(HealthAssessment.user_id == current_user.id)
        .order_by(HealthAssessment.created_at.desc())
        .limit(20)
        .all()
    )

# ================= MULTI-AGENT CHAT =================
@router.post("/chat", response_model=ChatResponse)
def chat_with_multi_agent(req: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = None
    if req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == req.conversation_id, Conversation.user_id == current_user.id).first()
    if not conv:
        conv = Conversation(
            user_id=current_user.id,
            title=req.message[:40] + ("..." if len(req.message) > 40 else "")
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
    # Save user message
    user_msg = Message(
        conversation_id=conv.id,
        sender_role="user",
        content=req.message
    )
    db.add(user_msg)
    db.commit()
    
    # Run Orchestrator Agent Pipeline
    orch_res = orchestrator.process_request(db, current_user.id, req.message, conv.id)
    
    # Save Assistant message
    assistant_msg = Message(
        conversation_id=conv.id,
        sender_role="assistant",
        content=orch_res["reply"],
        agent_metadata_json={
            "intent": orch_res["intent_detected"],
            "active_agents": orch_res["active_agents"],
            "timeline": orch_res["timeline"],
            "total_duration_ms": orch_res["total_duration_ms"]
        }
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    
    return {
        "conversation_id": conv.id,
        "message_id": assistant_msg.id,
        "reply": orch_res["reply"],
        "intent_detected": orch_res["intent_detected"],
        "active_agents": orch_res["active_agents"],
        "citations": orch_res["citations"],
        "alerts_triggered": orch_res["alerts_triggered"],
        "timeline": orch_res["timeline"],
        "total_duration_ms": orch_res["total_duration_ms"]
    }

@router.get("/chat/conversations", response_model=List[ConversationResponse])
def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

@router.get("/chat/conversations/{conv_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(conv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện.")
    return db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()

@router.delete("/chat/conversations/{conv_id}")
def delete_conversation(conv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hội thoại.")
    db.delete(conv)
    db.commit()
    return {"success": True}

# ================= AGENTS MONITORING =================
@router.get("/agents")
def get_agents_list():
    return [
        {
            "id": "orchestrator_agent",
            "name": "Orchestrator Agent",
            "role": "Điều phối & Phân luồng",
            "description": "Tiếp nhận câu hỏi, phân loại ý định, tạo kế hoạch và tổng hợp câu trả lời từ các Tác nhân chuyên trách."
        },
        {
            "id": "patient_context_agent",
            "name": "Patient Context Agent",
            "role": "Ngữ cảnh Bệnh nhân",
            "description": "Truy xuất lịch sử chỉ số đường huyết, BMI, thói quen và tiền sử y khoa được ủy quyền."
        },
        {
            "id": "health_assessment_agent",
            "name": "Health Assessment Agent",
            "role": "Đánh giá Nguy cơ Học máy",
            "description": "Gọi trực tiếp mô hình ML (XGBoost/RandomForest) và DL (PyTorch MLP) để dự báo xác suất và trích xuất SHAP."
        },
        {
            "id": "knowledge_agent",
            "name": "Knowledge Agent",
            "role": "Truy xuất Tri thức (RAG)",
            "description": "Tìm kiếm tài liệu y khoa chính thống từ cơ sở tri thức (WHO, ADA, CDC) và cung cấp trích dẫn nguồn."
        },
        {
            "id": "lifestyle_advisor_agent",
            "name": "Lifestyle Advisor Agent",
            "role": "Tư vấn Giáo dục Lối sống",
            "description": "Cung cấp kiến thức dinh dưỡng cân bằng và chế độ luyện tập thể chất phù hợp (tuyệt đối không kê đơn thuốc)."
        },
        {
            "id": "monitoring_agent",
            "name": "Monitoring Agent",
            "role": "Giám sát & Cảnh báo",
            "description": "Theo dõi các giá trị đo vượt ngưỡng và phân tích biến động đường huyết bất thường."
        },
        {
            "id": "safety_agent",
            "name": "Safety Agent",
            "role": "Thẩm định An toàn Y tế",
            "description": "Ngăn chặn các khuyến nghị độc hại, phát hiện cấp cứu y khoa và bắt buộc đính kèm tuyên bố miễn trừ trách nhiệm."
        },
        {
            "id": "report_agent",
            "name": "Report Agent",
            "role": "Tổng hợp Báo cáo",
            "description": "Thống kê dữ liệu chuỗi thời gian, tính toán giá trị trung bình và lập bảng tóm tắt sức khỏe."
        }
    ]

@router.get("/agents/executions")
def get_agent_executions(db: Session = Depends(get_db)):
    executions = db.query(AgentExecution).order_by(AgentExecution.created_at.desc()).limit(30).all()
    return [
        {
            "id": e.id,
            "query": e.user_query,
            "status": e.status,
            "total_duration_ms": e.total_duration_ms,
            "timeline": e.execution_timeline_json,
            "final_response": e.final_response,
            "created_at": e.created_at
        }
        for e in executions
    ]

# ================= KNOWLEDGE BASE & RAG =================
@router.post("/knowledge/documents", response_model=DocumentResponse)
def add_knowledge_doc(doc_in: DocumentCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    doc_id = f"DOC_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    chunks = RAGEngine.chunk_text(doc_in.content)
    
    doc = KnowledgeDocument(
        doc_id=doc_id,
        title=doc_in.title,
        category=doc_in.category,
        source=doc_in.source,
        content=doc_in.content,
        chunk_count=len(chunks)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    for i, c_text in enumerate(chunks):
        c_vec = RAGEngine.compute_embedding(c_text)
        chunk_obj = KnowledgeChunk(
            document_id=doc.id,
            chunk_index=i,
            content=c_text,
            embedding_json=c_vec
        )
        db.add(chunk_obj)
    db.commit()
    return doc

@router.get("/knowledge/documents", response_model=List[DocumentResponse])
def get_knowledge_docs(db: Session = Depends(get_db)):
    return db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()

@router.delete("/knowledge/documents/{d_id}")
def delete_knowledge_doc(d_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == d_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    db.delete(doc)
    db.commit()
    return {"success": True}

@router.post("/knowledge/search", response_model=List[KnowledgeSearchResult])
def search_knowledge_base(search_in: KnowledgeSearchRequest, db: Session = Depends(get_db)):
    results = RAGEngine.search_knowledge(db, search_in.query, search_in.category, search_in.top_k)
    return [
        {
            "title": r["title"],
            "category": r["category"],
            "source": r["source"],
            "content": r["content"],
            "similarity_score": r["similarity_score"]
        }
        for r in results
    ]

# ================= RULE ENGINE =================
@router.get("/rules", response_model=List[RuleResponse])
def get_rules(db: Session = Depends(get_db)):
    return db.query(RuleModel).order_by(RuleModel.priority.asc()).all()

@router.post("/rules", response_model=RuleResponse)
def create_rule(rule_in: RuleCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    rule = RuleModel(
        rule_id=rule_in.rule_id,
        rule_name=rule_in.rule_name,
        category=rule_in.category,
        description=rule_in.description,
        conditions_json=rule_in.conditions_json,
        actions_json=rule_in.actions_json,
        priority=rule_in.priority,
        is_enabled=rule_in.is_enabled,
        is_immutable=False
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/rules/{r_id}/toggle")
def toggle_rule(r_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    rule = db.query(RuleModel).filter(RuleModel.id == r_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Không tìm thấy quy tắc.")
    if rule.is_immutable:
        raise HTTPException(status_code=400, detail="Quy tắc an toàn lâm sàng cốt lõi không thể tắt.")
    rule.is_enabled = not rule.is_enabled
    db.commit()
    return {"id": rule.id, "is_enabled": rule.is_enabled}

# ================= REINFORCEMENT LEARNING =================
@router.post("/rl/train", response_model=RLExperimentResponse)
def train_rl_simulation(req: RLTrainRequest, db: Session = Depends(get_db)):
    sim_res = run_simulation(
        episodes=req.episodes,
        alpha=req.alpha,
        gamma=req.gamma,
        epsilon=req.epsilon
    )
    
    exp = RLExperiment(
        name=f"Q-Learning Education Policy (Ep: {req.episodes})",
        algorithm="Q-Learning",
        total_episodes=req.episodes,
        epsilon=req.epsilon,
        alpha=req.alpha,
        gamma=req.gamma,
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
    db.refresh(exp)
    
    return {
        "id": exp.id,
        "name": exp.name,
        "algorithm": exp.algorithm,
        "total_episodes": exp.total_episodes,
        "epsilon": exp.epsilon,
        "alpha": exp.alpha,
        "gamma": exp.gamma,
        "learning_metrics_json": exp.learning_metrics_json,
        "q_table_summary": exp.q_table_json,
        "status": exp.status,
        "created_at": exp.created_at
    }

@router.get("/rl/experiments", response_model=List[RLExperimentResponse])
def get_rl_experiments(db: Session = Depends(get_db)):
    records = db.query(RLExperiment).order_by(RLExperiment.created_at.desc()).limit(10).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "algorithm": r.algorithm,
            "total_episodes": r.total_episodes,
            "epsilon": r.epsilon,
            "alpha": r.alpha,
            "gamma": r.gamma,
            "learning_metrics_json": r.learning_metrics_json or {},
            "q_table_summary": r.q_table_json or {},
            "status": r.status,
            "created_at": r.created_at
        }
        for r in records
    ]

# ================= ADMIN DASHBOARD & MODELS =================
@router.get("/admin/models", response_model=List[ModelVersionResponse])
def get_registered_models(db: Session = Depends(get_db)):
    return db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()

@router.get("/admin/stats")
def get_admin_system_stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {
        "total_users": db.query(User).count(),
        "total_measurements": db.query(GlucoseMeasurement).count(),
        "total_assessments": db.query(HealthAssessment).count(),
        "total_rules": db.query(RuleModel).count(),
        "total_kb_documents": db.query(KnowledgeDocument).count(),
        "total_agent_executions": db.query(AgentExecution).count(),
        "active_model": model_service.metadata.get("model_name", "XGBoost") if model_service.metadata else "XGBoost",
        "dataset_name": "diabetes_prediction_dataset.csv (100,000 records)"
    }

