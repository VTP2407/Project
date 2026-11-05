import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

sys.path.append(os.path.dirname(__file__))
from data_loader import prepare_splits, SAVED_MODELS_DIR

BACKEND_SAVED_MODELS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app", "ml", "saved_models")
)

class DiabetesMLP(nn.Module):
    def __init__(self, input_dim: int = 8, hidden_dim1: int = 64, hidden_dim2: int = 32, dropout_rate: float = 0.2):
        super(DiabetesMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.BatchNorm1d(hidden_dim1),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.BatchNorm1d(hidden_dim2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim2, 1) # Logits
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

def train_dl_model(epochs: int = 20, batch_size: int = 256, lr: float = 0.001):
    print("Preparing data splits for PyTorch Deep Learning...")
    data = prepare_splits()
    
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    X_test, y_test = data["X_test"], data["y_test"]
    
    # Calculate pos_weight for BCEWithLogitsLoss due to 8.5% class imbalance
    num_neg = np.sum(y_train == 0)
    num_pos = np.sum(y_train == 1)
    pos_weight = torch.tensor([num_neg / (num_pos + 1e-5)], dtype=torch.float32)
    print(f"Class counts in training: Neg={num_neg}, Pos={num_pos}. pos_weight: {pos_weight.item():.2f}")
    
    # Convert to Tensors
    train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32).unsqueeze(1))
    val_dataset = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.float32).unsqueeze(1))
    test_dataset = TensorDataset(torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test, dtype=torch.float32).unsqueeze(1))
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = DiabetesMLP(input_dim=X_train.shape[1]).to(device)
    pos_weight = pos_weight.to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    
    best_val_f1 = 0.0
    best_weights_path = os.path.join(SAVED_MODELS_DIR, "diabetes_dl_model.pth")
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    
    history = {
        "train_loss": [],
        "val_loss": [],
        "val_f1": []
    }
    
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            logits = model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(bx)
        train_loss /= len(train_dataset)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_preds, val_targets = [], []
        with torch.no_grad():
            for bx, by in val_loader:
                bx, by = bx.to(device), by.to(device)
                logits = model(bx)
                loss = criterion(logits, by)
                val_loss += loss.item() * len(bx)
                probs = torch.sigmoid(logits).cpu().numpy().flatten()
                val_preds.extend((probs >= 0.5).astype(int))
                val_targets.extend(by.cpu().numpy().flatten())
        
        val_loss /= len(val_dataset)
        val_f1 = f1_score(val_targets, val_preds)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_f1"].append(val_f1)
        
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val F1: {val_f1:.4f}")
        
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            torch.save(model.state_dict(), best_weights_path)
            for out_dir in [SAVED_MODELS_DIR, BACKEND_SAVED_MODELS_DIR]:
                os.makedirs(out_dir, exist_ok=True)
                torch.save(model.state_dict(), os.path.join(out_dir, "diabetes_dl_model.pth"))
    
    # Test evaluation with best model
    model.load_state_dict(torch.load(best_weights_path))
    model.eval()
    test_preds, test_probs, test_targets = [], [], []
    with torch.no_grad():
        for bx, by in test_loader:
            bx = bx.to(device)
            logits = model(bx)
            probs = torch.sigmoid(logits).cpu().numpy().flatten()
            test_probs.extend(probs)
            test_preds.extend((probs >= 0.5).astype(int))
            test_targets.extend(by.numpy().flatten())
            
    dl_metrics = {
        "accuracy": float(accuracy_score(test_targets, test_preds)),
        "precision": float(precision_score(test_targets, test_preds, zero_division=0)),
        "recall": float(recall_score(test_targets, test_preds)),
        "f1_score": float(f1_score(test_targets, test_preds)),
        "roc_auc": float(roc_auc_score(test_targets, test_probs)),
    }
    print(f"\nPyTorch DL Model Test Metrics: {dl_metrics}")
    
    dl_metadata = {
        "model_name": "DiabetesMLP",
        "framework": "PyTorch",
        "architecture": "Linear(8->64)->BN->ReLU->Dropout(0.2)->Linear(64->32)->BN->ReLU->Dropout(0.2)->Linear(32->1)",
        "epochs_trained": epochs,
        "best_val_f1": float(best_val_f1),
        "test_metrics": dl_metrics,
        "history": history
    }
    
    for out_dir in [SAVED_MODELS_DIR, BACKEND_SAVED_MODELS_DIR]:
        with open(os.path.join(out_dir, "dl_model_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(dl_metadata, f, indent=2)

    return model, dl_metadata

if __name__ == "__main__":
    train_dl_model()

