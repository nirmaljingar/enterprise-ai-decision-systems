#!/usr/bin/env python3
"""Validate optional solver and forecaster extras if they are installed."""

import importlib.util

from eads.core.types import DecisionRequest, Signal
from eads.decision.adapters import (
    NaiveForecaster,
    OrtoolsSolver,
    PulpSolver,
    SciPySolver,
    SKTimeForecaster,
)


def _request(max_order: int = 1000) -> DecisionRequest:
    return DecisionRequest(
        request_id="x-1",
        goal="order",
        signals=[],
        policy_snapshot={"max_order_quantity": max_order},
    )


def _check_solver(name: str, cls) -> None:
    if not importlib.util.find_spec(name):
        print(f"[{cls.__name__}] {name} not installed; skipping.")
        return
    try:
        result = cls().optimize(_request(250))
        print(f"[{cls.__name__}] {result}")
    except Exception as exc:
        print(f"[{cls.__name__}] error: {exc}")


def _check_forecaster(name: str, cls) -> None:
    if not importlib.util.find_spec(name):
        print(f"[{cls.__name__}] {name} not installed; skipping.")
        return
    request = DecisionRequest(
        request_id="x-2",
        goal="forecast",
        signals=[
            Signal(id="s1", source="test", content="100"),
            Signal(id="s2", source="test", content="120"),
        ],
    )
    try:
        result = cls().forecast(request)
        print(f"[{cls.__name__}] {result}")
    except Exception as exc:
        print(f"[{cls.__name__}] error: {exc}")


def main() -> None:
    print("Validating optional solver/forecaster extras...")
    _check_solver("scipy", SciPySolver)
    _check_solver("pulp", PulpSolver)
    _check_solver("ortools", OrtoolsSolver)
    _check_forecaster("sktime", SKTimeForecaster)
    # NaiveForecaster has no extra dependency.
    try:
        request = DecisionRequest(
            request_id="x-3",
            goal="forecast",
            signals=[Signal(id="s1", source="test", content="Demand is 300")],
        )
        print(f"[NaiveForecaster] {NaiveForecaster().forecast(request)}")
    except Exception as exc:
        print(f"[NaiveForecaster] error: {exc}")


if __name__ == "__main__":
    main()
