from fastapi import FastAPI
from app.schemas.context import ContextInput
from app.schemas.simulate import SimulationInput
from app.schemas.recommend import RecommendResponse
from app.engine.model import CarbonModel
from app.engine.xai import explain_prediction
from app.engine.actions import get_actions
from app.engine.simulator import simulate_actions
from app.engine.scoring import score_actions

app = FastAPI(title="Carbon Decision Engine")

model = CarbonModel()

@app.post("/predict")
def predict(ctx: ContextInput):
    pred = model.predict(ctx)
    explanation = explain_prediction(ctx)
    return {"prediction": pred, "explanation": explanation}

@app.post("/diagnose")
def diagnose(ctx: ContextInput):
    explanation = explain_prediction(ctx)
    return {"causes": explanation}

@app.post("/actions")
def actions(ctx: ContextInput):
    return {"actions": get_actions(ctx)}

@app.post("/simulate")
def simulate(input: SimulationInput):
    result = simulate_actions(input.context, input.actions)
    return {"simulation_result": result}

@app.post("/recommend", response_model=RecommendResponse)
def recommend(ctx: ContextInput):
    pred = model.predict(ctx)
    causes = explain_prediction(ctx)
    possible_actions = get_actions(ctx)
    simulation = simulate_actions(ctx, possible_actions)
    ranked = score_actions(simulation)

    return RecommendResponse(
        prediction=pred,
        causes=causes,
        actions_ranked=ranked
    )