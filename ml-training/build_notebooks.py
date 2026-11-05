import os
import nbformat as nbf

NOTEBOOKS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "notebooks"))
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

def build_nb01():
    nb = nbf.v4.new_notebook()
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""# NOTEBOOK 01: DATASET EXPLORATION & CLINICAL ANALYSIS
## Diabetes Multi-Agent AI Support System
**Dataset**: `diabetes_prediction_dataset.csv` (100,000 patient records)
**Target Variable**: `diabetes` (0 = Non-diabetic, 1 = Diabetic)
"""))
    
    cells.append(nbf.v4.new_code_cell("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
DATASET_PATH = os.path.join("..", "datasets", "raw", "diabetes_prediction_dataset.csv")
print(f"Loading dataset from: {DATASET_PATH}")
df = pd.read_csv(DATASET_PATH)
print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.1 Overview & Schema Inspection"""))
    cells.append(nbf.v4.new_code_cell("""print("Column Data Types:\\n", df.dtypes)
print("\\nMissing Values Check:\\n", df.isnull().sum())
duplicates = df.duplicated().sum()
print(f"\\nDuplicated Rows: {duplicates} ({duplicates / len(df) * 100:.2f}%)")
df.head(10)
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.2 Target Class Distribution & Imbalance
In medical diagnosis, class imbalance is a critical challenge. Non-diabetic patients significantly outnumber diabetic cases.
"""))
    cells.append(nbf.v4.new_code_cell("""target_counts = df['diabetes'].value_counts()
target_pct = df['diabetes'].value_counts(normalize=True) * 100
print(f"Non-Diabetic (0): {target_counts[0]} ({target_pct[0]:.2f}%)")
print(f"Diabetic (1): {target_counts[1]} ({target_pct[1]:.2f}%)")
print(f"Imbalance Ratio: ~{target_counts[0]/target_counts[1]:.2f}:1")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.3 Statistical Summary of Features"""))
    cells.append(nbf.v4.new_code_cell("""df.describe()"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.4 Categorical Features Distribution"""))
    cells.append(nbf.v4.new_code_cell("""print("Gender distribution:\\n", df['gender'].value_counts())
print("\\nSmoking history distribution:\\n", df['smoking_history'].value_counts())
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.5 Key Clinical Biomarkers vs Diabetes Status
According to American Diabetes Association (ADA) guidelines:
- **HbA1c**: $<5.7\\%$ (Normal), $5.7\\% - 6.4\\%$ (Prediabetes), $\\ge 6.5\\%$ (Diabetes)
- **Fasting Blood Glucose**: $<100\\, mg/dL$ (Normal), $100-125\\, mg/dL$ (Prediabetes), $\\ge 126\\, mg/dL$ (Diabetes)
"""))
    cells.append(nbf.v4.new_code_cell("""print("Mean biomarker values by diabetes diagnosis:")
print(df.groupby('diabetes')[['HbA1c_level', 'blood_glucose_level', 'bmi', 'age']].mean())
"""))
    
    nb.cells = cells
    filepath = os.path.join(NOTEBOOKS_DIR, "01_data_exploration.ipynb")
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Built {filepath}")

def build_nb02():
    nb = nbf.v4.new_notebook()
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""# NOTEBOOK 02: DATA PREPROCESSING & LEAKAGE PREVENTION
## Pipeline Design
- Stratified splitting into **Train (70%)**, **Validation (10%)**, and **Test (20%)** sets.
- Strict fitting of encoders and scalers **only on the training split**.
- Handling categorical variables (`gender`, `smoking_history`).
- Saving reproducible preprocessed datasets.
"""))
    
    cells.append(nbf.v4.new_code_cell("""import os
import sys
import pandas as pd
import numpy as np

# Import custom data_loader
sys.path.append(os.path.join("..", "training_scripts"))
from data_loader import prepare_splits, load_raw_dataset, FEATURE_COLUMNS, TARGET_COLUMN

print("Executing stratified dataset preparation...")
splits = prepare_splits(test_size=0.2, val_size=0.1, random_state=42)

print(f"Training set:   {splits['X_train'].shape[0]} samples")
print(f"Validation set: {splits['X_val'].shape[0]} samples")
print(f"Test set:       {splits['X_test'].shape[0]} samples")
print(f"Total features: {len(FEATURE_COLUMNS)}")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 2.1 Verifying Class Proportions Across Splits
Stratification ensures that the 8.5% diabetes prevalence is maintained consistently in Train, Val, and Test sets.
"""))
    cells.append(nbf.v4.new_code_cell("""print(f"Train positive rate: {np.mean(splits['y_train']) * 100:.2f}%")
print(f"Val positive rate:   {np.mean(splits['y_val']) * 100:.2f}%")
print(f"Test positive rate:  {np.mean(splits['y_test']) * 100:.2f}%")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 2.2 Pipeline Serialization & Consistency Verification"""))
    cells.append(nbf.v4.new_code_cell("""pipeline = splits['pipeline']
test_sample = {
    'gender': 'Female',
    'age': 55.0,
    'hypertension': 1,
    'heart_disease': 0,
    'smoking_history': 'former',
    'bmi': 29.5,
    'HbA1c_level': 6.8,
    'blood_glucose_level': 160
}
transformed = pipeline.transform_single_dict(test_sample)
print(f"Transformed feature vector shape: {transformed.shape}")
print(f"Values: {transformed.round(4)}")
"""))
    
    nb.cells = cells
    filepath = os.path.join(NOTEBOOKS_DIR, "02_data_preprocessing.ipynb")
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Built {filepath}")

def build_nb03():
    nb = nbf.v4.new_notebook()
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""# NOTEBOOK 03: MACHINE LEARNING MODEL TRAINING & COMPARISON
We train and benchmark 3 classical ML models:
1. **Logistic Regression** (with cost-sensitive class balancing)
2. **Random Forest Classifier** (ensemble of decision trees)
3. **XGBoost Classifier** (extreme gradient boosted trees)
"""))
    
    cells.append(nbf.v4.new_code_cell("""import os
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

sys.path.append(os.path.join("..", "training_scripts"))
from data_loader import prepare_splits, FEATURE_COLUMNS

data = prepare_splits()
X_train, y_train = data['X_train'], data['y_train']
X_val, y_val = data['X_val'], data['y_val']
X_test, y_test = data['X_test'], data['y_test']
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 3.1 Training Candidate Models"""))
    cells.append(nbf.v4.new_code_cell("""models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, eval_metric="logloss")
}

val_results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    y_prob = model.predict_proba(X_val)[:, 1] if hasattr(model, "predict_proba") else y_pred
    
    val_results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_val, y_pred),
        "Precision": precision_score(y_val, y_pred),
        "Recall": recall_score(y_val, y_pred),
        "F1-Score": f1_score(y_val, y_pred),
        "ROC-AUC": roc_auc_score(y_val, y_prob)
    })

pd.DataFrame(val_results)
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 3.2 Evaluation on Unseen Test Set with Best Model"""))
    cells.append(nbf.v4.new_code_cell("""best_model = models["XGBoost"]
y_test_pred = best_model.predict(X_test)
y_test_prob = best_model.predict_proba(X_test)[:, 1]

print("Test Performance (XGBoost):")
print(f"Accuracy:  {accuracy_score(y_test, y_test_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_test_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_test_pred):.4f}")
print(f"F1-Score:  {f1_score(y_test, y_test_pred):.4f}")
print(f"ROC-AUC:   {roc_auc_score(y_test, y_test_prob):.4f}")
"""))
    
    nb.cells = cells
    filepath = os.path.join(NOTEBOOKS_DIR, "03_machine_learning_training.ipynb")
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Built {filepath}")

def build_nb04():
    nb = nbf.v4.new_notebook()
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""# NOTEBOOK 04: PYTORCH DEEP LEARNING (MLP NEURAL NETWORK)
## Architecture
- Input: 8 features
- Layer 1: Linear(8, 64) + BatchNorm1d + ReLU + Dropout(0.2)
- Layer 2: Linear(64, 32) + BatchNorm1d + ReLU + Dropout(0.2)
- Layer 3: Linear(32, 1) Logits
- Loss: `BCEWithLogitsLoss` with `pos_weight = 10.76` (inverse class prevalence)
"""))
    
    cells.append(nbf.v4.new_code_cell("""import os
import sys
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

sys.path.append(os.path.join("..", "training_scripts"))
from data_loader import prepare_splits
from train_dl import DiabetesMLP

data = prepare_splits()
X_train, y_train = data['X_train'], data['y_train']
X_val, y_val = data['X_val'], data['y_val']
X_test, y_test = data['X_test'], data['y_test']

print(f"PyTorch version: {torch.__version__}")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 4.1 PyTorch Model Definition and Initialization"""))
    cells.append(nbf.v4.new_code_cell("""model = DiabetesMLP(input_dim=8)
print(model)
pos_weight = torch.tensor([np.sum(y_train == 0) / (np.sum(y_train == 1) + 1e-5)])
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
print(f"Loss weighted for positive class with factor: {pos_weight.item():.2f}")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 4.2 Training Loop with Validation Monitoring"""))
    cells.append(nbf.v4.new_code_cell("""train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32).unsqueeze(1))
val_ds = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.float32).unsqueeze(1))
train_loader = DataLoader(train_ds, batch_size=256, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=256, shuffle=False)

for epoch in range(1, 6):
    model.train()
    for bx, by in train_loader:
        optimizer.zero_grad()
        loss = criterion(model(bx), by)
        loss.backward()
        optimizer.step()
    
    model.eval()
    val_preds, val_targets = [], []
    with torch.no_grad():
        for bx, by in val_loader:
            probs = torch.sigmoid(model(bx)).numpy().flatten()
            val_preds.extend((probs >= 0.5).astype(int))
            val_targets.extend(by.numpy().flatten())
    print(f"Epoch {epoch:02d} | Val F1: {f1_score(val_targets, val_preds):.4f} | Recall: {recall_score(val_targets, val_preds):.4f}")
"""))
    
    nb.cells = cells
    filepath = os.path.join(NOTEBOOKS_DIR, "04_deep_learning_training.ipynb")
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Built {filepath}")

def build_nb05():
    nb = nbf.v4.new_notebook()
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""# NOTEBOOK 05: MODEL EVALUATION & SHAP EXPLAINABILITY
In this notebook, we perform:
- Benchmark between Best Machine Learning Model (XGBoost) and Deep Learning (PyTorch MLP).
- Confusion Matrices, Classification Reports, ROC-AUC curves.
- **SHAP (SHapley Additive exPlanations)** for global feature importance and individual patient prediction interpretability.
"""))
    
    cells.append(nbf.v4.new_code_cell("""import os
import sys
import json
import joblib
import torch
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

sys.path.append(os.path.join("..", "training_scripts"))
from data_loader import prepare_splits, FEATURE_COLUMNS, SAVED_MODELS_DIR
from train_dl import DiabetesMLP

data = prepare_splits()
X_test, y_test = data['X_test'], data['y_test']

ml_model = joblib.load(os.path.join(SAVED_MODELS_DIR, "diabetes_model.pkl"))
dl_model = DiabetesMLP(input_dim=8)
dl_model.load_state_dict(torch.load(os.path.join(SAVED_MODELS_DIR, "diabetes_dl_model.pth")))
dl_model.eval()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 5.1 Test Set Classification Reports"""))
    cells.append(nbf.v4.new_code_cell("""y_pred_ml = ml_model.predict(X_test)
print("=== XGBoost Classification Report ===")
print(classification_report(y_test, y_pred_ml, target_names=["Non-Diabetic", "Diabetic"]))

with torch.no_grad():
    y_prob_dl = torch.sigmoid(dl_model(torch.tensor(X_test, dtype=torch.float32))).numpy().flatten()
    y_pred_dl = (y_prob_dl >= 0.5).astype(int)
print("=== PyTorch MLP Classification Report ===")
print(classification_report(y_test, y_pred_dl, target_names=["Non-Diabetic", "Diabetic"]))
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 5.2 SHAP Explainability"""))
    cells.append(nbf.v4.new_code_cell("""explainer = shap.TreeExplainer(ml_model)
sample_X = X_test[:300]
shap_values = explainer.shap_values(sample_X)
if isinstance(shap_values, list) and len(shap_values) == 2:
    shap_values = shap_values[1]

mean_shap = np.mean(np.abs(shap_values), axis=0)
shap_df = pd.DataFrame({"Feature": FEATURE_COLUMNS, "Mean_Absolute_SHAP": mean_shap})
shap_df = shap_df.sort_values(by="Mean_Absolute_SHAP", ascending=False).reset_index(drop=True)
shap_df
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 5.3 Clinical Interpretation
The SHAP analysis reveals that **HbA1c_level** and **blood_glucose_level** are by far the dominant drivers of diabetes risk prediction, completely aligned with modern clinical endocrinology standards.
"""))
    
    nb.cells = cells
    filepath = os.path.join(NOTEBOOKS_DIR, "05_model_evaluation.ipynb")
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Built {filepath}")

if __name__ == "__main__":
    build_nb01()
    build_nb02()
    build_nb03()
    build_nb04()
    build_nb05()
    print("All 5 Jupyter notebooks generated successfully.")
