"""
RSC Decentralized Endowment ABM

Real mechanism: RSC in RH account auto-earns yield (passive).
Yield = (your RSC / total RH RSC) x annual_emissions
Emissions decay: E(t) = 9,500,000 / 2^(t/64)
"""

from .model import EndowmentModel
from .agents import EndowmentHolder, EndowmentStaker, EndowmentProposal
from .constants import (
    TIME_WEIGHT_MULTIPLIERS, EMISSION_PARAMS, DEFAULT_PARAMS,
    ARCHETYPES, DEFAULT_ARCHETYPE_MIX,
    get_time_weight_multiplier, list_multipliers,
    get_archetype, list_archetypes,
)
from .scenarios import list_scenarios, build_scenario, SCENARIOS

__all__ = [
    "EndowmentModel",
    "EndowmentHolder",
    "EndowmentStaker",
    "EndowmentProposal",
    "TIME_WEIGHT_MULTIPLIERS",
    "EMISSION_PARAMS",
    "DEFAULT_PARAMS",
    "ARCHETYPES",
    "DEFAULT_ARCHETYPE_MIX",
    "get_time_weight_multiplier",
    "list_multipliers",
    "get_archetype",
    "list_archetypes",
    "list_scenarios",
    "build_scenario",
    "SCENARIOS",
]
