"""Canonical model panel loader.

Single source of truth for which model fills which role. Reads
`data/pilot_v1.1/spec_models_panel.json` (the machine-readable companion to
`docs/spec_models_v1.0.md`) and exposes lookups by id, role, or tier.

Downstream scripts MUST NOT hardcode model ids — they should call
`models_by_role(...)` and dispatch on `m["host"]` / `m["client"]` to choose the
right caller (api / ollama / claude_code_session).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

PANEL_PATH = Path(__file__).resolve().parents[1] / "data" / "pilot_v1.1" / "spec_models_panel.json"


@lru_cache(maxsize=1)
def _panel() -> dict:
    with PANEL_PATH.open() as f:
        return json.load(f)


def panel_version() -> str:
    return _panel()["panel_version"]


def all_models() -> list[dict]:
    """Returns a fresh copy — mutating returned dicts will not pollute the cache."""
    import copy
    return copy.deepcopy(_panel()["models"])


def get_model(model_id: str) -> dict:
    import copy
    for m in _panel()["models"]:
        if m["id"] == model_id:
            return copy.deepcopy(m)
    raise KeyError(f"model id {model_id!r} not in panel {PANEL_PATH}")


def models_by_role(role: str) -> list[dict]:
    roles = _panel()["roles"]
    if role not in roles:
        raise KeyError(
            f"unknown role {role!r}; valid roles in {PANEL_PATH}: {sorted(roles)}"
        )
    return [get_model(mid) for mid in roles[role]]


def models_by_tier(tier: str) -> list[dict]:
    tiers = _panel()["tiers_by_id"]
    if tier not in tiers:
        raise KeyError(
            f"unknown tier {tier!r}; valid tiers in {PANEL_PATH}: {sorted(tiers)}"
        )
    return [get_model(mid) for mid in tiers[tier]]


def tier_of(model_id: str) -> str:
    return get_model(model_id)["tier"]


def host_of(model_id: str) -> str:
    return get_model(model_id)["host"]


def client_of(model_id: str) -> str:
    """Returns the dispatch key for the calling layer.

    For host=api models, returns the SDK key (openai / google_genai / xai).
    For host=ollama, returns 'ollama'.
    For host=claude_code_session, returns 'claude_code_session' (no API call).
    """
    m = get_model(model_id)
    if m["host"] == "ollama":
        return "ollama"
    if m["host"] == "claude_code_session":
        return "claude_code_session"
    return m.get("client", m["host"])


def ollama_tag_of(model_id: str) -> str:
    m = get_model(model_id)
    if m["host"] != "ollama":
        raise ValueError(f"{model_id} is not an Ollama-hosted model")
    return m["ollama_tag"]


if __name__ == "__main__":
    p = _panel()
    print(f"panel_version: {p['panel_version']}")
    print(f"total models : {len(p['models'])}")
    for role, ids in p["roles"].items():
        print(f"  role {role:30s} -> {len(ids)} model(s): {ids}")
    for tier, ids in p["tiers_by_id"].items():
        print(f"  tier {tier:8s} -> {len(ids)} model(s): {ids}")
