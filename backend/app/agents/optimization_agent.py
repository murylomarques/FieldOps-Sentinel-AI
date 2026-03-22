from __future__ import annotations


class OptimizationAgent:
    def __init__(self) -> None:
        try:
            from ortools.sat.python import cp_model  # type: ignore

            self.cp_model = cp_model
        except Exception:
            self.cp_model = None

    def _heuristic_pick(self, scenarios: list[dict]) -> dict:
        feasible = [s for s in scenarios if s["feasibility_status"] == "feasible"]
        if not feasible:
            return scenarios[-1]

        for scenario in feasible:
            avoided = float(scenario.get("projected_loss_avoided", 0.0))
            action = float(scenario.get("projected_cost_of_action", 0.0))
            travel = float(scenario.get("projected_travel_delta_minutes", 0.0))
            scenario["optimizer_score"] = round(avoided - action - (0.8 * travel), 4)
        return sorted(feasible, key=lambda x: x.get("optimizer_score", -10e9), reverse=True)[0]

    def run(self, scenarios: list[dict], max_travel_delta: float = 45.0) -> dict:
        if not scenarios:
            raise ValueError("No scenarios provided for optimization")

        filtered = [
            s for s in scenarios if s["feasibility_status"] == "feasible" and s.get("projected_travel_delta_minutes", 0.0) <= max_travel_delta
        ]
        if not filtered:
            return self._heuristic_pick(scenarios)

        if self.cp_model is None:
            return self._heuristic_pick(filtered)

        cp_model = self.cp_model
        model = cp_model.CpModel()

        choose = [model.NewBoolVar(f"choose_{idx}") for idx, _ in enumerate(filtered)]
        model.Add(sum(choose) == 1)

        scaled_scores: list[int] = []
        for scenario in filtered:
            score = float(scenario.get("projected_loss_avoided", 0.0)) - float(scenario.get("projected_cost_of_action", 0.0))
            scaled_scores.append(int(round(score * 100)))

        model.Maximize(sum(var * score for var, score in zip(choose, scaled_scores, strict=True)))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 0.15
        solver.parameters.random_seed = 42

        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return self._heuristic_pick(filtered)

        for idx, var in enumerate(choose):
            if solver.BooleanValue(var):
                selected = filtered[idx]
                selected["optimizer_score"] = round(scaled_scores[idx] / 100, 4)
                selected["optimizer_explanation"] = "CP-SAT selected the best feasible intervention under one-choice constraints."
                return selected

        return self._heuristic_pick(filtered)
