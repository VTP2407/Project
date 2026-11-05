import os
import sys
from fastapi.testclient import TestClient

# Ensure backend root is on path
sys.path.append(os.path.dirname(__file__))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ONLINE"
    print("✓ Health check endpoint passed")

def test_auth_login():
    response = client.post("/api/auth/login", json={
        "email": "patient@diabetes.ai",
        "password": "Patient@123456"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "patient"
    print("✓ Authentication & JWT login passed")
    return data["access_token"]

def test_admin_login():
    response = client.post("/api/auth/login", json={
        "email": "admin@diabetes.ai",
        "password": "Admin@123456"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    print("✓ Admin login passed")
    return token

def test_patient_dashboard(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/patients/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "metrics_summary" in data
    assert "measurements_chart" in data
    print("✓ Patient dashboard & chart data passed")

def test_glucose_measurement_tracking(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    # Add a normal measurement (< 100 fasting)
    res1 = client.post("/api/measurements/glucose", headers=headers, json={
        "value": 85.0,
        "measurement_type": "fasting",
        "notes": "Test normal"
    })
    assert res1.status_code == 200
    assert res1.json()["is_abnormal"] is False
    
    # Add an emergency hypoglycemia measurement (< 70)
    res2 = client.post("/api/measurements/glucose", headers=headers, json={
        "value": 62.0,
        "measurement_type": "fasting",
        "notes": "Test hypo alert"
    })
    assert res2.status_code == 200
    assert res2.json()["is_abnormal"] is True
    assert res2.json()["alert_level"] == "HYPO"
    print("✓ Glucose measurement tracking & clinical alert detection passed")

def test_ml_prediction_assessment(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    # Test high risk diabetic profile
    req_data = {
        "gender": "Female",
        "age": 65.0,
        "hypertension": 1,
        "heart_disease": 1,
        "smoking_history": "former",
        "bmi": 32.5,
        "HbA1c_level": 7.8,
        "blood_glucose_level": 195.0
    }
    response = client.post("/api/ai/predictions", headers=headers, json=req_data)
    assert response.status_code == 200
    res = response.json()
    assert res["prediction"] == 1
    assert res["probability"] > 0.5
    assert "feature_importance" in res
    assert "limitations" in res
    print(f"✓ Trained ML Model inference passed: {res['predicted_class']} (Prob: {res['probability']})")

def test_multi_agent_chat_orchestration(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    query = "Chỉ số đường huyết sáng nay của tôi là 165 mg/dL, tôi nên làm gì và chế độ ăn như thế nào?"
    response = client.post("/api/chat", headers=headers, json={"message": query})
    assert response.status_code == 200
    data = response.json()
    assert len(data["timeline"]) >= 3
    assert len(data["active_agents"]) >= 3
    assert "reply" in data
    assert "Safety Agent" in [t["agent_name"] for t in data["timeline"]]
    print(f"✓ Multi-Agent Orchestrator passed (Active agents: {data['active_agents']}, Duration: {data['total_duration_ms']}ms)")

def test_knowledge_base_search():
    response = client.post("/api/knowledge/search", json={
        "query": "Tiêu chuẩn chẩn đoán đường huyết ADA",
        "top_k": 2
    })
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["similarity_score"] > 0
    print(f"✓ RAG semantic search passed: Top doc '{results[0]['title']}' (Score: {results[0]['similarity_score']})")

def test_rule_engine_listing():
    response = client.get("/api/rules")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) >= 5
    print(f"✓ Rule Engine listing passed: {len(rules)} active rules loaded")

def test_rl_simulation():
    response = client.post("/api/rl/train", json={
        "episodes": 100,
        "alpha": 0.1,
        "gamma": 0.95,
        "epsilon": 0.1
    })
    assert response.status_code == 200
    res = response.json()
    assert "learning_metrics_json" in res
    assert len(res["learning_metrics_json"]["reward_history"]) > 0
    print("✓ Q-Learning simulation demonstration passed")

def run_all_tests():
    print("\n================== RUNNING BACKEND INTEGRATION TESTS ==================")
    test_health_check()
    patient_token = test_auth_login()
    admin_token = test_admin_login()
    test_patient_dashboard(patient_token)
    test_glucose_measurement_tracking(patient_token)
    test_ml_prediction_assessment(patient_token)
    test_multi_agent_chat_orchestration(patient_token)
    test_knowledge_base_search()
    test_rule_engine_listing()
    test_rl_simulation()
    print("================== ALL TESTS PASSED SUCCESSFULLY! ==================\n")

if __name__ == "__main__":
    run_all_tests()
