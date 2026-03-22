def test_login_and_me(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@fieldops.ai", "password": "manager123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "manager"


def test_create_order_generates_recommendation(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "dispatcher@fieldops.ai", "password": "dispatcher123"},
    )
    token = login.json()["access_token"]

    payload = {
        "order_id": "ORD-TEST-0001",
        "customer_id": "CUST-9001",
        "city": "Sao Paulo",
        "region": "south",
        "service_type": "repair",
        "priority": "high",
        "created_at": "2026-03-21T10:00:00Z",
        "scheduled_start": "2026-03-21T12:00:00Z",
        "scheduled_end": "2026-03-21T14:00:00Z",
        "technician_id": "TECH-12",
        "technician_skill": "repair",
        "technician_load": 9,
        "distance_km": 26.2,
        "previous_reschedules": 2,
        "customer_history_no_show": 1,
        "rain_level": 0.4,
        "traffic_level": 0.8,
        "backlog_region": 36,
        "sla_hours_remaining": 5.5,
        "estimated_duration_minutes": 150,
    }

    create = client.post(
        "/api/v1/orders",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 200

    queue = client.get(
        "/api/v1/recommendations/queue",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert queue.status_code == 200
    assert len(queue.json()) >= 1
