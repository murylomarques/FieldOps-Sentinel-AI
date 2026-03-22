from app.services.model_service import model_service


class RiskScoringAgent:
    def run(self, payload: dict) -> dict:
        return model_service.score(payload)
