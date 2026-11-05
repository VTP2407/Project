# Diabetes Prediction Dataset

## Original Source & Preservation Record
- **Original Path**: `C:\Users\Admin\Desktop\_Anaconda\TieuLuanFinal\diabetes_prediction_dataset.csv`
- **SHA-256 Checksum**: `F233FC470E904201F35310D061CB46CA0A6BC7CA5C3E428B769FB4F87F69929B`
- **File Size**: 3,810,356 bytes
- **Total Records**: 100,000 rows
- **Total Features**: 8 predictive features + 1 binary target

## Dataset Schema
| Column | Type | Description | Values / Range |
|---|---|---|---|
| `gender` | Categorical | Patient gender | Female (58.5%), Male (41.4%), Other (0.018%) |
| `age` | Numerical | Age in years | 0.08 - 80.0 |
| `hypertension` | Binary | High blood pressure status | 0 (No), 1 (Yes) |
| `heart_disease` | Binary | History of heart disease | 0 (No), 1 (Yes) |
| `smoking_history` | Categorical | Smoking status | never, No Info, current, former, ever, not current |
| `bmi` | Numerical | Body Mass Index ($kg/m^2$) | 10.01 - 95.69 |
| `HbA1c_level` | Numerical | Glycated hemoglobin test (%) | 3.5 - 9.0 |
| `blood_glucose_level` | Numerical | Blood glucose level ($mg/dL$) | 80 - 300 |
| `diabetes` | Binary (Target) | Diagnosed diabetes | 0: Non-diabetic (91.5%), 1: Diabetic (8.5%) |

## Handling & Compliance
- The original CSV is strictly preserved without modification.
- Imbalanced ratio: ~10.76:1 (91.5% non-diabetic vs 8.5% diabetic).
- Evaluated with precision, recall, F1-score, ROC-AUC, PR-AUC, and minority-class recall.

