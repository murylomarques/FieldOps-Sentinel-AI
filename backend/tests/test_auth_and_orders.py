def _login(client, email: str = "manager@fieldops.ai", password: str = "manager123") -> str:
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_login_and_me(client):
    token = _login(client)
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "manager"


def test_orders_risk_recommendation_and_timeline(client):
    token = _login(client, "dispatcher@fieldops.ai", "dispatcher123")

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
        "technician_id": "TECH-012",
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

    create = client.post("/api/v1/orders", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert create.status_code == 200

    listed = client.get("/api/v1/orders?page=1&page_size=20", headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert len(listed.json()) >= 1

    risk = client.get("/api/v1/orders/ORD-TEST-0001/risk", headers={"Authorization": f"Bearer {token}"})
    assert risk.status_code == 200
    assert 0 <= risk.json()["overall_risk_score"] <= 1

    recommend = client.post("/api/v1/orders/ORD-TEST-0001/recommend", headers={"Authorization": f"Bearer {token}"})
    assert recommend.status_code == 200

    timeline = client.get("/api/v1/orders/ORD-TEST-0001/timeline", headers={"Authorization": f"Bearer {token}"})
    assert timeline.status_code == 200
    assert len(timeline.json()["events"]) >= 1


def test_approval_rejection_simulation_and_replay(client):
    manager_token = _login(client, "manager@fieldops.ai", "manager123")

    queue = client.get("/api/v1/recommendations/queue", headers={"Authorization": f"Bearer {manager_token}"})
    assert queue.status_code == 200
    assert queue.json()

    first = queue.json()[0]
    approve = client.post(
        f"/api/v1/recommendations/{first['id']}/approve",
        json={"justification": "Approved during test"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert approve.status_code == 200

    if len(queue.json()) > 1:
        second = queue.json()[1]
        reject = client.post(
            f"/api/v1/recommendations/{second['id']}/reject",
            json={"justification": "Rejected due to travel"},
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert reject.status_code == 200

    simulation = client.post(
        "/api/v1/simulations/what-if",
        json={
            "traffic_multiplier": 1.3,
            "weather_multiplier": 1.2,
            "region_backlog_delta": 10,
            "technician_unavailable_ids": ["TECH-001"],
            "sla_buffer_minutes_delta": -30,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert simulation.status_code == 200
    assert "projected_sla_breaches" in simulation.json()

    orders = client.get("/api/v1/orders?page=1&page_size=1", headers={"Authorization": f"Bearer {manager_token}"})
    assert orders.status_code == 200
    order_id = orders.json()[0]["order_id"]

    replay = client.get(f"/api/v1/replay/orders/{order_id}", headers={"Authorization": f"Bearer {manager_token}"})
    assert replay.status_code == 200
    assert "timeline" in replay.json()
