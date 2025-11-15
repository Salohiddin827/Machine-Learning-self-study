from pydantic import BaseModel
from typing import List
from app.schemas.context import ContextInput

class SimulationInput(BaseModel):
    context: ContextInput
    actions: List[str]
    