"""
Stress scenarios for RSC Endowment ABM.

Injectable perturbations that fire at a specific simulation step.
Designed for leadership conversations about endowment risk.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class StressScenario:
    name: str
    description: str
    trigger_step: int
    apply: Callable


def whale_exit(model):
    active = [h for h in model.holders if h.active]
    if not active:
        return
    whale = max(active, key=lambda h: h.rsc_held)
    whale.active = False
    model.log_event(
        "scenario",
        f"WHALE EXIT: H{whale.unique_id} ({whale.archetype}, "
        f"{whale.rsc_held:,.0f} RSC) exited"
    )


def foundation_flood(model):
    from .agents import EndowmentHolder
    rsc_amount = 50_000_000
    holder = EndowmentHolder(
        model,
        archetype="institution",
        rsc_held=rsc_amount,
        mission_alignment=0.9,
        engagement=0.5,
        price_sensitivity=0.05,
        hold_horizon=1.0,
    )
    model.holders.append(holder)
    model.log_event(
        "scenario",
        f"FOUNDATION FLOOD: New institution holder with "
        f"{rsc_amount:,.0f} RSC deposited"
    )


def cascade_exit(model):
    current_apy = model.current_apy()
    exited = []
    for h in model.holders:
        if h.active and h.archetype == "yield_seeker":
            if current_apy < h.yield_threshold:
                h.active = False
                exited.append(h)
    model.log_event(
        "scenario",
        f"CASCADE EXIT: {len(exited)} yield seekers exited "
        f"(APY {current_apy:.1%} below threshold)"
    )


SCENARIOS = {
    "whale_exit": {
        "name": "Whale Exit",
        "description": "The largest holder exits the endowment completely.",
        "factory": whale_exit,
    },
    "foundation_flood": {
        "name": "Foundation Flood",
        "description": "RH Foundation deposits 50M RSC, diluting existing holders' yield.",
        "factory": foundation_flood,
    },
    "cascade_exit": {
        "name": "Cascade Exit",
        "description": "All yield seekers below their APY threshold exit simultaneously.",
        "factory": cascade_exit,
    },
}


def build_scenario(scenario_id: str, trigger_step: int) -> StressScenario:
    if scenario_id not in SCENARIOS:
        raise ValueError(
            f"Unknown scenario: {scenario_id}. "
            f"Available: {list(SCENARIOS.keys())}"
        )
    info = SCENARIOS[scenario_id]
    return StressScenario(
        name=info["name"],
        description=info["description"],
        trigger_step=trigger_step,
        apply=info["factory"],
    )


def list_scenarios() -> list:
    return [
        {"id": k, "name": v["name"], "description": v["description"]}
        for k, v in SCENARIOS.items()
    ]
