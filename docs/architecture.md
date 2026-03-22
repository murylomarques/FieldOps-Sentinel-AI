# Architecture Notes

## Agent Flow
1. Intake Agent normalizes and validates incoming service order.
2. Risk Scoring Agent predicts delay / no-show / reschedule risks.
3. Dispatch Recommendation Agent proposes priority and resource reassignment.
4. Policy Guard Agent enforces hard business constraints.
5. Explainability Agent writes business and operational rationales.
6. Executive Report Agent aggregates strategic insights.

## Governance Model
- Every AI recommendation receives a `decision_id`.
- High-impact actions remain `pending_human_approval`.
- Approve/reject events are audited with actor, reason, and timestamp.

## Observability
- Structured logs at request level.
- Rate limiting and request correlation via `request_id`.
- Monitoring endpoint reports latency, drift simulation, and override rate.
