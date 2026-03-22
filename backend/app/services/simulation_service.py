from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.recommendation import Recommendation


class SimulationService:
    def run_what_if(self, db: Session, payload: dict) -> dict:
        traffic_multiplier = float(payload.get("traffic_multiplier", 1.0))
        weather_multiplier = float(payload.get("weather_multiplier", 1.0))
        region_backlog_delta = int(payload.get("region_backlog_delta", 0))
        unavailable_ids = set(payload.get("technician_unavailable_ids", []))
        sla_buffer_minutes_delta = int(payload.get("sla_buffer_minutes_delta", 0))

        orders = db.query(Order).all()
        recommendations = db.query(Recommendation).all()

        projected_risky = 0
        projected_breaches = 0
        projected_loss_delta = 0.0
        impacted_regions: Counter[str] = Counter()

        for order in orders:
            risk_proxy = (
                (order.traffic_level * traffic_multiplier * 0.33)
                + (order.rain_level * weather_multiplier * 0.18)
                + ((order.backlog_region + region_backlog_delta) / 120 * 0.27)
                + ((max(0.5, order.sla_hours_remaining - (sla_buffer_minutes_delta / 60))) / 48 * -0.18)
                + (order.previous_reschedules * 0.05)
            )
            if order.technician_id in unavailable_ids:
                risk_proxy += 0.3

            if risk_proxy >= 0.55:
                projected_risky += 1
                impacted_regions[order.region] += 1
            if risk_proxy >= 0.72:
                projected_breaches += 1
                projected_loss_delta += order.projected_sla_penalty if hasattr(order, "projected_sla_penalty") else 220.0

        projected_recovery_actions = []
        if unavailable_ids:
            projected_recovery_actions.append("Reassign impacted orders to same-skill technicians in nearby regions.")
        if traffic_multiplier > 1.2:
            projected_recovery_actions.append("Advance high-priority jobs by one slot to protect SLA-critical windows.")
        if weather_multiplier > 1.2:
            projected_recovery_actions.append("Trigger proactive customer confirmation to reduce no-show probability.")
        if not projected_recovery_actions:
            projected_recovery_actions.append("Current operation remains within acceptable resilience limits.")

        baseline_breaches = sum(1 for rec in recommendations if rec.impact_score >= 0.72)
        return {
            "projected_risky_orders": projected_risky,
            "projected_sla_breaches": projected_breaches,
            "projected_breaches_delta": projected_breaches - baseline_breaches,
            "projected_loss_delta": round(projected_loss_delta, 2),
            "top_impacted_regions": [{"region": region, "orders": count} for region, count in impacted_regions.most_common(5)],
            "projected_recovery_actions": projected_recovery_actions,
        }


simulation_service = SimulationService()
