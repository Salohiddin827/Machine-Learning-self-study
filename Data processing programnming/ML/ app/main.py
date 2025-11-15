from fastapi import FastAPI, HTTPException
from app.config import settings
from app.schemas.context import ContextIn
from app.schemas.actions import CauseItem, Action
from app.schemas.recommend import SimulateRequest
from app import storage
from fastapi.middleware.cors import CORSMiddleware
import logging

# import the realtime starter
from app.realtime import start_realtime_poller_on_startup

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = "/api/v1/decision"

@app.on_event("startup")
async def startup_event():
    logger.info("Starting app: %s", settings.APP_NAME)
    # kick off realtime poller if configured
    await start_realtime_poller_on_startup()

@app.post(BASE + "/ingest/context")
def ingest_context(ctx: ContextIn):
    storage.save_context(ctx.dict())
    return {"status": "ok", "used_at": ctx.timestamp}

@app.post(BASE + "/analyze/causes")
def analyze_causes(ctx: ContextIn):
    # lazy import
    from app.engine.cause_analyzer import analyze_causes as analyzer
    result = analyzer(ctx.features)
    # format top_causes
    from app.models.forecast_model import predict
    base_prediction = predict(ctx.features)
    return {"timestamp": ctx.timestamp, "base_prediction": base_prediction, "top_causes": result["top_causes"], "anomalies": result["anomalies"]}

@app.post(BASE + "/generate/actions")
def generate_actions(req: dict):
    from app.engine.action_generator import generate_actions
    causes = req.get("causes", [])
    constraints = req.get("constraints")
    actions = generate_actions(causes, constraints)
    return {"actions": actions}

@app.post(BASE + "/simulate/actions")
def simulate(req: SimulateRequest):
    from app.engine.simulator import simulate_actions
    results = simulate_actions(req.base_features, req.base_prediction, req.actions)
    return {"base_prediction": req.base_prediction, "results": results}

@app.post(BASE + "/recommend")
def recommend(req: dict):
    timestamp = req.get("timestamp")
    location_id = req.get("location_id")
    features = req.get("features", {})
    constraints = req.get("constraints")
    weights = req.get("weights")
    from app.engine.recommender import recommend_pipeline
    res = recommend_pipeline(timestamp, location_id, features, constraints, weights)
    return res

@app.get(BASE + "/models/status")
def models_status():
    return storage.get_model_status()

@app.get(BASE + "/recommendations/latest")
def get_latest_recommendations(limit: int = 10):
    """
    Returns last saved recommendations from realtime poller.
    """
    return storage.get_recommendations(limit)