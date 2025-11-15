from app.schemas.context import ContextInput

def simulate_actions(ctx: ContextInput, actions: list):
    reduction = 0

    if "Reduce industrial electricity consumption" in actions:
        reduction += 10
    if "Optimize traffic light timing" in actions:
        reduction += 5
    if "Introduce cleaner production technology" in actions:
        reduction += 7
    if "Expand green energy usage" in actions:
        reduction += 8

    final_score = max(0, ctx.energy_use + ctx.traffic_flow - reduction)

    return {
        "original_score": ctx.energy_use + ctx.traffic_flow,
        "reduction": reduction,
        "final_score": final_score
    }
