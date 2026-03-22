# Modeling and Training

## Data Generation
`ml/scripts/generate_synthetic_data.py` creates correlated synthetic operational data with realistic imbalance and dependencies:
- backlog and traffic increase delay and SLA breach risks
- low SLA remaining hours increases breach probability
- previous reschedules increase reschedule probability
- customer no-show history increases no-show probability

## Targets
- `risk_delay_label`
- `risk_no_show_label`
- `risk_reschedule_label`
- `risk_sla_breach_label`

## Training
`ml/scripts/train_models.py` trains one model per target and stores metrics/artifacts.

Primary model:
- XGBoost classifier

Fallback:
- sklearn GradientBoosting classifier (if xgboost is unavailable)

## Artifact Outputs
- `ml/models/*_model.pkl`
- `ml/models/feature_columns.json`
- `ml/reports/model_metrics.json`
- `ml/reports/feature_importance.json`
- `ml/artifacts/registry.json`

## Inference in Backend
`backend/app/services/model_service.py` loads artifacts and provides deterministic scoring + factor contribution approximation used by explainability and policy layers.
