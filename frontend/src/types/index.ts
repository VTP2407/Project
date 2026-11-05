export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'patient' | 'doctor';
}

export interface HealthProfile {
  id?: number;
  date_of_birth?: string;
  gender: string;
  height_cm: number;
  weight_kg: number;
  bmi: number;
  hypertension: number;
  heart_disease: number;
  smoking_history: string;
  target_glucose_min: number;
  target_glucose_max: number;
  health_goals?: string;
}

export interface PredictionRequest {
  gender: string;
  age: number;
  hypertension: number;
  heart_disease: number;
  smoking_history: string;
  bmi: number;
  HbA1c_level: number;
  blood_glucose_level: number;
}

export interface GlucoseMeasurement {
  id: number;
  value: number;
  measurement_type: string;
  measured_at: string;
  notes?: string;
  is_abnormal: boolean;
  alert_level: string;
}

export interface HealthAssessment {
  id: number;
  prediction: number;
  predicted_class: string;
  probability: number;
  confidence_pct: number;
  risk_category: string;
  model_name: string;
  model_version: string;
  feature_importance: Record<string, number>;
  clinical_explanation: string;
  limitations: string;
  created_at?: string;
}

export interface AgentTimelineStep {
  agent_id: string;
  agent_name: string;
  status: string;
  duration_ms: number;
  action_summary: string;
  output_preview?: string;
}

export interface ChatResponse {
  conversation_id: number;
  message_id: number;
  reply: string;
  intent_detected: string;
  active_agents: string[];
  citations: Array<{ title: string; source: string; category: string; score: number }>;
  alerts_triggered: string[];
  timeline: AgentTimelineStep[];
  total_duration_ms: number;
}

export interface Rule {
  id: number;
  rule_id: string;
  rule_name: string;
  category: string;
  description: string;
  priority: number;
  is_enabled: boolean;
  is_immutable: boolean;
}

export interface KnowledgeDocument {
  id: number;
  doc_id: string;
  title: string;
  category: string;
  source: string;
  content: string;
  chunk_count: number;
}

export interface RLExperiment {
  id: number;
  name: string;
  algorithm: string;
  total_episodes: number;
  learning_metrics_json: {
    reward_history: number[];
    moving_average: number[];
    final_average_reward: number;
  };
  q_table_summary: {
    policy_summary: Array<{
      glucose_state: string;
      recommended_action: string;
      q_values: number[];
    }>;
  };
}
