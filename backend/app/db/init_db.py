from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.audit import AuditLog
from app.models.decision import Decision
from app.models.metric import ModelMetric
from app.models.order import Order
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.demo_data_service import bootstrap_demo_operations


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

        if not db.query(Order).count():
            bootstrap_demo_operations(db, n_orders=180)
    finally:
        db.close()
