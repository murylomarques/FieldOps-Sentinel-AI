import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

CITIES = [
    ("Sao Paulo", "south"),
    ("Rio de Janeiro", "east"),
    ("Belo Horizonte", "central"),
    ("Curitiba", "south"),
    ("Brasilia", "central"),
    ("Salvador", "north"),
    ("Recife", "north"),
    ("Porto Alegre", "south"),
]
SERVICE_TYPES = ["installation", "repair", "inspection", "maintenance", "emergency"]
PRIORITIES = ["low", "medium", "high", "critical"]
SKILL_BY_SERVICE = {
    "installation": "installation",
    "repair": "repair",
    "inspection": "inspection",
    "maintenance": "maintenance",
    "emergency": "emergency",
}


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def generate(n_rows: int = 5000) -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    rows = []

    for i in range(n_rows):
        city, region = CITIES[RNG.integers(0, len(CITIES))]
        service = SERVICE_TYPES[RNG.integers(0, len(SERVICE_TYPES))]
        priority = PRIORITIES[RNG.integers(0, len(PRIORITIES))]
        created_at = now - timedelta(hours=int(RNG.integers(1, 240)))
        scheduled_start = created_at + timedelta(hours=int(RNG.integers(2, 96)))
        duration = int(RNG.integers(45, 240))
        scheduled_end = scheduled_start + timedelta(minutes=duration)

        technician_load = int(RNG.integers(1, 12))
        distance_km = float(np.round(RNG.uniform(1, 55), 2))
        previous_reschedules = int(RNG.integers(0, 5))
        customer_history_no_show = int(RNG.integers(0, 4))
        rain_level = float(np.round(RNG.uniform(0, 1), 2))
        traffic_level = float(np.round(RNG.uniform(0, 1), 2))
        backlog_region = int(RNG.integers(10, 80))
        sla_hours_remaining = float(np.round(RNG.uniform(1, 72), 2))

        priority_encoded = {"low": 0, "medium": 1, "high": 2, "critical": 3}[priority]
        service_encoded = {"installation": 0, "repair": 1, "inspection": 2, "maintenance": 3, "emergency": 4}[service]

        delay_logit = (
            -1.8
            + (0.18 * technician_load)
            + (0.03 * distance_km)
            + (0.5 * traffic_level)
            + (0.015 * backlog_region)
            + (0.28 * previous_reschedules)
            - (0.04 * sla_hours_remaining)
            + (0.15 * priority_encoded)
        )
        noshow_logit = (
            -2.1
            + (0.65 * customer_history_no_show)
            + (0.25 * rain_level)
            + (0.16 * previous_reschedules)
            + (0.1 * service_encoded)
        )
        reschedule_logit = (
            -1.9
            + (0.33 * previous_reschedules)
            + (0.27 * technician_load)
            + (0.21 * traffic_level)
            + (0.02 * distance_km)
            - (0.03 * sla_hours_remaining)
            + (0.18 * priority_encoded)
        )

        delay = int(RNG.random() < sigmoid(np.array([delay_logit]))[0])
        noshow = int(RNG.random() < sigmoid(np.array([noshow_logit]))[0])
        reschedule = int(RNG.random() < sigmoid(np.array([reschedule_logit]))[0])

        rows.append(
            {
                "order_id": f"ORD-{i + 1:06d}",
                "customer_id": f"CUST-{RNG.integers(10000, 99999)}",
                "city": city,
                "region": region,
                "service_type": service,
                "priority": priority,
                "created_at": created_at.isoformat(),
                "scheduled_start": scheduled_start.isoformat(),
                "scheduled_end": scheduled_end.isoformat(),
                "technician_id": f"TECH-{RNG.integers(1, 120):03d}",
                "technician_skill": SKILL_BY_SERVICE[service],
                "technician_load": technician_load,
                "distance_km": distance_km,
                "previous_reschedules": previous_reschedules,
                "customer_history_no_show": customer_history_no_show,
                "rain_level": rain_level,
                "traffic_level": traffic_level,
                "backlog_region": backlog_region,
                "sla_hours_remaining": sla_hours_remaining,
                "estimated_duration_minutes": duration,
                "risk_delay_label": delay,
                "risk_no_show_label": noshow,
                "risk_reschedule_label": reschedule,
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--output", type=str, default="ml/data/synthetic_orders.csv")
    args = parser.parse_args()

    df = generate(args.rows)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"Saved synthetic dataset with {len(df)} rows to {output}")


if __name__ == "__main__":
    main()
