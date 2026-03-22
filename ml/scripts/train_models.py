import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

DATA_PATH = Path("ml/data/synthetic_orders.csv")
MODEL_DIR = Path("ml/models")
REPORT_DIR = Path("ml/reports")

TARGETS = {
    "delay": "risk_delay_label",
    "noshow": "risk_no_show_label",
    "reschedule": "risk_reschedule_label",
}

FEATURES = [
    "region",
    "service_type",
    "priority",
    "technician_load",
    "distance_km",
    "previous_reschedules",
    "customer_history_no_show",
    "rain_level",
    "traffic_level",
    "backlog_region",
    "sla_hours_remaining",
    "estimated_duration_minutes",
]



def compute_metrics(y_true, y_pred, y_proba):
    result = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    try:
        result["roc_auc"] = float(roc_auc_score(y_true, y_proba))
    except ValueError:
        result["roc_auc"] = 0.0
    return result


def build_pipeline():
    numeric_features = [
        "technician_load",
        "distance_km",
        "previous_reschedules",
        "customer_history_no_show",
        "rain_level",
        "traffic_level",
        "backlog_region",
        "sla_hours_remaining",
        "estimated_duration_minutes",
    ]
    categorical_features = ["region", "service_type", "priority"]

    preprocess = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    model = XGBClassifier(
        n_estimators=180,
        max_depth=5,
        learning_rate=0.07,
        subsample=0.95,
        colsample_bytree=0.95,
        eval_metric="logloss",
        random_state=42,
    )

    pipeline = Pipeline(steps=[("preprocess", preprocess), ("model", model)])
    return pipeline


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}. Run generate_synthetic_data.py first.")

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]

    report = {}
    for model_name, target_col in TARGETS.items():
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        pipeline = build_pipeline()
        pipeline.fit(X_train, y_train)

        pred = pipeline.predict(X_test)
        proba = pipeline.predict_proba(X_test)[:, 1]
        metrics = compute_metrics(y_test, pred, proba)
        report[model_name] = metrics

        model_path = MODEL_DIR / f"{model_name}_model.pkl"
        joblib.dump(pipeline, model_path)

    # Backend fallback-compatible feature list
    feature_columns = [
        "technician_load",
        "distance_km",
        "previous_reschedules",
        "customer_history_no_show",
        "rain_level",
        "traffic_level",
        "backlog_region",
        "sla_hours_remaining",
        "estimated_duration_minutes",
        "priority_encoded",
        "service_type_encoded",
        "region_encoded",
    ]
    (MODEL_DIR / "feature_columns.json").write_text(json.dumps(feature_columns, indent=2), encoding="utf-8")
    (REPORT_DIR / "model_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Training complete. Metrics:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
