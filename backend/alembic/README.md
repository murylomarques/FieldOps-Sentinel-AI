# Alembic

Initialize migrations from `backend/`:
- `alembic revision --autogenerate -m "init"`
- `alembic upgrade head`

Current project still bootstraps schemas with SQLAlchemy `create_all` for local demo startup.
