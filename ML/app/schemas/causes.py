from pydantic import BaseModel
from typing import List, Dict

class CausesResponse(BaseModel):
    causes: Dict[str, float]
    top_causes: List
    