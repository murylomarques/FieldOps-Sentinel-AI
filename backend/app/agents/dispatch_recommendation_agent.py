from datetime import timedelta


class DispatchRecommendationAgent:
    def run(self, payload: dict, risk: dict) -> dict:
        overall = risk["overall_risk"]
        scheduled_start = payload["scheduled_start"]

        if overall >= 0.75:
            recommended_priority = "critical"
            action_type = "expedite_reassignment"
            window = f"{scheduled_start.isoformat()} to {(scheduled_start + timedelta(hours=1)).isoformat()}"
            confidence = 0.88
            impact = 0.82
        elif overall >= 0.55:
            recommended_priority = "high"
            action_type = "priority_boost"
            window = f"{scheduled_start.isoformat()} to {(scheduled_start + timedelta(hours=2)).isoformat()}"
            confidence = 0.77
            impact = 0.64
        else:
            recommended_priority = payload.get("priority", "medium")
            action_type = "monitor"
            window = f"{scheduled_start.isoformat()} to {(scheduled_start + timedelta(hours=3)).isoformat()}"
            confidence = 0.66
            impact = 0.31

        alt_region = payload["region"]
        if payload.get("technician_load", 0) >= 9 and payload["region"] != "central":
            alt_region = "central"

        technician = payload["technician_id"]
        if overall >= 0.7:
            technician = f"backup-{payload['region']}-01"

        return {
            "recommended_priority": recommended_priority,
            "recommended_technician_id": technician,
            "recommended_region": alt_region,
            "recommended_window": window,
            "action_type": action_type,
            "confidence": confidence,
            "impact_score": impact,
            "requires_human_approval": overall >= 0.55,
        }
