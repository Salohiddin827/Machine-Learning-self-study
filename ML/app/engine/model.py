import numpy as np
from app.schemas.context import ContextInput

class CarbonModel:
    def __init__(self):
        # fake demo model
        self.weights = np.array([0.4, 0.3, 0.2, 0.1])

    def predict(self, ctx: ContextInput):
        x = np.array([
            ctx.energy_use,
            ctx.traffic_flow,
            ctx.temperature,
            ctx.industry_output
        ])
        return float(np.dot(self.weights, x))
    