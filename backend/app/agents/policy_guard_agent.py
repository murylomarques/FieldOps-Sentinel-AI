class PolicyGuardAgent:
    skill_map = {
        "installation": {"installation", "multi"},
        "repair": {"repair", "multi"},
        "inspection": {"inspection", "multi"},
        "maintenance": {"maintenance", "multi"},
        "emergency": {"emergency", "multi"},
    }

    def run(self, payload: dict, recommendation: dict, risk: dict) -> dict:
        flags: list[str] = []
        service = payload.get("service_type", "maintenance")
        tech_skill = payload.get("technician_skill", "")
        if tech_skill not in self.skill_map.get(service, {"multi"}):
            flags.append("technician_skill_mismatch")

        if payload.get("sla_hours_remaining", 999) < 2 and risk["overall_risk"] > 0.65:
            flags.append("critical_sla_violation_risk")

        if recommendation.get("projected_travel_delta_minutes", 0.0) > 45:
            flags.append("travel_delta_too_high")

        if risk.get("sla_breach_risk", risk["overall_risk"]) > 0.8 and recommendation.get("projected_risk_reduction", 0) < 0.2:
            flags.append("insufficient_breach_reduction")

        requires_human = recommendation.get("requires_human_approval", False)
        if recommendation.get("impact_score", 0) > 0.7:
            requires_human = True
            flags.append("high_impact_action")

        if recommendation.get("severity", "low") in {"high", "critical"} and recommendation.get("confidence", 0) < 0.6:
            flags.append("critical_low_confidence")

        blocked = any(
            flag in {"technician_skill_mismatch", "travel_delta_too_high", "insufficient_breach_reduction"}
            for flag in flags
        )
        return {
            "blocked": blocked,
            "requires_human_approval": requires_human,
            "flags": flags,
        }
