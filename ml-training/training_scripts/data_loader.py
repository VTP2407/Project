import os
import joblib
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

RAW_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "datasets", "raw", "diabetes_prediction_dataset.csv")
)
PROCESSED_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
)
SAVED_MODELS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "saved_models")
)

FEATURE_COLUMNS = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "smoking_history",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level"
]
TARGET_COLUMN = "diabetes"

def load_raw_dataset(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw diabetes prediction dataset with verification."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raw dataset not found at {path}")
    df = pd.read_csv(path)
    return df

class PreprocessingPipeline:
    def __init__(self):
        self.le_gender = LabelEncoder()
        self.le_smoke = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_columns = FEATURE_COLUMNS
        self.target_column = TARGET_COLUMN
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        data = df.copy()
        self.le_gender.fit(data["gender"].astype(str))
        self.le_smoke.fit(data["smoking_history"].astype(str))
        
        data["gender"] = self.le_gender.transform(data["gender"].astype(str))
        data["smoking_history"] = self.le_smoke.transform(data["smoking_history"].astype(str))
        
        X = data[self.feature_columns]
        self.scaler.fit(X)
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Pipeline is not fitted yet.")
        data = df.copy()
        
        # Handle unseen categories smoothly
        gender_classes = set(self.le_gender.classes_)
        data["gender"] = data["gender"].apply(lambda x: x if x in gender_classes else self.le_gender.classes_[0])
        data["gender"] = self.le_gender.transform(data["gender"].astype(str))
        
        smoke_classes = set(self.le_smoke.classes_)
        data["smoking_history"] = data["smoking_history"].apply(lambda x: x if x in smoke_classes else "No Info")
        data["smoking_history"] = self.le_smoke.transform(data["smoking_history"].astype(str))
        
        X = data[self.feature_columns]
        return self.scaler.transform(X)

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        return self.fit(df).transform(df)

    def transform_single_dict(self, record: dict) -> np.ndarray:
        df = pd.DataFrame([record])
        return self.transform(df)

    def save(self, filepath: str):
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "PreprocessingPipeline":
        return joblib.load(filepath)

def prepare_splits(test_size: float = 0.2, val_size: float = 0.1, random_state: int = 42):
    """
    Split the dataset into Train / Validation / Test sets with stratification
    to handle class imbalance (8.5% positive).
    """
    df = load_raw_dataset()
    
    # Train + Val vs Test
    df_train_val, df_test = train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=df[TARGET_COLUMN]
    )
    
    # Train vs Val
    val_relative = val_size / (1.0 - test_size)
    df_train, df_val = train_test_split(
        df_train_val, test_size=val_relative, random_state=random_state, stratify=df_train_val[TARGET_COLUMN]
    )
    
    # Fit pipeline ONLY on training set to prevent data leakage
    pipeline = PreprocessingPipeline()
    pipeline.fit(df_train)
    
    X_train = pipeline.transform(df_train)
    y_train = df_train[TARGET_COLUMN].values
    
    X_val = pipeline.transform(df_val)
    y_val = df_val[TARGET_COLUMN].values
    
    X_test = pipeline.transform(df_test)
    y_test = df_test[TARGET_COLUMN].values
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df_train.to_csv(os.path.join(PROCESSED_DIR, "train.csv"), index=False)
    df_val.to_csv(os.path.join(PROCESSED_DIR, "val.csv"), index=False)
    df_test.to_csv(os.path.join(PROCESSED_DIR, "test.csv"), index=False)
    
    return {
        "pipeline": pipeline,
        "df_train": df_train,
        "df_val": df_val,
        "df_test": df_test,
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
    }

