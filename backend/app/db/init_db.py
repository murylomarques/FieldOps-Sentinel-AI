from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.audit import AuditLog
from app.models.decision import Decision
from app.models.human_decision import HumanDecision
from app.models.intervention_scenario import InterventionScenario
from app.models.metric import ModelMetric
from app.models.order import Order
from app.models.order_event import OrderEvent
from app.models.override_feedback import OverrideFeedback
from app.models.recommendation import Recommendation
from app.models.risk_assessment import RiskAssessment
from app.models.technician import Technician
from app.models.user import User
from app.services.demo_data_service import bootstrap_demo_operations, seed_technicians


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).count():
            users = [
                User(email="manager@fieldops.ai", full_name="Operations Manager", role="manager", hashed_password=get_password_hash("manager123")),
                User(email="dispatcher@fieldops.ai", full_name="Dispatch Specialist", role="dispatcher", hashed_password=get_password_hash("dispatcher123")),
                User(email="analyst@fieldops.ai", full_name="Operations Analyst", role="analyst", hashed_password=get_password_hash("analyst123")),
            ]
            db.add_all(users)
            db.commit()

        if not db.query(Technician).count():
            seed_technicians(db)

        if not db.query(Order).count():
            bootstrap_demo_operations(db, n_orders=180)
    finally:
        db.close()
