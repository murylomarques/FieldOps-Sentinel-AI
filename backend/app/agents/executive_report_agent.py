from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.recommendation import Recommendation


class ExecutiveReportAgent:
    def run(self, db: Session) -> dict:
        backlog = db.query(Order.region, func.count(Order.id)).group_by(Order.region).all()
        risks = (
            db.query(Order.region, func.avg(Recommendation.impact_score), func.count(Recommendation.id))
            .join(Recommendation, Recommendation.order_id == Order.order_id)
            .group_by(Order.region)
            .all()
        )

        bottlenecks = [f"{region} backlog: {count}" for region, count in sorted(backlog, key=lambda x: x[1], reverse=True)[:3]]
        high_risk = [region for region, avg_risk, _ in risks if (avg_risk or 0) > 0.55]
        loads = (
            db.query(Order.technician_id, func.avg(Order.technician_load))
            .group_by(Order.technician_id)
            .having(func.avg(Order.technician_load) > 8)
            .all()
        )
        load_alerts = [f"{tech}: load {avg_load:.1f}" for tech, avg_load in loads[:5]]

        critical_backlog = (
            db.query(Order)
            .filter(Order.priority.in_(["high", "critical"]))
            .count()
        )

        risk_orders_next_hours = (
            db.query(Recommendation)
            .filter(Recommendation.impact_score > 0.6)
            .count()
        )

        return {
            "key_bottlenecks": bottlenecks,
            "high_risk_regions": high_risk,
            "technician_load_alerts": load_alerts,
            "critical_backlog": critical_backlog,
            "risk_orders_next_hours": risk_orders_next_hours,
        }
