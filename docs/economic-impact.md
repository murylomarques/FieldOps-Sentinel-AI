# Economic Impact Model

The intervention engine uses transparent deterministic formulas to estimate operational loss.

## Inputs
From order context and risk scoring:
- `projected_sla_penalty`
- `order_value`
- `delay_risk`
- `no_show_risk`
- `reschedule_risk`
- `sla_breach_risk`
- `previous_reschedules`
- `customer_history_no_show`
- scenario `travel_delta_minutes`
- scenario `risk_reduction`

## Formulas
- `projected_sla_penalty = projected_sla_penalty_base * sla_breach_risk`
- `projected_repeat_visit_loss = order_value * 0.35 * reschedule_risk * (1 + previous_reschedules * 0.08)`
- `projected_no_show_loss = order_value * 0.22 * no_show_risk * (1 + customer_history_no_show * 0.12)`
- `projected_delay_loss = order_value * 0.18 * delay_risk`

Then:
- `projected_cost_of_inaction = sum(loss components)`
- `projected_cost_of_action = max(15, travel_delta_minutes * 1.8 + order_value * 0.045)`
- `projected_total_loss_avoided = max(0, projected_cost_of_inaction * risk_reduction - projected_cost_of_action)`

## Why this is useful
This provides a stable and explainable baseline for:
- scenario ranking
- intervention prioritization
- executive communication of expected operational value
