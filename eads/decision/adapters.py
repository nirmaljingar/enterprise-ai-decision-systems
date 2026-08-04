import re
from abc import ABC, abstractmethod
from typing import Any

from ..core.types import DecisionRequest


class SolverBackend(ABC):
    """Abstract optimization solver adapter for decision candidates."""

    @abstractmethod
    def optimize(self, request: DecisionRequest, plan: Any | None = None) -> dict[str, Any]:
        """Return a dictionary of optimization results for the given request."""
        ...


class SciPySolver(SolverBackend):
    """Reference linear programming solver using scipy (requires the 'solvers' extra)."""

    def optimize(self, request: DecisionRequest, plan: Any | None = None) -> dict[str, Any]:
        try:
            from scipy.optimize import linprog
        except ImportError as exc:
            raise ImportError(
                "SciPy is not installed. Run `pip install -e '.[solvers]'`."
            ) from exc
        max_qty = request.policy_snapshot.get("max_order_quantity", 1000)
        # Maximize order quantity: minimize -x subject to 0 <= x <= max_qty.
        result = linprog(c=[-1.0], bounds=[(0, max_qty)], method="highs")
        if not result.success:
            return {"solver_status": "failed", "message": result.message}
        return {
            "order_quantity": int(round(result.x[0])),  # noqa: RUF046
            "max_order_quantity": max_qty,
            "solver_status": "success",
            "solver": "scipy.linprog",
        }


class PulpSolver(SolverBackend):
    """Reference mixed-integer LP solver using PuLP (requires the 'solvers' extra)."""

    def optimize(self, request: DecisionRequest, plan: Any | None = None) -> dict[str, Any]:
        try:
            import pulp
        except ImportError as exc:
            raise ImportError(
                "PuLP is not installed. Run `pip install -e '.[solvers]'`."
            ) from exc
        max_qty = request.policy_snapshot.get("max_order_quantity", 1000)
        problem = pulp.LpProblem("eads_order_quantity", pulp.LpMaximize)
        x = pulp.LpVariable("order_quantity", lowBound=0, upBound=max_qty, cat="Integer")
        problem += x
        problem.solve(pulp.PULP_CBC_CMD(msg=False))
        status = pulp.LpStatus[problem.status]
        return {
            "order_quantity": int(round(pulp.value(x))) if status == "Optimal" else 0,  # noqa: RUF046
            "max_order_quantity": max_qty,
            "solver_status": status.lower(),
            "solver": "pulp",
        }


class OrtoolsSolver(SolverBackend):
    """Reference constraint solver using OR-Tools (requires the 'solvers' extra)."""

    def optimize(self, request: DecisionRequest, plan: Any | None = None) -> dict[str, Any]:
        try:
            from ortools.linear_solver import pywraplp
        except ImportError as exc:
            raise ImportError(
                "OR-Tools is not installed. Run `pip install -e '.[solvers]'`."
            ) from exc
        max_qty = request.policy_snapshot.get("max_order_quantity", 1000)
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver:
            return {"solver_status": "failed", "message": "solver not available"}
        x = solver.IntVar(0, max_qty, "order_quantity")
        solver.Maximize(x)
        status = solver.Solve()
        status_map = {
            pywraplp.Solver.OPTIMAL: "optimal",
            pywraplp.Solver.FEASIBLE: "feasible",
        }
        if status in status_map:
            return {
                "order_quantity": int(x.solution_value()),
                "max_order_quantity": max_qty,
                "solver_status": status_map[status],
                "solver": "ortools",
            }
        return {"solver_status": "failed", "status_code": status}


class ForecasterBackend(ABC):
    """Abstract forecaster adapter for demand and supply estimates."""

    @abstractmethod
    def forecast(self, request: DecisionRequest, plan: Any | None = None) -> dict[str, Any]:
        """Return a dictionary of forecasted values for the given request."""
        ...


class NaiveForecaster(ForecasterBackend):
    """Reference last-value forecaster that does not require extra packages."""

    def forecast(self, request: DecisionRequest, plan: Any | None = None) -> dict[str, Any]:
        values: list[int] = []
        for signal in request.signals:
            # Extract simple integers from the signal content as a crude surrogate.
            values.extend(int(n) for n in re.findall(r"\d+", signal.content))
        last = values[-1] if values else 0
        return {
            "predicted_demand": last,
            "samples": len(values),
            "method": "naive_last_value",
        }


class SKTimeForecaster(ForecasterBackend):
    """Reference time-series forecaster using sktime (requires the 'forecasters' extra)."""

    def forecast(self, request: DecisionRequest, plan: Any | None = None) -> dict[str, Any]:
        try:
            import pandas as pd
            from sktime.forecasting.base import ForecastingHorizon
            from sktime.forecasting.naive import NaiveForecaster
        except ImportError as exc:
            raise ImportError(
                "sktime/pandas are not installed. Run `pip install -e '.[forecasters]'`."
            ) from exc
        values: list[int] = []
        for signal in request.signals:
            values.extend(int(n) for n in re.findall(r"\d+", signal.content))
        if not values:
            return {"predicted_demand": 0, "method": "sktime_naive", "samples": 0}
        series = pd.Series(values, index=pd.RangeIndex(start=0, stop=len(values)))
        forecaster = NaiveForecaster(strategy="last")
        forecaster.fit(series)
        fh = ForecastingHorizon([1], is_relative=True)
        prediction = forecaster.predict(fh)
        return {
            "predicted_demand": int(round(prediction.iloc[0])),  # noqa: RUF046
            "samples": len(values),
            "method": "sktime_naive",
        }


__all__ = [
    "ForecasterBackend",
    "NaiveForecaster",
    "OrtoolsSolver",
    "PulpSolver",
    "SKTimeForecaster",
    "SciPySolver",
    "SolverBackend",
]
