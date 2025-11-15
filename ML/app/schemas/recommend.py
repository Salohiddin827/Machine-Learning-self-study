from pydantic import BaseModel
from typing import List, Dict

class RecommendResponse(BaseModel):
    prediction: float
    causes: Dict
    actions_ranked: List[Dict]
    