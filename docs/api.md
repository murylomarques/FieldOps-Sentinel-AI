# API Reference

Base path: `/api/v1`

## Auth
- `POST /auth/login`
- `GET /auth/me`

## Orders
- `GET /orders` (supports pagination and filters)
- `GET /orders/{order_id}`
- `POST /orders`
- `POST /orders/bulk-seed`
- `GET /orders/{order_id}/timeline`
- `POST /orders/{order_id}/score`
- `GET /orders/{order_id}/risk`
- `POST /orders/{order_id}/recommend`

## Recommendations
- `GET /recommendations`
- `GET /recommendations/queue`
- `GET /recommendations/{recommendation_id}`
- `GET /recommendations/decision/{decision_id}`
- `POST /recommendations/{recommendation_id}/approve`
- `POST /recommendations/{recommendation_id}/reject`
- `POST /recommendations/approve` (legacy compatibility)

## Simulation
- `POST /simulations/what-if`

Supported payload fields:
- `traffic_multiplier`
- `weather_multiplier`
- `region_backlog_delta`
- `technician_unavailable_ids`
- `order_priority_override`
- `sla_buffer_minutes_delta`

## Dashboard
- `GET /dashboard/summary`
- `GET /dashboard/critical-orders`
- `GET /dashboard/approval-metrics`
- `GET /dashboard/model-monitoring`
- `GET /dashboard/loss-prevention`
- `GET /dashboard/risk-by-region`
- `GET /dashboard/executive-insights`
- `GET /dashboard/demo-status`

## Replay
- `GET /replay/orders/{order_id}`

## System
- `GET /health`
- `GET /metrics`
