
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

        requires_human = recommendation.get("requires_human_approval", False)
        if recommendation.get("impact_score", 0) > 0.7:
            requires_human = True
            flags.append("high_impact_action")

        blocked = "technician_skill_mismatch" in flags
        return {
            "blocked": blocked,
            "requires_human_approval": requires_human,
            "flags": flags,
        }
