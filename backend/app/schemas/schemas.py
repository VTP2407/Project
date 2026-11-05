from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# ----------------- AUTH & USER -----------------
class UserBase(BaseModel):
    email: str
    full_name: str
    role: Optional[str] = "patient"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    full_name: str
    role: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- HEALTH PROFILE -----------------
class HealthProfileBase(BaseModel):
    date_of_birth: Optional[str] = None
    gender: str = "Female"
    height_cm: float = 165.0
    weight_kg: float = 65.0
    bmi: float = 23.88
    hypertension: int = 0
    heart_disease: int = 0
    smoking_history: str = "never"
    target_glucose_min: float = 70.0
    target_glucose_max: float = 140.0
    health_goals: Optional[str] = None

class HealthProfileUpdate(BaseModel):
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    hypertension: Optional[int] = None
    heart_disease: Optional[int] = None
    smoking_history: Optional[str] = None
    target_glucose_min: Optional[float] = None
    target_glucose_max: Optional[float] = None
    health_goals: Optional[str] = None

class HealthProfileResponse(HealthProfileBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# ----------------- GLUCOSE TRACKING -----------------
class MeasurementCreate(BaseModel):
    value: float = Field(..., ge=20.0, le=600.0, description="Blood glucose value in mg/dL")
    measurement_type: str = Field("fasting", description="fasting, postprandial, bedtime, random")
    measured_at: Optional[datetime] = None
    notes: Optional[str] = None

class MeasurementResponse(BaseModel):
    id: int
    user_id: int
    value: float
    measurement_type: str
    measured_at: datetime
    notes: Optional[str]
    is_abnormal: bool
    alert_level: str

    class Config:
        from_attributes = True

# ----------------- AI PREDICTIONS -----------------
class PredictionRequest(BaseModel):
    gender: str = Field(..., description="Female, Male, Other")
    age: float = Field(..., ge=0.0, le=120.0)
    hypertension: int = Field(0, ge=0, le=1)
    heart_disease: int = Field(0, ge=0, le=1)
    smoking_history: str = Field("never", description="never, No Info, current, former, ever, not current")
    bmi: float = Field(..., ge=10.0, le=95.0)
    HbA1c_level: float = Field(..., ge=3.5, le=15.0)
    blood_glucose_level: float = Field(..., ge=40.0, le=400.0)

class PredictionResponse(BaseModel):
    prediction: int  # 0 or 1
    predicted_class: str
    probability: float
    confidence_pct: float
    risk_category: str  # Low, Moderate, High, Severe
    model_name: str
    model_version: str
    feature_importance: Dict[str, float]
    clinical_explanation: str
    limitations: str
    assessment_id: Optional[int] = None

# ----------------- CHAT & MULTI-AGENT -----------------
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class AgentTimelineStep(BaseModel):
    agent_id: str
    agent_name: str
    status: str
    duration_ms: float
    action_summary: str
    output_preview: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    reply: str
    intent_detected: str
    active_agents: List[str]
    citations: List[Dict[str, Any]]
    alerts_triggered: List[str]
    timeline: List[AgentTimelineStep]
    total_duration_ms: float

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_role: str
    content: str
    agent_metadata_json: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- RULE ENGINE -----------------
class RuleCreate(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    description: str
    conditions_json: Dict[str, Any]
    actions_json: Dict[str, Any]
    priority: int = 10
    is_enabled: bool = True

class RuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    conditions_json: Optional[Dict[str, Any]] = None
    actions_json: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_enabled: Optional[bool] = None

class RuleResponse(BaseModel):
    id: int
    rule_id: str
    rule_name: str
    category: str
    description: str
    conditions_json: Dict[str, Any]
    actions_json: Dict[str, Any]
    priority: int
    is_enabled: bool
    is_immutable: bool
    version: str

    class Config:
        from_attributes = True

# ----------------- KNOWLEDGE BASE -----------------
class DocumentCreate(BaseModel):
    title: str
    category: str
    source: str
    content: str

class DocumentResponse(BaseModel):
    id: int
    doc_id: str
    title: str
    category: str
    source: str
    content: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class KnowledgeSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: int = 3

class KnowledgeSearchResult(BaseModel):
    title: str
    category: str
    source: str
    content: str
    similarity_score: float

# ----------------- REINFORCEMENT LEARNING -----------------
class RLTrainRequest(BaseModel):
    episodes: int = Field(500, ge=50, le=5000)
    alpha: float = Field(0.1, ge=0.01, le=1.0)
    gamma: float = Field(0.95, ge=0.5, le=0.99)
    epsilon: float = Field(0.1, ge=0.01, le=0.5)

class RLExperimentResponse(BaseModel):
    id: int
    name: str
    algorithm: str
    total_episodes: int
    epsilon: float
    alpha: float
    gamma: float
    learning_metrics_json: Dict[str, Any]
    q_table_summary: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- MODEL MANAGEMENT -----------------
class ModelVersionResponse(BaseModel):
    id: int
    model_name: str
    model_type: str
    version: str
    is_active: bool
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    created_at: datetime

    class Config:
        from_attributes = True
