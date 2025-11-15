from pydantic import BaseModel

class ContextInput(BaseModel):
    energy_use: float
    traffic_flow: float
    temperature: float
    industry_output: float