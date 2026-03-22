from __future__ import annotations


def calculate_economic_impact(order: dict, risk: dict, risk_reduction: float, travel_delta_minutes: float) -> dict:
    """Transparent deterministic loss model used by scenario generation.

    Units are local currency points and are intentionally simple for demo reproducibility.
    """

    sla_penalty_base = float(order.get("projected_sla_penalty", 220.0))
    order_value = float(order.get("order_value", 380.0))
    no_show_history = float(order.get("customer_history_no_show", 0))
    reschedules = float(order.get("previous_reschedules", 0))

    breach_risk = float(risk.get("sla_breach_risk", risk.get("overall_risk", 0.0)))
    no_show_risk = float(risk.get("no_show_risk", 0.0))
    reschedule_risk = float(risk.get("reschedule_risk", 0.0))

    projected_sla_penalty = sla_penalty_base * breach_risk
    projected_repeat_visit_loss = order_value * 0.35 * reschedule_risk * (1.0 + (reschedules * 0.08))
    projected_no_show_loss = order_value * 0.22 * no_show_risk * (1.0 + (no_show_history * 0.12))
    projected_delay_loss = order_value * 0.18 * float(risk.get("delay_risk", 0.0))

    projected_cost_of_inaction = (
        projected_sla_penalty
        + projected_repeat_visit_loss
        + projected_no_show_loss
        + projected_delay_loss
    )

    projected_cost_of_action = max(15.0, (travel_delta_minutes * 1.8) + (order_value * 0.045))
    projected_loss_avoided = max(0.0, projected_cost_of_inaction * max(0.0, min(1.0, risk_reduction)) - projected_cost_of_action)

    return {
        "projected_cost_of_inaction": round(projected_cost_of_inaction, 2),
        "projected_cost_of_action": round(projected_cost_of_action, 2),
        "projected_sla_penalty_avoided": round(projected_sla_penalty * risk_reduction, 2),
        "projected_repeat_visit_avoided": round(projected_repeat_visit_loss * risk_reduction, 2),
        "projected_no_show_loss_avoided": round(projected_no_show_loss * risk_reduction, 2),
        "projected_total_loss_avoided": round(projected_loss_avoided, 2),
    }
