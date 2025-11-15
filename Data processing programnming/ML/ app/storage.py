"""
Simple in-memory storage for demo purposes.
Replace with persistent store in production.
"""
from typing import Dict, Any
from datetime import datetime

_store: Dict[str, Any] = {
    "contexts": [],
    "actions_executed": [],
    "recommendations": [],
    "model_status": {
        "anomaly_model": {"version": "1.0.0", "updated_at": datetime.utcnow().isoformat() + "Z", "status": "ready"},
        "forecast_model": {"version": "1.0.0", "updated_at": datetime.utcnow().isoformat() + "Z", "status": "ready"},
        "xai_engine": {"method": "mock_shap", "status": "ready"}
    }
}

def save_context(ctx: Dict):
    _store["contexts"].append(ctx)
    return True

def get_latest_context():
    if not _store["contexts"]:
        return None
    return _store["contexts"][-1]

def save_executed_action(record: Dict):
    _store["actions_executed"].append(record)

def save_recommendation(rec: Dict):
    rec_record = rec.copy()
    rec_record["saved_at"] = datetime.utcnow().isoformat() + "Z"
    _store["recommendations"].append(rec_record)

def get_model_status():
    return _store["model_status"]

def get_recommendations(limit: int = 10):
    return _store["recommendations"][-limit:]