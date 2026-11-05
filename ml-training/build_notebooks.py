import os
import nbformat as nbf

NOTEBOOKS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "notebooks"))
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

def build_nb01():
    nb = nbf.v4.new_notebook()
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""# NOTEBOOK 01: DATASET EXPLORATION & CLINICAL VISUALIZATION
## Diabetes Multi-Agent AI Support System
**Dataset**: `diabetes_prediction_dataset.csv` (100,000 patient records)
**Target Variable**: `diabetes` (0 = Non-diabetic, 1 = Diabetic)
"""))
    
    cells.append(nbf.v4.new_code_cell("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
sns.set_palette("tab10")
plt.rcParams['font.size'] = 11

DATASET_PATH = os.path.join("..", "datasets", "raw", "diabetes_prediction_dataset.csv")
print(f"Loading dataset from: {DATASET_PATH}")
df = pd.read_csv(DATASET_PATH)
print(f"Shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
df.head(5)
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.1 Target Class Imbalance Analysis (Donut Chart & Bar Chart)"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Donut Chart
counts = df['diabetes'].value_counts()
labels = [f"Non-Diabetic (0): {counts[0]:,} ({counts[0]/len(df)*100:.1f}%)",
          f"Diabetic (1): {counts[1]:,} ({counts[1]/len(df)*100:.1f}%)"]
colors = ['#38bdf8', '#f87171']
axes[0].pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, 
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
axes[0].set_title("Target Class Distribution (Imbalance Ratio: ~10.76 : 1)", fontsize=13, fontweight='bold')

# Bar Chart
sns.barplot(x=['Non-Diabetic (0)', 'Diabetic (1)'], y=counts.values, palette=colors, ax=axes[1], hue=['Non-Diabetic (0)', 'Diabetic (1)'], legend=False)
for i, v in enumerate(counts.values):
    axes[1].text(i, v + 1500, f"{v:,} ({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')
axes[1].set_ylabel("Patient Count")
axes[1].set_title("Absolute Record Counts", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.2 Continuous Biomarker Distributions (Histograms & KDE)"""))
    cells.append(nbf.v4.new_code_cell("""num_cols = ['age', 'bmi', 'HbA1c_level', 'blood_glucose_level']
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for idx, col in enumerate(num_cols):
    ax = axes[idx // 2, idx % 2]
    sns.histplot(data=df, x=col, kde=True, hue='diabetes', bins=30, ax=ax, 
                 palette={0: '#0284c7', 1: '#dc2626'}, alpha=0.5)
    ax.set_title(f"Distribution of {col} by Diabetes Diagnosis", fontsize=12, fontweight='bold')
    ax.set_xlabel(col)
    ax.set_ylabel("Count")

plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.3 ADA Clinical Diagnostic Thresholds (Violin & Boxplots)
American Diabetes Association (ADA) criteria:
- **HbA1c**: $<5.7\\%$ (Normal), $5.7\\% - 6.4\\%$ (Prediabetes), $\\ge 6.5\\%$ (Diabetes)
- **Fasting Glucose**: $<100\\, mg/dL$ (Normal), $100-125\\, mg/dL$ (Prediabetes), $\\ge 126\\, mg/dL$ (Diabetes)
"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# HbA1c with ADA threshold
sns.violinplot(data=df, x='diabetes', y='HbA1c_level', palette=['#93c5fd', '#fca5a5'], ax=axes[0], inner='box')
axes[0].axhline(y=6.5, color='red', linestyle='--', linewidth=2, label='ADA Diabetes Cutoff (>= 6.5%)')
axes[0].axhline(y=5.7, color='orange', linestyle=':', linewidth=2, label='ADA Prediabetes Cutoff (5.7%)')
axes[0].set_xticklabels(['Non-Diabetic (0)', 'Diabetic (1)'])
axes[0].set_title("HbA1c Level vs Clinical Diagnostic Cutoffs", fontsize=13, fontweight='bold')
axes[0].legend(loc='upper left')

# Glucose with ADA threshold
sns.violinplot(data=df, x='diabetes', y='blood_glucose_level', palette=['#93c5fd', '#fca5a5'], ax=axes[1], inner='box')
axes[1].axhline(y=126, color='red', linestyle='--', linewidth=2, label='ADA Fasting Diabetes (>= 126 mg/dL)')
axes[1].axhline(y=100, color='orange', linestyle=':', linewidth=2, label='ADA Impaired Fasting (>= 100 mg/dL)')
axes[1].set_xticklabels(['Non-Diabetic (0)', 'Diabetic (1)'])
axes[1].set_title("Blood Glucose Level vs Clinical Cutoffs", fontsize=13, fontweight='bold')
axes[1].legend(loc='upper left')

plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.4 Categorical Risk Factor Analysis & Prevalence Rates"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Gender vs Diabetes Rate
gender_rates = df.groupby('gender')['diabetes'].mean() * 100
sns.barplot(x=gender_rates.index, y=gender_rates.values, palette='Blues_d', ax=axes[0])
for i, v in enumerate(gender_rates.values):
    axes[0].text(i, v + 0.3, f"{v:.2f}%", ha='center', fontweight='bold')
axes[0].set_title("Diabetes Rate (%) by Gender", fontsize=12, fontweight='bold')
axes[0].set_ylabel("Prevalence (%)")

# Smoking History vs Diabetes Rate
smoke_rates = df.groupby('smoking_history')['diabetes'].mean().sort_values(ascending=False) * 100
sns.barplot(x=smoke_rates.index, y=smoke_rates.values, palette='Reds_d', ax=axes[1])
for i, v in enumerate(smoke_rates.values):
    axes[1].text(i, v + 0.3, f"{v:.1f}%", ha='center', fontweight='bold')
axes[1].set_title("Diabetes Rate (%) by Smoking History", fontsize=12, fontweight='bold')
axes[1].set_xticklabels(smoke_rates.index, rotation=30)
axes[1].set_ylabel("Prevalence (%)")

# Comorbidity: Hypertension & Heart Disease
comorbid = df.groupby(['hypertension', 'heart_disease'])['diabetes'].mean().unstack() * 100
sns.heatmap(comorbid, annot=True, fmt=".1f", cmap="YlOrRd", ax=axes[2], cbar_kws={'label': 'Diabetes Rate (%)'})
axes[2].set_title("Diabetes Rate by Comorbidities (%)", fontsize=12, fontweight='bold')
axes[2].set_xlabel("Heart Disease (0/1)")
axes[2].set_ylabel("Hypertension (0/1)")

plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.5 Bivariate Scatter Quadrant (HbA1c vs Blood Glucose)"""))
    cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(10, 7))
sample_df = df.sample(n=3000, random_state=42)
sns.scatterplot(data=sample_df, x='HbA1c_level', y='blood_glucose_level', hue='diabetes', 
                palette={0: '#38bdf8', 1: '#dc2626'}, alpha=0.6, s=35)
plt.axvline(x=6.5, color='darkred', linestyle='--', linewidth=1.5, label='ADA HbA1c Cutoff (6.5%)')
plt.axhline(y=126, color='darkred', linestyle='--', linewidth=1.5, label='ADA Glucose Cutoff (126 mg/dL)')
plt.title("Bivariate Clinical Quadrant (HbA1c vs Glucose Level) [Sample n=3,000]", fontsize=13, fontweight='bold')
plt.xlabel("HbA1c Level (%)")
plt.ylabel("Blood Glucose Level (mg/dL)")
plt.legend(title="Diabetes Outcome", loc='upper left')
plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 1.6 Correlation Matrix Heatmap"""))
    cells.append(nbf.v4.new_code_cell("""# Compute correlation for numerical + encoded columns
corr_df = df.copy()
corr_df['gender'] = corr_df['gender'].astype('category').cat.codes
corr_df['smoking_history'] = corr_df['smoking_history'].astype('category').cat.codes
corr_matrix = corr_df.corr()

plt.figure(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, annot=True, fmt=".3f", cmap='coolwarm', vmin=-0.2, vmax=1.0, 
            mask=mask, square=True, linewidths=0.5)
plt.title("Feature Correlation Heatmap with Target 'diabetes'", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
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
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.join("..", "training_scripts"))
from data_loader import prepare_splits, load_raw_dataset, FEATURE_COLUMNS, TARGET_COLUMN

print("Executing stratified dataset preparation...")
splits = prepare_splits(test_size=0.2, val_size=0.1, random_state=42)

print(f"Training set:   {splits['X_train'].shape[0]:,} samples")
print(f"Validation set: {splits['X_val'].shape[0]:,} samples")
print(f"Test set:       {splits['X_test'].shape[0]:,} samples")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 2.1 Visualizing Class Proportions Across Splits (Stratification Proof)"""))
    cells.append(nbf.v4.new_code_cell("""split_names = ['Training Set (70k)', 'Validation Set (10k)', 'Test Set (20k)']
pos_rates = [np.mean(splits['y_train']) * 100, np.mean(splits['y_val']) * 100, np.mean(splits['y_test']) * 100]

plt.figure(figsize=(9, 4))
bars = plt.bar(split_names, pos_rates, color=['#0d9488', '#0284c7', '#6366f1'], width=0.45)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold')

plt.axhline(y=8.5, color='red', linestyle='--', label='Population Positive Rate (8.50%)')
plt.ylabel("Positive Diabetic Class Rate (%)")
plt.ylim(0, 12)
plt.title("Stratified Class Balance Preservation Across Splits", fontsize=13, fontweight='bold')
plt.legend()
plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 2.2 Feature Scaling Transformation Visualizer (Raw vs Standardized)"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# Raw vs Scaled BMI
sns.kdeplot(splits['df_train']['bmi'], color='purple', fill=True, ax=axes[0, 0])
axes[0, 0].set_title("BMI Distribution - Raw ($kg/m^2$)", fontsize=11, fontweight='bold')

scaled_bmi = splits['X_train'][:, FEATURE_COLUMNS.index('bmi')]
sns.kdeplot(scaled_bmi, color='teal', fill=True, ax=axes[0, 1])
axes[0, 1].set_title("BMI Distribution - Standardized (Z-Score)", fontsize=11, fontweight='bold')

# Raw vs Scaled Glucose
sns.kdeplot(splits['df_train']['blood_glucose_level'], color='purple', fill=True, ax=axes[1, 0])
axes[1, 0].set_title("Blood Glucose Distribution - Raw ($mg/dL$)", fontsize=11, fontweight='bold')

scaled_glucose = splits['X_train'][:, FEATURE_COLUMNS.index('blood_glucose_level')]
sns.kdeplot(scaled_glucose, color='teal', fill=True, ax=axes[1, 1])
axes[1, 1].set_title("Blood Glucose Distribution - Standardized (Z-Score)", fontsize=11, fontweight='bold')

plt.tight_layout()
plt.show()
"""))
    
    nb.cells = cells
    filepath = os.path.join(NOTEBOOKS_DIR, "02_data_preprocessing.ipynb")
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Built {filepath}")

def build_nb03():
    nb = nbf.v4.new_notebook()
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""# NOTEBOOK 03: MACHINE LEARNING MODEL TRAINING & BENCHMARKING
We train and benchmark 3 classical ML models:
1. **Logistic Regression** (with cost-sensitive class balancing)
2. **Random Forest Classifier** (ensemble of decision trees)
3. **XGBoost Classifier** (extreme gradient boosted trees)
"""))
    
    cells.append(nbf.v4.new_code_cell("""import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    roc_curve, precision_recall_curve, confusion_matrix
)

sys.path.append(os.path.join("..", "training_scripts"))
from data_loader import prepare_splits, FEATURE_COLUMNS

data = prepare_splits()
X_train, y_train = data['X_train'], data['y_train']
X_val, y_val = data['X_val'], data['y_val']
X_test, y_test = data['X_test'], data['y_test']
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 3.1 Model Training & Validation Benchmark"""))
    cells.append(nbf.v4.new_code_cell("""models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, eval_metric="logloss")
}

val_results = []
fitted_models = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    fitted_models[name] = model
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

res_df = pd.DataFrame(val_results)
res_df
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 3.2 Visual Performance Comparison (Grouped Bar Chart)"""))
    cells.append(nbf.v4.new_code_cell("""metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
melted_df = pd.melt(res_df, id_vars=['Model'], value_vars=metrics, var_name='Metric', value_name='Score')

plt.figure(figsize=(13, 6))
sns.barplot(data=melted_df, x='Metric', y='Score', hue='Model', palette=['#38bdf8', '#34d399', '#f59e0b'])
plt.ylim(0.3, 1.05)
plt.title("Validation Performance Metrics Comparison Across Models", fontsize=14, fontweight='bold')
plt.ylabel("Score")
plt.legend(loc='lower right', frameon=True)
plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 3.3 Receiver Operating Characteristic (ROC) & Precision-Recall Curves"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(15, 6))

colors = {'Logistic Regression': '#38bdf8', 'Random Forest': '#34d399', 'XGBoost': '#f59e0b'}

# ROC Curves
for name, model in fitted_models.items():
    y_prob = model.predict_proba(X_val)[:, 1]
    fpr, tpr, _ = roc_curve(y_val, y_prob)
    auc_score = roc_auc_score(y_val, y_prob)
    axes[0].plot(fpr, tpr, label=f"{name} (AUC = {auc_score:.4f})", color=colors[name], linewidth=2)

axes[0].plot([0, 1], [0, 1], 'k--', label="Chance Level (AUC = 0.50)")
axes[0].set_title("ROC Curves Comparison", fontsize=13, fontweight='bold')
axes[0].set_xlabel("False Positive Rate (1 - Specificity)")
axes[0].set_ylabel("True Positive Rate (Sensitivity / Recall)")
axes[0].legend(loc='lower right')

# Precision-Recall Curves (crucial for imbalanced datasets)
for name, model in fitted_models.items():
    y_prob = model.predict_proba(X_val)[:, 1]
    prec, rec, _ = precision_recall_curve(y_val, y_prob)
    axes[1].plot(rec, prec, label=f"{name}", color=colors[name], linewidth=2)

axes[1].set_title("Precision-Recall Curves (Minority Class Assessment)", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Recall")
axes[1].set_ylabel("Precision")
axes[1].legend(loc='lower left')

plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 3.4 Confusion Matrix Comparison on Validation Set"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, (name, model) in enumerate(fitted_models.items()):
    y_pred = model.predict(X_val)
    cm = confusion_matrix(y_val, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx], cbar=False,
                xticklabels=['Non-Diabetic', 'Diabetic'], yticklabels=['Non-Diabetic', 'Diabetic'])
    axes[idx].set_title(f"Confusion Matrix: {name}", fontsize=12, fontweight='bold')
    axes[idx].set_xlabel("Predicted Label")
    axes[idx].set_ylabel("Actual Label")

plt.tight_layout()
plt.show()
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
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

sys.path.append(os.path.join("..", "training_scripts"))
from data_loader import prepare_splits
from train_dl import DiabetesMLP

data = prepare_splits()
X_train, y_train = data['X_train'], data['y_train']
X_val, y_val = data['X_val'], data['y_val']
X_test, y_test = data['X_test'], data['y_test']

print(f"PyTorch version: {torch.__version__}")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 4.1 Training PyTorch MLP with Epoch Monitoring"""))
    cells.append(nbf.v4.new_code_cell("""model = DiabetesMLP(input_dim=8)
pos_weight = torch.tensor([np.sum(y_train == 0) / (np.sum(y_train == 1) + 1e-5)], dtype=torch.float32)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32).unsqueeze(1))
val_ds = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.float32).unsqueeze(1))
train_loader = DataLoader(train_ds, batch_size=256, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=256, shuffle=False)

epochs = 10
history = {'train_loss': [], 'val_loss': [], 'val_f1': [], 'val_recall': []}

for epoch in range(1, epochs + 1):
    model.train()
    t_loss = 0.0
    for bx, by in train_loader:
        optimizer.zero_grad()
        loss = criterion(model(bx), by)
        loss.backward()
        optimizer.step()
        t_loss += loss.item() * len(bx)
    t_loss /= len(train_ds)
    
    model.eval()
    v_loss = 0.0
    val_preds, val_targets = [], []
    with torch.no_grad():
        for bx, by in val_loader:
            logits = model(bx)
            v_loss += criterion(logits, by).item() * len(bx)
            probs = torch.sigmoid(logits).cpu().numpy().flatten()
            val_preds.extend((probs >= 0.5).astype(int))
            val_targets.extend(by.cpu().numpy().flatten())
            
    v_loss /= len(val_ds)
    vf1 = f1_score(val_targets, val_preds)
    vrec = recall_score(val_targets, val_preds)
    
    history['train_loss'].append(t_loss)
    history['val_loss'].append(v_loss)
    history['val_f1'].append(vf1)
    history['val_recall'].append(vrec)
    print(f"Epoch {epoch:02d} | Train Loss: {t_loss:.4f} | Val Loss: {v_loss:.4f} | Val F1: {vf1:.4f} | Val Recall: {vrec:.4f}")
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 4.2 Training Dynamics Curves (Loss & Metric Convergence)"""))
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Loss Curves
axes[0].plot(range(1, epochs + 1), history['train_loss'], 'o-', color='#0284c7', label='Training Loss', linewidth=2)
axes[0].plot(range(1, epochs + 1), history['val_loss'], 's-', color='#ea580c', label='Validation Loss', linewidth=2)
axes[0].set_title("PyTorch MLP Loss Convergence Across Epochs", fontsize=12, fontweight='bold')
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Weighted BCE Loss")
axes[0].legend()

# Performance Evolution
axes[1].plot(range(1, epochs + 1), history['val_f1'], '^-', color='#10b981', label='Validation F1-Score', linewidth=2)
axes[1].plot(range(1, epochs + 1), history['val_recall'], 'd-', color='#8b5cf6', label='Validation Recall', linewidth=2)
axes[1].set_title("Validation Metric Evolution (High Recall for Screening)", fontsize=12, fontweight='bold')
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Score")
axes[1].legend()

plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 4.3 Output Probability Calibration & Separation Margin"""))
    cells.append(nbf.v4.new_code_cell("""model.eval()
with torch.no_grad():
    test_logits = model(torch.tensor(X_test, dtype=torch.float32))
    test_probs = torch.sigmoid(test_logits).cpu().numpy().flatten()

plt.figure(figsize=(10, 5))
sns.kdeplot(test_probs[y_test == 0], color='#0284c7', fill=True, label='Actual Non-Diabetic (0)', alpha=0.5)
sns.kdeplot(test_probs[y_test == 1], color='#ef4444', fill=True, label='Actual Diabetic (1)', alpha=0.5)
plt.axvline(x=0.5, color='black', linestyle='--', label='Decision Threshold (0.50)')
plt.title("PyTorch Output Probability Distribution (Class Separation)", fontsize=13, fontweight='bold')
plt.xlabel("Predicted Probability of Diabetes")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.show()
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
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, roc_auc_score

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
    
    cells.append(nbf.v4.new_markdown_cell("""### 5.1 Test Set Confusion Matrix Comparison (XGBoost vs PyTorch MLP)"""))
    cells.append(nbf.v4.new_code_cell("""# ML Predictions
y_pred_ml = ml_model.predict(X_test)
cm_ml = confusion_matrix(y_test, y_pred_ml)

# DL Predictions
with torch.no_grad():
    y_prob_dl = torch.sigmoid(dl_model(torch.tensor(X_test, dtype=torch.float32))).cpu().numpy().flatten()
    y_pred_dl = (y_prob_dl >= 0.5).astype(int)
cm_dl = confusion_matrix(y_test, y_pred_dl)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.heatmap(cm_ml, annot=True, fmt='d', cmap='Blues', ax=axes[0], cbar=False,
            xticklabels=['Non-Diabetic', 'Diabetic'], yticklabels=['Non-Diabetic', 'Diabetic'])
axes[0].set_title(f"XGBoost Test Confusion Matrix (Acc: {np.mean(y_pred_ml==y_test)*100:.2f}%)", fontsize=12, fontweight='bold')
axes[0].set_xlabel("Predicted")
axes[0].set_ylabel("Actual")

sns.heatmap(cm_dl, annot=True, fmt='d', cmap='Purples', ax=axes[1], cbar=False,
            xticklabels=['Non-Diabetic', 'Diabetic'], yticklabels=['Non-Diabetic', 'Diabetic'])
axes[1].set_title(f"PyTorch MLP Test Confusion Matrix (Recall: {np.sum((y_pred_dl==1)&(y_test==1))/np.sum(y_test==1)*100:.2f}%)", fontsize=12, fontweight='bold')
axes[1].set_xlabel("Predicted")
axes[1].set_ylabel("Actual")

plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 5.2 Global SHAP Feature Importance (Bar Chart & Beeswarm Plot)"""))
    cells.append(nbf.v4.new_code_cell("""explainer = shap.TreeExplainer(ml_model)
sample_X = X_test[:300]
shap_values = explainer.shap_values(sample_X)
if isinstance(shap_values, list) and len(shap_values) == 2:
    shap_values = shap_values[1]

# Global Bar Chart
mean_shap = np.mean(np.abs(shap_values), axis=0)
shap_df = pd.DataFrame({"Feature": FEATURE_COLUMNS, "Mean_Absolute_SHAP": mean_shap})
shap_df = shap_df.sort_values(by="Mean_Absolute_SHAP", ascending=True)

plt.figure(figsize=(10, 5))
plt.barh(shap_df['Feature'], shap_df['Mean_Absolute_SHAP'], color='#0d9488', edgecolor='black', linewidth=0.5)
plt.title("Global Feature Importance via SHAP Values (Mean |SHAP|)", fontsize=13, fontweight='bold')
plt.xlabel("Mean Absolute SHAP Impact on Model Output")
plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 5.3 SHAP Beeswarm Summary Plot (Direction of Feature Impact)"""))
    cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, sample_X, feature_names=FEATURE_COLUMNS, show=False)
plt.title("SHAP Beeswarm Summary (Feature Value vs Risk Direction)", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""### 5.4 Individual Patient Local Prediction Interpretability (SHAP Waterfall/Local Bar)"""))
    cells.append(nbf.v4.new_code_cell("""# Compare a High Risk Patient vs Low Risk Patient
high_risk_idx = np.where(y_test == 1)[0][0]
low_risk_idx = np.where(y_test == 0)[0][0]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# High risk patient contribution
high_shap = explainer.shap_values(X_test[high_risk_idx:high_risk_idx+1])
if isinstance(high_shap, list): high_shap = high_shap[1]
high_series = pd.Series(high_shap[0], index=FEATURE_COLUMNS).sort_values()

axes[0].barh(high_series.index, high_series.values, color=['#ef4444' if x > 0 else '#38bdf8' for x in high_series.values])
axes[0].set_title(f"Case #1 (Diabetic Patient): Individual SHAP Attribution", fontsize=12, fontweight='bold')
axes[0].set_xlabel("SHAP Impact (+ raises risk, - lowers risk)")
axes[0].axvline(0, color='gray', linestyle='--')

# Low risk patient contribution
low_shap = explainer.shap_values(X_test[low_risk_idx:low_risk_idx+1])
if isinstance(low_shap, list): low_shap = low_shap[1]
low_series = pd.Series(low_shap[0], index=FEATURE_COLUMNS).sort_values()

axes[1].barh(low_series.index, low_series.values, color=['#ef4444' if x > 0 else '#38bdf8' for x in low_series.values])
axes[1].set_title(f"Case #2 (Non-Diabetic Patient): Individual SHAP Attribution", fontsize=12, fontweight='bold')
axes[1].set_xlabel("SHAP Impact (+ raises risk, - lowers risk)")
axes[1].axvline(0, color='gray', linestyle='--')

plt.tight_layout()
plt.show()
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
    print("All 5 rich-visualization Jupyter notebooks generated successfully.")
