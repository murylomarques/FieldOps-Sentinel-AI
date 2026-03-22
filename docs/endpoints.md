# API Endpoints

Base URL: `/api/v1`

## Auth
- `POST /auth/login`
  - body: `{ email, password }`
  - response: `{ access_token, token_type }`
- `GET /auth/me`
  - header: `Authorization: Bearer <token>`

## Orders
- `POST /orders`
  - Creates/updates service order and triggers full agentic pipeline.
- `GET /orders?city=&region=&priority=&q=`
  - Filtered listing for operations table.
- `GET /orders/{order_id}`
  - Order detail for case investigation.

## Recommendations & Human Approval
- `GET /recommendations/queue`
  - Pending recommendations requiring operator decision.
- `GET /recommendations/{decision_id}`
  - Recommendation details.
- `POST /recommendations/approve`
  - body: `{ decision_id, approve, justification }`
- `GET /recommendations/decision/{decision_id}`
  - Full AI + human decision trace.

## Dashboard & Executive Insights
- `GET /dashboard/kpis`
- `GET /dashboard/risk-by-region`
- `GET /dashboard/executive-insights`

## Monitoring
- `GET /monitoring/models`

## Health
- `GET /health`

## Request Tracking
- All responses include `x-request-id` header.
- Decision workflows are linked via `decision_id` and persisted in `audit_logs`.
