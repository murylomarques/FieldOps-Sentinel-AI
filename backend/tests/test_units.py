from app.agents.explainability_agent import ExplainabilityAgent
from app.agents.optimization_agent import OptimizationAgent
from app.agents.policy_guard_agent import PolicyGuardAgent
from app.services.economic_impact import calculate_economic_impact


def test_economic_impact_formula_outputs_positive_values():
    result = calculate_economic_impact(
        {"projected_sla_penalty": 200, "order_value": 500, "customer_history_no_show": 1, "previous_reschedules": 2},
        {"sla_breach_risk": 0.8, "no_show_risk": 0.3, "reschedule_risk": 0.4, "delay_risk": 0.5},
        risk_reduction=0.25,
        travel_delta_minutes=12,
    )
    assert result["projected_cost_of_inaction"] > result["projected_cost_of_action"]
    assert result["projected_total_loss_avoided"] >= 0


def test_policy_guard_blocks_skill_mismatch():
    agent = PolicyGuardAgent()
    response = agent.run(
        {"service_type": "repair", "technician_skill": "installation", "sla_hours_remaining": 1},
        {"impact_score": 0.9, "confidence": 0.4, "severity": "critical", "projected_travel_delta_minutes": 20, "projected_risk_reduction": 0.1},
        {"overall_risk": 0.8, "sla_breach_risk": 0.9},
    )
    assert response["blocked"] is True
    assert "technician_skill_mismatch" in response["flags"]


def test_optimizer_fallback_selects_best_feasible():
    agent = OptimizationAgent()
    scenarios = [
        {"scenario_code": "A", "feasibility_status": "feasible", "projected_loss_avoided": 100, "projected_cost_of_action": 20, "projected_travel_delta_minutes": 5},
        {"scenario_code": "B", "feasibility_status": "feasible", "projected_loss_avoided": 130, "projected_cost_of_action": 60, "projected_travel_delta_minutes": 4},
    ]
    best = agent.run(scenarios)
    assert best["scenario_code"] in {"A", "B"}
    assert "optimizer_score" in best


def test_explainability_builder_contains_three_layers():
    agent = ExplainabilityAgent()
    output = agent.run(
        {"order_id": "ORD-1"},
        {"overall_risk": 0.71, "factors": [{"feature": "backlog_region"}, {"feature": "traffic_level"}, {"feature": "sla_hours_remaining"}]},
        {
            "action_type": "assign_same_region",
            "recommended_technician_id": "TECH-001",
            "recommended_region": "south",
            "recommended_window": "2026-03-22T10:00:00 to 2026-03-22T11:30:00",
            "projected_risk_reduction": 0.22,
            "projected_loss_avoided": 95.4,
        },
        {"flags": []},
    )
    assert "reason_summary" in output
    assert "operational_summary" in output
    assert "executive_summary" in output
