class ExplainabilityAgent:
    def run(self, payload: dict, risk: dict, recommendation: dict, policy: dict) -> dict:
        top_factors = ", ".join([f["feature"].replace("_", " ") for f in risk["factors"][:3]])

        reason_summary = (
            f"High influence from {top_factors} drove the consolidated risk score to {risk['overall_risk']:.2f}."
        )
        operational_summary = (
            f"Selected action {recommendation['action_type']} with technician {recommendation['recommended_technician_id']} "
            f"for region {recommendation['recommended_region']} in window {recommendation['recommended_window']}. "
            f"Projected risk reduction: {recommendation.get('projected_risk_reduction', 0.0):.2f}."
        )
        executive_summary = (
            f"The intervention is expected to avoid approximately {recommendation.get('projected_loss_avoided', 0.0):.2f} in "
            f"projected operational losses while policy flags remain {', '.join(policy['flags']) or 'none'}."
        )
        return {
            "reason_summary": reason_summary,
            "operational_summary": operational_summary,
            "executive_summary": executive_summary,
        }
