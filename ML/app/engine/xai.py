from app.schemas.context import ContextInput

def explain_prediction(ctx: ContextInput):
    return {
        "energy_contribution": ctx.energy_use * 0.4,
        "traffic_contribution": ctx.traffic_flow * 0.3,
        "temperature_contribution": ctx.temperature * 0.2,
        "industry_contribution": ctx.industry_output * 0.1,
        "top_causes": sorted(
            {
                "energy": ctx.energy_use * 0.4,
                "traffic": ctx.traffic_flow * 0.3,
                "temperature": ctx.temperature * 0.2,
                "industry": ctx.industry_output * 0.1
            }.items(),
            key=lambda x: x[1],
            reverse=True
        )
    }