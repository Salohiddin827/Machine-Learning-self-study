def score_actions(simulation_result: dict):
    impact = simulation_result["reduction"]
    final = simulation_result["final_score"]

    return [
        {"action_combo": "best_actions", "impact": impact, "final_score": final}
    ]