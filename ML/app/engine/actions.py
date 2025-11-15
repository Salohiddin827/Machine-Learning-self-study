from app.schemas.context import ContextInput

def get_actions(ctx: ContextInput):
    actions = []

    if ctx.energy_use > 30:
        actions.append("Reduce industrial electricity consumption")
    if ctx.traffic_flow > 50:
        actions.append("Optimize traffic light timing")
    if ctx.industry_output > 40:
        actions.append("Introduce cleaner production technology")

    actions.append("Expand green energy usage")
    actions.append("Activate air quality alert level")

    return actions