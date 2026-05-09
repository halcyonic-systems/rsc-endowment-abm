"""
Flask server for RSC Decentralized Endowment ABM

Real mechanism: RSC in RH account auto-earns yield (passive, no staking action).
Primary question: What participation_rate does the market equilibrate to?
"""

import os
from functools import wraps

from flask import Flask, jsonify, request, render_template, Response

from src import (
    EndowmentModel,
    TIME_WEIGHT_MULTIPLIERS,
    EMISSION_PARAMS,
    DEFAULT_PARAMS,
    ARCHETYPES,
    DEFAULT_ARCHETYPE_MIX,
    list_multipliers,
    list_archetypes,
    list_scenarios,
)
from src.data import take_snapshot, get_latest_snapshot

app = Flask(__name__)

# ============================================
# Auth Gate (password-protect until ready)
# ============================================

AUTH_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")

def check_auth(password):
    return password == AUTH_PASSWORD

def authenticate():
    return Response(
        "Access restricted. This observatory is not yet public.\n",
        401,
        {"WWW-Authenticate": 'Basic realm="RSC Endowment Observatory"'},
    )

@app.before_request
def require_auth():
    if not AUTH_PASSWORD:
        return
    auth = request.authorization
    if not auth or not check_auth(auth.password):
        return authenticate()


# Global model instance
model = None


def get_model():
    """Get or create the global model instance."""
    global model
    if model is None:
        model = EndowmentModel()
    return model


def reset_model(**kwargs):
    """Reset the model with new parameters."""
    global model
    model = EndowmentModel(**kwargs)
    return model


# ============================================
# API Endpoints
# ============================================

@app.route("/")
def index():
    """Interactive dashboard (v3)."""
    return render_template("index.html")


@app.route("/v4")
def v4():
    """v4 Observatory prototype."""
    return render_template("v4-kpi-prototype.html")


@app.route("/api")
def api_info():
    """API info."""
    return jsonify({
        "name": "RSC Decentralized Endowment ABM",
        "description": "RSC in RH account auto-earns yield. Yield = (your RSC / total RSC) x emissions.",
        "primary_question": "What participation rate does the market equilibrate to?",
        "endpoints": {
            "/api/init": "POST - Initialize model with parameters",
            "/api/step": "POST - Advance simulation by 1 step (1 week)",
            "/api/run": "POST - Run N steps",
            "/api/state": "GET - Get current model state",
            "/api/metrics": "GET - Get computed metrics",
            "/api/holders": "GET - List all holders",
            "/api/proposals": "GET - List all proposals",
            "/api/history": "GET - Get time series data",
            "/api/events": "GET - Get event log",
            "/api/multipliers": "GET - List time-weight multipliers",
            "/api/archetypes": "GET - List behavioral archetypes",
            "/api/participation": "GET - Participation rate data + reference scenarios",
            "/api/status": "GET - Compact KPI summary for v4 dashboard",
            "/api/scenarios": "GET - List available stress scenarios",
        },
        "status": "ready",
    })


@app.route("/api/init", methods=["POST"])
def api_init():
    """Initialize model with parameters."""
    data = request.get_json() or {}

    params = {
        "num_holders": data.get("num_holders") or data.get("num_stakers"),
        "num_proposals": data.get("num_proposals"),
        "burn_rate": data.get("burn_rate"),
        "success_rate": data.get("success_rate"),
        "funding_target_min": data.get("funding_target_min"),
        "funding_target_max": data.get("funding_target_max"),
        "deploy_probability": data.get("deploy_probability"),
        "archetype_mix": data.get("archetype_mix"),
        "yield_threshold_mean": data.get("yield_threshold_mean"),
        "initial_participation_rate": data.get("initial_participation_rate"),
        "seed": data.get("seed"),
        # Design Lab params
        "burn_on_deploy": data.get("burn_on_deploy"),
        "time_weight_enabled": data.get("time_weight_enabled"),
        "credit_expiry_enabled": data.get("credit_expiry_enabled"),
        "credit_expiry_weeks": data.get("credit_expiry_weeks"),
        "failure_mode": data.get("failure_mode"),
        "scenario": data.get("scenario"),
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    m = reset_model(**params)
    return jsonify({
        "status": "initialized",
        "model": m.to_dict(),
    })


@app.route("/api/step", methods=["POST"])
def api_step():
    """Advance model by one step (1 week)."""
    m = get_model()
    m.step()
    return jsonify({
        "model": m.to_dict(),
        "events": m.get_events(10),
    })


@app.route("/api/run", methods=["POST"])
def api_run():
    """Run model for N steps."""
    data = request.get_json() or {}
    n = data.get("steps", 10)

    m = get_model()
    m.run_steps(n)

    return jsonify({
        "model": m.to_dict(),
        "steps_run": n,
    })


@app.route("/api/state")
def api_state():
    """Get current model state."""
    m = get_model()
    return jsonify({
        "model": m.to_dict(),
        "events": m.get_events(20),
    })


@app.route("/api/metrics")
def api_metrics():
    """Get computed metrics."""
    m = get_model()
    return jsonify(m.get_metrics())


@app.route("/api/holders")
def api_holders():
    """List all holders."""
    m = get_model()
    return jsonify(m.get_holders())


@app.route("/api/stakers")
def api_stakers():
    """Legacy alias for /api/holders."""
    m = get_model()
    return jsonify(m.get_holders())


@app.route("/api/holders/<int:holder_id>")
def api_holder_detail(holder_id: int):
    """Get single holder details."""
    m = get_model()
    for holder in m.holders:
        if holder.unique_id == holder_id:
            return jsonify(holder.to_dict())
    return jsonify({"error": "Holder not found"}), 404


@app.route("/api/proposals")
def api_proposals():
    """List all proposals."""
    m = get_model()
    return jsonify(m.get_proposals())


@app.route("/api/proposals/<int:proposal_id>")
def api_proposal_detail(proposal_id: int):
    """Get single proposal details."""
    m = get_model()
    for proposal in m.proposals:
        if proposal.unique_id == proposal_id:
            return jsonify(proposal.to_dict())
    return jsonify({"error": "Proposal not found"}), 404


@app.route("/api/history")
def api_history():
    """Get time series data."""
    m = get_model()
    return jsonify(m.get_history())


@app.route("/api/events")
def api_events():
    """Get event log."""
    m = get_model()
    limit = request.args.get("limit", 50, type=int)
    return jsonify(m.get_events(limit))


@app.route("/api/multipliers")
def api_multipliers():
    """List time-weight multipliers."""
    return jsonify(list_multipliers())


@app.route("/api/tiers")
def api_tiers():
    """Legacy alias for /api/multipliers."""
    return jsonify(list_multipliers())


@app.route("/api/archetypes")
def api_archetypes():
    """List behavioral archetypes and current distribution."""
    m = get_model()
    return jsonify({
        "archetypes": list_archetypes(),
        "default_mix": DEFAULT_ARCHETYPE_MIX,
        "current_distribution": m.get_archetype_distribution(),
        "current_metrics": m.get_archetype_metrics(),
    })


@app.route("/api/participation")
def api_participation():
    """Participation rate data with reference scenarios from CSV model."""
    m = get_model()
    return jsonify(m.get_participation_data())


@app.route("/api/defaults")
def api_defaults():
    """Get default parameter values."""
    return jsonify({
        **DEFAULT_PARAMS,
        "emission_params": EMISSION_PARAMS,
    })


@app.route("/api/status")
def api_status():
    """Compact KPI summary for v4 dashboard."""
    m = get_model()
    active = len([h for h in m.holders if h.active])
    apy = m.current_apy()

    if apy > 0.05:
        health_color = "green"
    elif apy > 0.02:
        health_color = "amber"
    else:
        health_color = "red"

    return jsonify({
        "apy": round(apy, 4),
        "participation_rate": round(m.participation_rate, 4),
        "total_staked": round(m.total_rsc_held, 0),
        "active_holders": active,
        "total_holders": len(m.holders),
        "health_color": health_color,
        "step": m.step_count,
        "year": round(m.step_count / 52, 2),
        "weekly_emission": round(m.weekly_emission(), 2),
        "scenario_active": m.scenario.name if m.scenario else None,
    })


@app.route("/api/scenarios")
def api_scenarios():
    """List available stress scenarios."""
    return jsonify(list_scenarios())


@app.route("/api/forecast", methods=["POST"])
def api_forecast():
    """Forecast mode: init model from chain state, run N steps forward."""
    global model
    data = request.get_json() or {}
    steps = data.get("steps", 26)
    scenario = data.get("scenario")

    try:
        snapshot = take_snapshot()
        model = EndowmentModel.from_chain_data(
            snapshot,
            num_synthetic=data.get("num_synthetic", 50),
            scenario=scenario,
            seed=data.get("seed", 42),
        )

        anchored = sum(1 for h in model.holders if getattr(h, 'anchored', False))
        pre_apy = model.current_apy()

        model.run_steps(steps)

        return jsonify({
            "status": "ok",
            "mode": "forecast",
            "init": {
                "pool_rsc": round(snapshot["pool"]["total_rsc"], 0),
                "price_usd": round(snapshot["pool"]["price_usd"], 6),
                "anchored_holders": anchored,
                "synthetic_holders": len(model.holders) - anchored,
                "init_apy": round(pre_apy, 4),
            },
            "result": {
                "steps_run": steps,
                "final_apy": round(model.current_apy(), 4),
                "final_pool": round(model.total_rsc_held, 0),
                "active_holders": len([h for h in model.holders if h.active]),
                "participation_rate": round(model.participation_rate, 4),
            },
            "model": model.to_dict(),
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/chain/snapshot", methods=["POST"])
def api_chain_snapshot():
    """Take a fresh chain data snapshot from Dune Sim API."""
    try:
        result = take_snapshot()
        pool = result["pool"]
        return jsonify({
            "status": "ok",
            "pool_rsc": round(pool["total_rsc"], 0),
            "price_usd": round(pool["price_usd"], 6),
            "value_usd": round(pool["total_usd"], 2),
            "chains": pool["chains"],
            "treasuries": len(result["treasuries"]),
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/chain/latest")
def api_chain_latest():
    """Get the most recent chain data snapshot from local store."""
    latest = get_latest_snapshot()
    if not latest["pool"]:
        return jsonify({"status": "no_data", "message": "No snapshots yet. POST /api/chain/snapshot first."})
    return jsonify({
        "status": "ok",
        "pool": latest["pool"],
        "treasury": latest["treasury"],
        "history_points": len(latest["history"]),
    })


@app.route("/api/chain/history")
def api_chain_history():
    """Get pool size history for charting."""
    latest = get_latest_snapshot()
    return jsonify(latest["history"])


@app.route("/api/chain/health")
def api_chain_health():
    """Compute system health indicators from chain data."""
    latest = get_latest_snapshot()
    if not latest["pool"]:
        return jsonify({"status": "no_data"})

    pool_rsc = latest["pool"]["total_rsc"]
    price = latest["pool"].get("price_usd", 0)
    circ = EMISSION_PARAMS["year0_circulating"]
    participation = pool_rsc / circ if circ > 0 else 0
    apy = EMISSION_PARAMS["year0_emission"] / pool_rsc if pool_rsc > 0 else 0

    # Concentration: what % of pool is in the largest treasury?
    treasury_total = sum(t.get("total_rsc", 0) for t in latest["treasury"])
    foundation = next(
        (t for t in latest["treasury"] if t["label"] == "foundation_treasury"), None
    )
    foundation_rsc = foundation["total_rsc"] if foundation else 0
    foundation_pct = foundation_rsc / circ if circ > 0 else 0

    # Health color
    if apy > 0.10 and participation > 0.01:
        overall = "green"
    elif apy > 0.03:
        overall = "amber"
    else:
        overall = "red"

    return jsonify({
        "status": "ok",
        "pool_rsc": round(pool_rsc, 0),
        "participation": round(participation, 4),
        "apy": round(apy, 4),
        "price_usd": round(price, 6),
        "overall_health": overall,
        "concentration": {
            "foundation_pct": round(foundation_pct, 4),
            "foundation_rsc": round(foundation_rsc, 0),
            "level": "high" if foundation_pct > 0.40 else "medium" if foundation_pct > 0.20 else "low",
        },
        "self_balancing": "active" if apy > 0.05 else "slowing" if apy > 0.02 else "stalled",
        "timestamp": latest["pool"]["timestamp"],
    })


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    get_model()

    print("=" * 60)
    print("RSC Decentralized Endowment ABM Server")
    print("=" * 60)
    print("Mechanism: RSC held in RH account -> passive yield")
    print("Yield = (your RSC / total RSC) x emissions")
    print("Emissions: E(t) = 9.5M / 2^(t/64)")
    print()
    print("Endpoints:")
    print("  GET  /               - v3 Dashboard")
    print("  GET  /v4             - v4 Observatory")
    print("  GET  /api/status     - KPI summary")
    print("  GET  /api/scenarios  - Stress scenarios")
    print("  POST /api/init       - Initialize model")
    print("  POST /api/run        - Run N weeks")
    print()
    print("Open http://localhost:5000 in your browser")
    print("=" * 60)

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)
