from __future__ import annotations

from datetime import timedelta

from app.services.economic_impact import calculate_economic_impact


class ScenarioGenerationAgent:
    def run(self, order: dict, risk: dict, technicians: list[dict]) -> list[dict]:
        current_start = order["scheduled_start"]
        current_end = order["scheduled_end"]
        service_skill = order.get("technician_skill", "")
        region = order.get("region", "central")

        candidate_same_region = next(
            (
                tech
                for tech in technicians
                if tech["region"] == region and tech["status"] == "available" and service_skill in tech["skills"]
            ),
            None,
        )
        candidate_adjacent = next(
            (
                tech
                for tech in technicians
                if tech["region"] != region and tech["status"] == "available" and service_skill in tech["skills"]
            ),
            None,
        )

        scenario_blueprints = [
            {
                "scenario_code": "KEEP_CURRENT",
                "scenario_type": "keep_current_schedule",
                "recommended_technician_id": order.get("technician_id"),
                "recommended_start": current_start,
                "recommended_end": current_end,
                "travel_delta": 0.0,
                "risk_reduction": 0.0,
                "feasible": True,
                "policy_flags": [],
            },
            {
                "scenario_code": "SHIFT_WITHIN_TECH",
                "scenario_type": "move_within_same_technician_window",
                "recommended_technician_id": order.get("technician_id"),
                "recommended_start": current_start - timedelta(minutes=45),
                "recommended_end": current_end - timedelta(minutes=45),
                "travel_delta": 6.0,
                "risk_reduction": 0.14,
                "feasible": order.get("technician_load", 0) <= 10,
                "policy_flags": [] if order.get("technician_load", 0) <= 10 else ["technician_overload"],
            },
            {
                "scenario_code": "REASSIGN_SAME_REGION",
                "scenario_type": "assign_same_region",
                "recommended_technician_id": candidate_same_region["external_code"] if candidate_same_region else None,
                "recommended_start": current_start,
                "recommended_end": current_end,
                "travel_delta": 12.0,
                "risk_reduction": 0.27,
                "feasible": candidate_same_region is not None,
                "policy_flags": [] if candidate_same_region else ["no_same_region_technician"],
            },
            {
                "scenario_code": "REASSIGN_ADJACENT_REGION",
                "scenario_type": "assign_adjacent_region",
                "recommended_technician_id": candidate_adjacent["external_code"] if candidate_adjacent else None,
                "recommended_start": current_start + timedelta(minutes=20),
                "recommended_end": current_end + timedelta(minutes=20),
                "travel_delta": 28.0,
                "risk_reduction": 0.22,
                "feasible": candidate_adjacent is not None,
                "policy_flags": [] if candidate_adjacent else ["no_adjacent_region_technician"],
            },
            {
                "scenario_code": "PRIORITIZE_AND_SWAP",
                "scenario_type": "prioritize_and_deprioritize_lower_impact_order",
                "recommended_technician_id": order.get("technician_id"),
                "recommended_start": current_start - timedelta(minutes=75),
                "recommended_end": current_end - timedelta(minutes=75),
                "travel_delta": 9.0,
                "risk_reduction": 0.32,
                "feasible": order.get("priority") in {"high", "critical"},
                "policy_flags": [] if order.get("priority") in {"high", "critical"} else ["priority_precedence_violation"],
            },
            {
                "scenario_code": "MANUAL_ESCALATION",
                "scenario_type": "flag_manual_intervention",
                "recommended_technician_id": None,
                "recommended_start": None,
                "recommended_end": None,
                "travel_delta": 0.0,
                "risk_reduction": 0.08,
                "feasible": True,
                "policy_flags": ["manual_intervention_required"],
            },
        ]

        scenarios: list[dict] = []
        for item in scenario_blueprints:
            impact = calculate_economic_impact(order, risk, item["risk_reduction"], item["travel_delta"])
            scenarios.append(
                {
                    "scenario_code": item["scenario_code"],
                    "scenario_type": item["scenario_type"],
                    "recommended_technician_id": item["recommended_technician_id"],
                    "recommended_start": item["recommended_start"],
                    "recommended_end": item["recommended_end"],
                    "projected_travel_delta_minutes": item["travel_delta"],
                    "projected_risk_reduction": item["risk_reduction"],
                    "projected_cost_of_action": impact["projected_cost_of_action"],
                    "projected_cost_of_inaction": impact["projected_cost_of_inaction"],
                    "projected_loss_avoided": impact["projected_total_loss_avoided"],
                    "feasibility_status": "feasible" if item["feasible"] else "infeasible",
                    "policy_flags_json": {"flags": item["policy_flags"]},
                    "impact_breakdown": impact,
                }
            )
        return scenarios
