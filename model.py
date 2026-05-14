"""
model.py — RandomForest-based link failure prediction.
Exposes: train_model, load_model, predict_link, predict_graph_edges
"""
import numpy as np
import pandas as pd
import pickle, os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

FEATURES    = ["bandwidth", "latency", "packet_loss", "traffic_load"]
MODEL_FILE  = "failure_model.pkl"
SCALER_FILE = "failure_scaler.pkl"


def train_model(df: pd.DataFrame):
    """Train on df, return (model, scaler, metrics_dict)."""
    X = df[FEATURES].values
    y = df["failure"].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_tr)
    X_te = scaler.transform(X_te)
    clf = RandomForestClassifier(n_estimators=150, max_depth=8, min_samples_split=5,
                                 class_weight="balanced", random_state=42, n_jobs=-1)
    clf.fit(X_tr, y_tr)
    y_pred = clf.predict(X_te)
    y_prob = clf.predict_proba(X_te)[:, 1]
    metrics = {
        "accuracy":  round(accuracy_score(y_te, y_pred), 4),
        "precision": round(precision_score(y_te, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_te, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_te, y_pred, zero_division=0), 4),
        "cm":        confusion_matrix(y_te, y_pred).tolist(),
        "feature_importance": dict(zip(FEATURES, clf.feature_importances_.round(4).tolist())),
        "report":    classification_report(y_te, y_pred),
    }
    with open(MODEL_FILE,  "wb") as f: pickle.dump(clf,    f)
    with open(SCALER_FILE, "wb") as f: pickle.dump(scaler, f)
    return clf, scaler, metrics


def load_model():
    """Return (model, scaler) if saved files exist, else (None, None)."""
    if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
        with open(MODEL_FILE,  "rb") as f: clf    = pickle.load(f)
        with open(SCALER_FILE, "rb") as f: scaler = pickle.load(f)
        return clf, scaler
    return None, None


def predict_link(model, scaler, attrs: dict) -> dict:
    """
    Predict failure probability for a single link.
    attrs keys: bandwidth, latency, packet_loss, traffic_load
    Returns: {failure_prob, risk_label}
    """
    if model is None:
        return {"failure_prob": 0.0, "risk_label": "Unknown"}
    row = np.array([[
        attrs.get("bandwidth",    300),
        attrs.get("latency",       20),
        attrs.get("packet_loss",    1),
        attrs.get("traffic_load",  50),
    ]])
    prob = float(model.predict_proba(scaler.transform(row))[0][1])
    if prob < 0.35:   risk = "Low"
    elif prob < 0.65: risk = "Medium"
    else:             risk = "High"
    return {"failure_prob": round(prob, 4), "risk_label": risk}


def predict_graph_edges(model, scaler, G):
    """Update every edge in G with failure_prob and risk_label in-place."""
    if model is None:
        return
    for u, v, data in G.edges(data=True):
        result = predict_link(model, scaler, data)
        G[u][v]["failure_prob"] = result["failure_prob"]
        G[u][v]["risk_label"]   = result["risk_label"]
