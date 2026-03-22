import argparse
import json
from pathlib import Path

import pandas as pd
import requests


DATA_PATH = Path("ml/data/synthetic_orders.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--email", default="dispatcher@fieldops.ai")
    parser.add_argument("--password", default="dispatcher123")
    parser.add_argument("--rows", type=int, default=120)
    args = parser.parse_args()

    if not DATA_PATH.exists():
        raise FileNotFoundError("Synthetic dataset not found. Run ml/scripts/generate_synthetic_data.py first")

    login = requests.post(
        f"{args.base_url}/api/v1/auth/login",
        json={"email": args.email, "password": args.password},
        timeout=20,
    )
    login.raise_for_status()
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    df = pd.read_csv(DATA_PATH).head(args.rows)

    success = 0
    for _, row in df.iterrows():
        payload = {
            "order_id": row["order_id"],
            "customer_id": row["customer_id"],
            "city": row["city"],
            "region": row["region"],
            "service_type": row["service_type"],
            "priority": row["priority"],
            "created_at": row["created_at"],
            "scheduled_start": row["scheduled_start"],
            "scheduled_end": row["scheduled_end"],
            "technician_id": row["technician_id"],
            "technician_skill": row["technician_skill"],
            "technician_load": int(row["technician_load"]),
            "distance_km": float(row["distance_km"]),
            "previous_reschedules": int(row["previous_reschedules"]),
            "customer_history_no_show": int(row["customer_history_no_show"]),
            "rain_level": float(row["rain_level"]),
            "traffic_level": float(row["traffic_level"]),
            "backlog_region": int(row["backlog_region"]),
            "sla_hours_remaining": float(row["sla_hours_remaining"]),
            "estimated_duration_minutes": int(row["estimated_duration_minutes"]),
        }
        response = requests.post(f"{args.base_url}/api/v1/orders", json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            success += 1

    print(json.dumps({"inserted": success, "requested": args.rows}, indent=2))


if __name__ == "__main__":
    main()
