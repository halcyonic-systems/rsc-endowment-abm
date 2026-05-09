"""
Tests for RSC Endowment ABM mechanism correctness.

Validates the model matches the actual mechanism:
Yield = RSC Emissions * (Your RSC / Total RSC on Platform)
No multipliers, no burn-from-principal, by default.
"""

import pytest
from src.model import EndowmentModel
from src.scenarios import build_scenario


class TestNoBurnFromPrincipal:

    def test_deploy_preserves_principal(self):
        m = EndowmentModel(num_holders=10, num_proposals=30, seed=42)
        m.run_steps(5)

        holder = next(
            (h for h in m.holders if h.active and h.credits > 0), None
        )
        assert holder is not None, "No holder with credits after 5 steps"

        rsc_before = holder.rsc_held
        proposals = [p for p in m.proposals if p.status == "open"]
        assert len(proposals) > 0

        holder.deploy_credits(proposals[0], holder.credits * 0.5)
        assert holder.rsc_held == rsc_before

    def test_burn_on_deploy_reduces_principal(self):
        m = EndowmentModel(
            num_holders=10, num_proposals=30,
            burn_rate=0.02, burn_on_deploy=True, seed=42,
        )
        m.run_steps(5)

        holder = next(
            (h for h in m.holders if h.active and h.credits > 0), None
        )
        assert holder is not None

        rsc_before = holder.rsc_held
        proposals = [p for p in m.proposals if p.status == "open"]
        assert len(proposals) > 0
        holder.deploy_credits(proposals[0], holder.credits * 0.5)
        assert holder.rsc_held < rsc_before

    def test_total_burned_stays_zero_default(self):
        m = EndowmentModel(num_holders=50, seed=42)
        m.run_steps(52)
        assert m.total_burned == 0.0


class TestSimpleDilution:

    def test_yield_proportional_to_rsc_share(self):
        m = EndowmentModel(num_holders=2, seed=42)
        m.holders[0].rsc_held = 70_000
        m.holders[1].rsc_held = 30_000
        m.holders[0].credits = 0
        m.holders[1].credits = 0

        m.holders[0]._earn_credits()
        m.holders[1]._earn_credits()

        total_credits = m.holders[0].credits + m.holders[1].credits
        assert total_credits > 0
        share_0 = m.holders[0].credits / total_credits
        assert abs(share_0 - 0.70) < 0.01, f"Expected ~70% share, got {share_0:.1%}"

    def test_30pct_participation_year0_apy(self):
        m = EndowmentModel(
            num_holders=100,
            initial_participation_rate=0.30,
            seed=42,
        )
        apy = m.current_apy()
        assert 0.20 < apy < 0.28, f"APY at 30% participation should be ~23.6%, got {apy:.1%}"

    def test_multipliers_engaged_when_enabled(self):
        m = EndowmentModel(num_holders=2, seed=42, time_weight_enabled=True)
        m.holders[0].rsc_held = 50_000
        m.holders[0].weeks_held = 0
        m.holders[1].rsc_held = 50_000
        m.holders[1].weeks_held = 60
        m.holders[0].credits = 0
        m.holders[1].credits = 0

        m.holders[0]._earn_credits()
        m.holders[1]._earn_credits()

        assert m.holders[1].credits > m.holders[0].credits, (
            "LongTerm holder should earn more when multipliers enabled"
        )


class TestStressScenarios:

    def test_whale_exit_removes_largest_holder(self):
        m = EndowmentModel(num_holders=20, seed=42)
        whale = max(
            (h for h in m.holders if h.active), key=lambda h: h.rsc_held
        )
        m.scenario = build_scenario("whale_exit", trigger_step=5)
        m.run_steps(5)
        assert not whale.active

    def test_foundation_flood_adds_large_holder(self):
        m = EndowmentModel(num_holders=20, seed=42)
        m.scenario = build_scenario("foundation_flood", trigger_step=3)
        m.run_steps(3)

        flood_holders = [h for h in m.holders if h.rsc_held >= 40_000_000]
        assert len(flood_holders) >= 1
        assert flood_holders[0].rsc_held == 50_000_000

    def test_cascade_exit_fires(self):
        m = EndowmentModel(num_holders=50, seed=42)
        m.scenario = build_scenario("cascade_exit", trigger_step=2)
        m.run_steps(2)

        scenario_events = [e for e in m.events if e["type"] == "scenario"]
        assert len(scenario_events) == 1
        assert "CASCADE EXIT" in scenario_events[0]["message"]

    def test_scenario_fires_only_at_trigger_step(self):
        m = EndowmentModel(num_holders=20, seed=42)
        initial_count = len(m.holders)
        m.scenario = build_scenario("foundation_flood", trigger_step=10)

        m.run_steps(5)
        flood_holders = [h for h in m.holders if h.rsc_held >= 40_000_000]
        assert len(flood_holders) == 0, "Scenario should not fire before trigger_step"

        m.run_steps(5)
        flood_holders = [h for h in m.holders if h.rsc_held >= 40_000_000]
        assert len(flood_holders) >= 1


class TestAPIStatus:

    def test_status_endpoint_fields(self):
        import server as srv
        client = srv.app.test_client()

        client.post("/api/init", json={"num_holders": 20, "seed": 42})
        resp = client.get("/api/status")
        data = resp.get_json()

        for field in ["apy", "participation_rate", "total_staked",
                       "active_holders", "health_color", "step", "year"]:
            assert field in data, f"Missing field: {field}"
        assert data["health_color"] in ("green", "amber", "red")

    def test_scenarios_endpoint(self):
        import server as srv
        client = srv.app.test_client()

        resp = client.get("/api/scenarios")
        data = resp.get_json()

        assert len(data) == 4
        ids = {s["id"] for s in data}
        assert ids == {"whale_exit", "foundation_flood", "cascade_exit", "mint_event"}

    def test_init_with_scenario(self):
        import server as srv
        client = srv.app.test_client()

        resp = client.post("/api/init", json={
            "num_holders": 20,
            "seed": 42,
            "scenario": {"name": "whale_exit", "trigger_step": 5},
        })
        data = resp.get_json()
        assert data["model"]["scenario"]["name"] == "Whale Exit"
        assert data["model"]["scenario"]["trigger_step"] == 5
