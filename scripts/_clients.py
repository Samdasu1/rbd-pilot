"""Unified per-host client layer.

Each `call_*` function returns a dict with normalized keys so downstream
ledger code is host-agnostic:

  {
    "raw":            <verbatim model output, str>,
    "input_tokens":   <prompt tokens, int>,
    "output_tokens":  <completion tokens, int>,
    "latency_ms":     <wall-clock latency, int>,
    "model":          <model id used, str>,
    "ollama_digest":  <SHA hash of GGUF, str | None>     # Ollama only
    "cache_creation_input_tokens": <claude only, int>,
    "cache_read_input_tokens":     <claude only, int>,
  }

`call_by_panel(model_id, system, user, ...)` dispatches to the right caller
based on the panel entry.
"""

from __future__ import annotations

import os
import time
from typing import Optional

import _models


# ------------------ OpenAI (gpt-5) ------------------

def call_openai(model_id: str, system: str, user: str, *,
                max_tokens: int = 1500, temperature: float = 0.0,
                force_json: bool = False) -> dict:
    import openai
    client = openai.OpenAI()
    t0 = time.time()
    # gpt-5 quirks (vs gpt-4o):
    #   - rejects `max_tokens`; use `max_completion_tokens`
    #   - rejects `temperature` other than the default → omit when caller wants 0.0
    kwargs = dict(
        model=model_id,
        max_completion_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    # Only send temperature for non-gpt-5 models (gpt-4o etc. still accept it).
    if not model_id.startswith("gpt-5"):
        kwargs["temperature"] = temperature
    if force_json:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return {
        "raw": resp.choices[0].message.content,
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
        "latency_ms": int((time.time() - t0) * 1000),
        "model": model_id,
        "ollama_digest": None,
    }


# ------------------ Codex CLI (gpt-5 family via ChatGPT subscription) ------------------

class CodexFailure(Exception):
    """Raised when codex CLI fails in a way that should trigger API fallback."""
    pass


_CODEX_RATE_LIMIT_INDICATORS = (
    "rate_limit", "rate limit", "quota", "exhausted", "exceeded", "429",
    "too many requests", "usage limit",
)


def _parse_codex_stdout(stdout: str) -> str:
    """Extract the final assistant response from codex exec stdout.

    Codex output structure:
        OpenAI Codex v...
        --------
        [metadata: workdir/model/sandbox/...]
        --------
        user
        <prompt>

        [optional: codex / exec turns]

        codex
        <FINAL RESPONSE>

        tokens used
        NNN
    """
    lines = stdout.split("\n")
    last_codex = -1
    tokens_used = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s == "codex":
            last_codex = i
        elif s == "tokens used":
            tokens_used = i
    if last_codex >= 0:
        # Long-form output with metadata + 'codex' / 'tokens used' markers.
        end = tokens_used if tokens_used > last_codex else len(lines)
        body = "\n".join(lines[last_codex + 1:end]).strip()
    else:
        # Short-form output: stdout is just the response text.
        body = stdout.strip()
    # Strip markdown json fences if present
    if body.startswith("```json"):
        body = body[len("```json"):].strip()
    elif body.startswith("```"):
        body = body[len("```"):].strip()
    if body.endswith("```"):
        body = body[:-3].strip()
    return body


def call_codex_exec(system: str, user: str, *,
                    max_tokens: int = 1500, force_json: bool = False,
                    timeout_s: int = 600) -> dict:
    """Invoke codex CLI in non-interactive exec mode. Returns same dict shape as call_openai.

    Codex shells out via ChatGPT subscription rather than the OpenAI API. Token
    usage and pricing are not surfaced (input_tokens/output_tokens reported as -1).
    Raises CodexFailure on rate-limit / quota / non-zero exit / empty response —
    callers should fallback to call_openai.
    """
    import subprocess
    parts = []
    if system:
        parts.append(f"[SYSTEM]\n{system}\n[/SYSTEM]")
    parts.append(user)
    if force_json:
        parts.append("\nIMPORTANT: Respond with valid JSON only. Do not run any commands. Do not include any prose, comments, or markdown fences before or after the JSON.")
    else:
        parts.append("\nIMPORTANT: Respond with the answer text only. Do not run any commands.")
    prompt = "\n\n".join(parts)

    t0 = time.time()
    try:
        proc = subprocess.run(
            ["codex", "exec",
             "--sandbox", "read-only",
             "--skip-git-repo-check",
             prompt],
            capture_output=True, text=True, timeout=timeout_s,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as e:
        raise CodexFailure(f"timeout after {timeout_s}s") from e

    err_l = (proc.stderr or "").lower()
    out_l = (proc.stdout or "").lower()
    if any(ind in err_l for ind in _CODEX_RATE_LIMIT_INDICATORS) or \
       any(ind in out_l for ind in _CODEX_RATE_LIMIT_INDICATORS):
        raise CodexFailure(f"rate-limit/quota signal: stderr={proc.stderr[:200]} stdout={proc.stdout[:200]}")

    if proc.returncode != 0:
        raise CodexFailure(f"non-zero exit {proc.returncode}: {proc.stderr[:300]}")

    raw = _parse_codex_stdout(proc.stdout)
    if not raw or not raw.strip():
        raise CodexFailure(f"empty response from codex")

    return {
        "raw": raw,
        "input_tokens": -1,
        "output_tokens": -1,
        "latency_ms": int((time.time() - t0) * 1000),
        "model": "gpt-5-via-codex",
        "ollama_digest": None,
    }


_CODEX_QUOTA_STRATEGIES = ("fallback", "wait_5h", "wait_weekly")


def _quota_strategy() -> str:
    s = os.environ.get("CODEX_QUOTA_STRATEGY", "fallback").lower()
    return s if s in _CODEX_QUOTA_STRATEGIES else "fallback"


def call_openai_via_codex_or_api(model_id: str, system: str, user: str, *,
                                  max_tokens: int = 1500, temperature: float = 0.0,
                                  force_json: bool = False,
                                  prefer_codex: bool = True) -> dict:
    """Primary path: codex CLI. Behavior on codex rate-limit/quota signal is
    controlled by env var CODEX_QUOTA_STRATEGY:
      fallback (default) — switch to OpenAI API immediately (paid)
      wait_5h            — sleep 5h10m, retry codex (preserves subscription)
      wait_weekly        — sleep 24h, retry codex (weekly bucket recovers slowly)
    Used for gpt-5 family calls when the user wants to consume ChatGPT
    subscription rather than API quota.
    """
    import sys
    if prefer_codex and model_id.startswith("gpt-5"):
        strategy = _quota_strategy()
        while True:
            try:
                result = call_codex_exec(system, user,
                                         max_tokens=max_tokens, force_json=force_json)
                result["_path"] = "codex"
                return result
            except CodexFailure as e:
                if strategy == "fallback":
                    print(f"  [codex→api fallback] {e}", file=sys.stderr)
                    break
                if strategy == "wait_5h":
                    sleep_s = 5 * 3600 + 600   # 5h10m past the bucket boundary
                elif strategy == "wait_weekly":
                    sleep_s = 24 * 3600        # poll daily until weekly bucket recovers
                else:
                    print(f"  [codex→api fallback] {e}", file=sys.stderr)
                    break
                wake = time.strftime("%Y-%m-%d %H:%M",
                                     time.localtime(time.time() + sleep_s))
                print(f"  [codex quota — strategy={strategy}; sleeping until ~{wake}] {e}",
                      file=sys.stderr)
                time.sleep(sleep_s)
                # loop and retry codex
    result = call_openai(model_id, system, user,
                         max_tokens=max_tokens, temperature=temperature,
                         force_json=force_json)
    result["_path"] = "api"
    return result


# ------------------ Google (gemini-2.5-pro) ------------------

def call_google_genai(model_id: str, system: str, user: str, *,
                      max_tokens: int = 1500, temperature: float = 0.0,
                      force_json: bool = False) -> dict:
    from google import genai
    from google.genai import types as gtypes
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    t0 = time.time()
    # NOTE: gemini-2.5-pro does NOT support thinking_budget=0 (thinking is
    # always-on for pro). gemini-2.5-flash does support disabling. Only pass
    # thinking_config when the model is a flash variant.
    config_kwargs = dict(
        system_instruction=system,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    if "flash" in model_id.lower():
        config_kwargs["thinking_config"] = gtypes.ThinkingConfig(thinking_budget=0)
    config = gtypes.GenerateContentConfig(**config_kwargs)
    if force_json:
        config.response_mime_type = "application/json"
    resp = client.models.generate_content(model=model_id, contents=user, config=config)
    return {
        "raw": resp.text,
        "input_tokens": resp.usage_metadata.prompt_token_count,
        "output_tokens": resp.usage_metadata.candidates_token_count,
        "latency_ms": int((time.time() - t0) * 1000),
        "model": model_id,
        "ollama_digest": None,
    }


# ------------------ xAI (grok-4) ------------------

def call_xai(model_id: str, system: str, user: str, *,
             max_tokens: int = 1500, temperature: float = 0.0,
             force_json: bool = False) -> dict:
    """xAI exposes an OpenAI-compatible chat endpoint."""
    import openai
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("XAI_API_KEY env var not set")
    client = openai.OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    t0 = time.time()
    kwargs = dict(
        model=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    if force_json:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return {
        "raw": resp.choices[0].message.content,
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
        "latency_ms": int((time.time() - t0) * 1000),
        "model": model_id,
        "ollama_digest": None,
    }


# ------------------ Ollama (local open-weight models) ------------------

def _ollama_tag_to_digest(tag: str) -> Optional[str]:
    """Look up the SHA digest of a locally-pulled Ollama model."""
    import subprocess
    try:
        out = subprocess.check_output(["ollama", "show", tag, "--modelfile"],
                                      stderr=subprocess.DEVNULL, text=True, timeout=5)
        for line in out.splitlines():
            if line.startswith("# Modelfile generated by "):
                continue
            if "FROM " in line and "sha256:" in line:
                return line.split("sha256:")[1].split(" ")[0].strip()
    except Exception:
        return None
    return None


def call_ollama(model_id: str, system: str, user: str, *,
                max_tokens: int = 1500, temperature: float = 0.0,
                force_json: bool = False,
                base_url: str = "http://localhost:11434") -> dict:
    import requests
    tag = _models.ollama_tag_of(model_id)
    t0 = time.time()
    options = {
        "temperature": temperature,
        "num_predict": max_tokens,
    }
    payload = {
        "model": tag,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": options,
    }
    if force_json:
        payload["format"] = "json"
    resp = requests.post(f"{base_url}/api/chat", json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    return {
        "raw": data["message"]["content"],
        "input_tokens": data.get("prompt_eval_count", 0),
        "output_tokens": data.get("eval_count", 0),
        "latency_ms": int((time.time() - t0) * 1000),
        "model": model_id,
        "ollama_digest": _ollama_tag_to_digest(tag),
    }


# ------------------ Anthropic (Claude API — only used if needed; not for executor) ------------------
# Executor (claude-opus-4-7) is invoked through the Claude Code interactive session,
# NOT through the API. This function exists for completeness / fallback only.

def call_anthropic(model_id: str, system: str, user: str, *,
                   max_tokens: int = 1500, temperature: float = 0.0,
                   force_json: bool = False) -> dict:
    """Anthropic doesn't have a `response_format=json_object` mode like OpenAI;
    if `force_json=True` we append a JSON-only instruction to the system prompt.

    NOTE: claude-opus-4-7 deprecated the `temperature` parameter. We send it
    only for models that still accept it (sonnet-4.x, haiku-4.x).
    """
    import anthropic
    if force_json:
        system = system + "\n\nOutput exactly one JSON object. No prose before or after. No code fences."
    client = anthropic.Anthropic()
    t0 = time.time()
    create_kwargs = dict(
        model=model_id,
        max_tokens=max_tokens,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    if "opus-4-7" not in model_id:
        create_kwargs["temperature"] = temperature
    msg = client.messages.create(**create_kwargs)
    return {
        "raw": msg.content[0].text,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
        "cache_creation_input_tokens": getattr(msg.usage, "cache_creation_input_tokens", 0),
        "cache_read_input_tokens": getattr(msg.usage, "cache_read_input_tokens", 0),
        "latency_ms": int((time.time() - t0) * 1000),
        "model": model_id,
        "ollama_digest": None,
    }


# ------------------ Dispatcher ------------------

_DISPATCH = {
    # OpenAI is routed through codex CLI (ChatGPT subscription) by default,
    # with API fallback on rate-limit/quota errors. Set env CODEX_PREFER_API=1
    # to skip codex and go straight to API.
    "openai": (lambda *a, **k: call_openai_via_codex_or_api(
        *a, prefer_codex=os.environ.get("CODEX_PREFER_API", "0") != "1", **k)),
    "google_genai": call_google_genai,
    "xai": call_xai,
    "ollama": call_ollama,
    "anthropic": call_anthropic,
}


def call_by_panel(model_id: str, system: str, user: str, **kwargs) -> dict:
    """Dispatch to the right caller based on the panel entry's `client` field.

    Raises if model is `executor` (claude_code_session) — the executor is invoked
    by the Claude Code session itself, not via this client layer.
    """
    client_key = _models.client_of(model_id)
    if client_key == "claude_code_session":
        raise RuntimeError(
            f"model {model_id} is the executor; it is invoked by the Claude Code "
            f"session, not via _clients.py. Use the session-handoff path instead."
        )
    fn = _DISPATCH.get(client_key)
    if fn is None:
        raise KeyError(f"no client registered for {client_key!r} (model {model_id})")
    return fn(model_id, system, user, **kwargs)


# ------------------ Cost estimation ------------------

# Pricing as of 2026-05; update when vendors change rates. None for Ollama/local.
_PRICE_PER_M_TOKEN = {
    # (input, output) USD per 1M tokens
    "gpt-5": (5.0, 30.0),
    "gemini-2.5-pro": (1.25, 10.0),
    "grok-4": (3.0, 15.0),
    # Anthropic pricing kept for fallback completeness
    "claude-opus-4-7": (None, None),  # subscription, not metered for this paper
}


def estimate_cost_usd(model_id: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    if _models.host_of(model_id) == "ollama":
        return 0.0
    rates = _PRICE_PER_M_TOKEN.get(model_id)
    if rates is None or rates[0] is None:
        return None
    in_rate, out_rate = rates
    # Defensive: providers may return None for token counts on empty/blocked responses.
    in_t = input_tokens or 0
    out_t = output_tokens or 0
    return round(in_t * in_rate / 1e6 + out_t * out_rate / 1e6, 6)


if __name__ == "__main__":
    # Smoke check — dry-run the dispatcher mapping without calling real APIs.
    for mid in ["gpt-5", "gemini-2.5-pro", "grok-4", "llama-3.1-70b-instruct",
                "qwen-2.5-7b-instruct"]:
        print(f"{mid:35s} -> client={_models.client_of(mid):15s} tier={_models.tier_of(mid)}")
