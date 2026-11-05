from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="patient")  # admin, patient, doctor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("HealthProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    measurements = relationship("GlucoseMeasurement", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("HealthAssessment", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("HealthAlert", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

class HealthProfile(Base):
    __tablename__ = "health_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = Column(String(50), nullable=True)
    gender = Column(String(20), default="Female")  # Female, Male, Other
    height_cm = Column(Float, default=165.0)
    weight_kg = Column(Float, default=65.0)
    bmi = Column(Float, default=23.88)
    hypertension = Column(Integer, default=0)
    heart_disease = Column(Integer, default=0)
    smoking_history = Column(String(50), default="never")
    target_glucose_min = Column(Float, default=70.0)
    target_glucose_max = Column(Float, default=140.0)
    health_goals = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")

class GlucoseMeasurement(Base):
    __tablename__ = "glucose_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    value = Column(Float, nullable=False)  # mg/dL
    measurement_type = Column(String(50), default="fasting")  # fasting, postprandial, bedtime, random
    measured_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(255), nullable=True)
    is_abnormal = Column(Boolean, default=False)
    alert_level = Column(String(50), default="NORMAL")  # NORMAL, PREDIABETES, DIABETES, HYPO, HYPER_EMERGENCY
    
    user = relationship("User", back_populates="measurements")

class HealthAssessment(Base):
    __tablename__ = "health_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    gender = Column(String(20), nullable=False)
    age = Column(Float, nullable=False)
    hypertension = Column(Integer, nullable=False)
    heart_disease = Column(Integer, nullable=False)
    smoking_history = Column(String(50), nullable=False)
    bmi = Column(Float, nullable=False)
    HbA1c_level = Column(Float, nullable=False)
    blood_glucose_level = Column(Float, nullable=False)
    
    prediction = Column(Integer, nullable=False)  # 0 or 1
    predicted_class = Column(String(50), nullable=False)
    probability = Column(Float, nullable=False)
    risk_category = Column(String(50), nullable=False)  # Low, Moderate, High, Severe
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    feature_importance_json = Column(JSON, nullable=True)
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="assessments")

class HealthAlert(Base):
    __tablename__ = "health_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="INFO")  # INFO, WARNING, EMERGENCY
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="alerts")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), default="Cuộc hội thoại sức khỏe")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True, nullable=False)
    sender_role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    agent_metadata_json = Column(JSON, nullable=True)  # captures active agents, citations, latency
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    conversation_id = Column(Integer, nullable=True)
    user_query = Column(Text, nullable=False)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED
    total_duration_ms = Column(Float, default=0.0)
    execution_timeline_json = Column(JSON, nullable=False)  # steps, agents fired, timing
    final_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class RuleModel(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(100), unique=True, index=True, nullable=False)
    rule_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # safety, monitoring, input_validation, response_validation
    description = Column(Text, nullable=False)
    conditions_json = Column(JSON, nullable=False)
    actions_json = Column(JSON, nullable=False)
    priority = Column(Integer, default=10)  # 1 = highest
    is_enabled = Column(Boolean, default=True)
    is_immutable = Column(Boolean, default=False)  # Core clinical safety rules cannot be disabled
    version = Column(String(20), default="1.0.0")

class RuleExecutionLog(Base):
    __tablename__ = "rule_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(100), index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    triggered = Column(Boolean, default=False)
    input_data_json = Column(JSON, nullable=True)
    result_json = Column(JSON, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    source = Column(String(255), nullable=False)  # WHO, ADA, CDC, NIDDK
    content = Column(Text, nullable=False)
    chunk_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_json = Column(JSON, nullable=True)  # vector representation
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("KnowledgeDocument", back_populates="chunks")

class RLExperiment(Base):
    __tablename__ = "rl_experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    algorithm = Column(String(100), default="Q-Learning")
    total_episodes = Column(Integer, default=500)
    epsilon = Column(Float, default=0.1)
    alpha = Column(Float, default=0.1)  # learning rate
    gamma = Column(Float, default=0.95)  # discount factor
    q_table_json = Column(JSON, nullable=True)
    learning_metrics_json = Column(JSON, nullable=True)  # episode reward curve
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=False)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIProviderConfig(Base):
    __tablename__ = "ai_provider_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, nullable=False)  # local_demo, openai, gemini, ollama
    model_name = Column(String(100), nullable=False)
    api_key_masked = Column(String(100), default="")
    is_active = Column(Boolean, default=False)
    status = Column(String(50), default="CONNECTED")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

