import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.core.config import get_settings


class ModelService:
    def __init__(self) -> None:
        settings = get_settings()
        self.delay_model = self._load_model(settings.model_delay_path)
        self.noshow_model = self._load_model(settings.model_noshow_path)
        self.reschedule_model = self._load_model(settings.model_reschedule_path)
        self.sla_model = self._load_model(settings.model_sla_path)
        self.feature_columns = self._load_feature_columns(settings.feature_columns_path)

    @staticmethod
    def _load_model(path: str):
        p = Path(path)
        return joblib.load(p) if p.exists() else None

    @staticmethod
    def _load_feature_columns(path: str) -> list[str]:
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return [
            "technician_load",
            "distance_km",
            "previous_reschedules",
            "customer_history_no_show",
            "rain_level",
            "traffic_level",
            "backlog_region",
            "sla_hours_remaining",
            "estimated_duration_minutes",
            "priority_encoded",
            "service_type_encoded",
            "region_encoded",
        ]

    def _encode(self, features: dict) -> dict:
        priority_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        service_map = {"installation": 0, "repair": 1, "inspection": 2, "maintenance": 3, "emergency": 4}
        region_map = {"north": 0, "south": 1, "east": 2, "west": 3, "central": 4}

        encoded = dict(features)
        encoded["priority_encoded"] = priority_map.get(str(features.get("priority", "medium")).lower(), 1)
        encoded["service_type_encoded"] = service_map.get(str(features.get("service_type", "maintenance")).lower(), 3)
        encoded["region_encoded"] = region_map.get(str(features.get("region", "central")).lower(), 4)
        return encoded

    def _predict_single(self, model, encoded: dict, fallback_formula: float) -> float:
        if model is None:
            return float(np.clip(fallback_formula, 0.05, 0.98))
        frame = pd.DataFrame([{c: encoded.get(c, 0) for c in self.feature_columns}])
        proba = model.predict_proba(frame)[0][1]
        return float(np.clip(proba, 0.01, 0.99))

    def score(self, features: dict) -> dict:
        encoded = self._encode(features)
        fallback_delay = (
            0.25
            + 0.018 * encoded.get("technician_load", 0)
            + 0.03 * encoded.get("traffic_level", 0)
            + 0.02 * encoded.get("backlog_region", 0)
            - 0.015 * encoded.get("sla_hours_remaining", 0)
        )
        fallback_noshow = 0.12 + 0.05 * encoded.get("customer_history_no_show", 0) + 0.01 * encoded.get("rain_level", 0)
        fallback_reschedule = 0.18 + 0.04 * encoded.get("previous_reschedules", 0) + 0.02 * encoded.get("distance_km", 0) / 10
        fallback_sla = (
            0.2
            + 0.016 * encoded.get("backlog_region", 0)
            + 0.15 * encoded.get("traffic_level", 0)
            + 0.12 * encoded.get("rain_level", 0)
            - 0.02 * encoded.get("sla_hours_remaining", 0)
        )

        delay = self._predict_single(self.delay_model, encoded, fallback_delay)
        no_show = self._predict_single(self.noshow_model, encoded, fallback_noshow)
        reschedule = self._predict_single(self.reschedule_model, encoded, fallback_reschedule)
        sla_breach = self._predict_single(self.sla_model, encoded, fallback_sla)

        factors = self.explain_factors(encoded)
        overall = float(np.clip((delay * 0.35) + (no_show * 0.2) + (reschedule * 0.2) + (sla_breach * 0.25), 0.0, 1.0))
        return {
            "delay_risk": delay,
            "no_show_risk": no_show,
            "reschedule_risk": reschedule,
            "sla_breach_risk": sla_breach,
            "overall_risk": overall,
            "factors": factors,
        }

    def explain_factors(self, encoded: dict) -> list[dict]:
        importance = {
            "technician_load": 0.18,
            "traffic_level": 0.17,
            "backlog_region": 0.14,
            "sla_hours_remaining": -0.16,
            "previous_reschedules": 0.13,
            "customer_history_no_show": 0.12,
            "distance_km": 0.10,
        }
        scored = []
        for feature, weight in importance.items():
            value = float(encoded.get(feature, 0))
            contribution = round(value * weight, 4)
            scored.append({"feature": feature, "value": value, "weight": weight, "contribution": contribution})
        scored.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return scored[:5]


model_service = ModelService()
