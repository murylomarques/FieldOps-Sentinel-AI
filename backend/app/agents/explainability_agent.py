
class ExplainabilityAgent:
    def run(self, payload: dict, risk: dict, recommendation: dict, policy: dict) -> dict:
        top_factors = ", ".join([f["feature"] for f in risk["factors"][:3]])

        business = (
            f"Order {payload['order_id']} was flagged due to a combined risk score of {risk['overall_risk']:.2f}. "
            f"Key drivers are {top_factors}. The recommended action is {recommendation['action_type']} "
            f"with expected impact score {recommendation['impact_score']:.2f}."
        )
        ops = (
            f"Delay={risk['delay_risk']:.2f}, NoShow={risk['no_show_risk']:.2f}, Reschedule={risk['reschedule_risk']:.2f}. "
            f"Suggested technician {recommendation['recommended_technician_id']} in {recommendation['recommended_region']} "
            f"window {recommendation['recommended_window']}. Policy flags: {', '.join(policy['flags']) or 'none'}."
        )
        return {
            "business_summary": business,
            "operational_summary": ops,
        }
