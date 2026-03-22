from datetime import datetime


class IntakeAgent:
    required_fields = [
        "order_id",
        "customer_id",
        "city",
        "region",
        "service_type",
        "priority",
        "scheduled_start",
        "scheduled_end",
        "technician_id",
        "technician_skill",
    ]

    def run(self, payload: dict) -> dict:
        missing = [f for f in self.required_fields if not payload.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        normalized = dict(payload)
        normalized["service_type"] = str(payload["service_type"]).strip().lower()
        normalized["priority"] = str(payload["priority"]).strip().lower()
        normalized["region"] = str(payload["region"]).strip().lower()
        normalized["city"] = str(payload["city"]).strip().title()
        normalized["ingested_at"] = datetime.utcnow().isoformat()

        if normalized["service_type"] in {"emergency", "outage"}:
            normalized["order_class"] = "urgent"
        elif normalized["service_type"] in {"repair", "maintenance"}:
            normalized["order_class"] = "core_ops"
        else:
            normalized["order_class"] = "standard"
        return normalized
