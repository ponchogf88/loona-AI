"""Model bridge for LOONA chat.

Honors config.brain.provider. Keys live in runtime/.env (never the repo).
DeepSeek is OpenAI-compatible: https://api.deepseek.com/v1
"""
from __future__ import annotations

import os
from pathlib import Path

import httpx

OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"
OLLAMA_MODEL = "llama3.2:3b"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
TIMEOUT = 60.0


def load_runtime_env() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_runtime_env()


async def _ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get("http://127.0.0.1:11434/api/tags")
            return resp.status_code == 200
    except httpx.HTTPError:
        return False


async def _call_xai(text: str, system_prompt: str | None) -> str:
    key = os.environ["XAI_API_KEY"]
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": text})
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "grok-4", "messages": messages},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_gemini(text: str, system_prompt: str | None) -> str:
    key = os.environ["GEMINI_API_KEY"]
    model = "gemini-2.5-flash"
    payload = {"contents": [{"parts": [{"text": text}]}]}
    if system_prompt:
        payload["system_instruction"] = {"parts": [{"text": system_prompt}]}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": key},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def _call_anthropic(text: str, system_prompt: str | None) -> str:
    key = os.environ["ANTHROPIC_API_KEY"]
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": text}],
    }
    if system_prompt:
        payload["system"] = system_prompt
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]


async def _call_ollama(text: str, system_prompt: str | None, model: str = OLLAMA_MODEL) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": text})
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"{OLLAMA_BASE_URL}/chat/completions",
            json={"model": model, "messages": messages},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_openai_compatible(
    text: str,
    system_prompt: str | None,
    *,
    base_url: str,
    api_key: str,
    model: str,
) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": text})
    root = base_url.rstrip("/")
    url = f"{root}/chat/completions"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _resolve_provider(brain: dict | None) -> tuple[str, str, str, str]:
    """Return (provider, model, base_url, api_key_or_empty)."""
    brain = brain or {}
    wanted = (brain.get("provider") or "").strip().lower()
    model = (brain.get("model") or "").strip()
    base = (brain.get("baseUrl") or "").strip()

    if wanted in ("deepseek", "openai-compatible") and (
        os.environ.get("DEEPSEEK_API_KEY")
        or (wanted == "openai-compatible" and os.environ.get("OPENAI_API_KEY"))
    ):
        key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
        return (
            "deepseek" if "deepseek" in (base.lower() + wanted) or wanted == "deepseek" else "openai-compatible",
            model or "deepseek-chat",
            base or DEEPSEEK_BASE_URL,
            key,
        )
    if wanted == "xai" and os.environ.get("XAI_API_KEY"):
        return "xai", model or "grok-4", base or "https://api.x.ai/v1", os.environ["XAI_API_KEY"]
    if wanted == "gemini" and os.environ.get("GEMINI_API_KEY"):
        return "gemini", model or "gemini-2.5-flash", base, os.environ["GEMINI_API_KEY"]
    if wanted == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", model or "claude-sonnet-4-5", base, os.environ["ANTHROPIC_API_KEY"]
    if wanted == "ollama":
        return "ollama", model or OLLAMA_MODEL, base or OLLAMA_BASE_URL, ""

    if os.environ.get("DEEPSEEK_API_KEY"):
        return "deepseek", model or "deepseek-chat", base or DEEPSEEK_BASE_URL, os.environ["DEEPSEEK_API_KEY"]
    if os.environ.get("XAI_API_KEY"):
        return "xai", model or "grok-4", "https://api.x.ai/v1", os.environ["XAI_API_KEY"]
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini", model or "gemini-2.5-flash", "", os.environ["GEMINI_API_KEY"]
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", model or "claude-sonnet-4-5", "", os.environ["ANTHROPIC_API_KEY"]
    return "ollama", model or OLLAMA_MODEL, OLLAMA_BASE_URL, ""


async def get_reply(
    text: str,
    ollama_model: str = OLLAMA_MODEL,
    system_prompt: str | None = None,
    brain: dict | None = None,
) -> dict:
    """Returns {reply, provider} or {reply: None, provider: None, error: ...}."""
    if brain is None:
        brain = {"provider": "auto", "model": ollama_model}
    provider, model, base_url, api_key = _resolve_provider(brain)

    async def call(t: str) -> str:
        if provider in ("deepseek", "openai-compatible"):
            if not api_key:
                raise RuntimeError("missing DEEPSEEK_API_KEY or OPENAI_API_KEY")
            return await _call_openai_compatible(
                t, system_prompt, base_url=base_url, api_key=api_key, model=model
            )
        if provider == "xai":
            return await _call_xai(t, system_prompt)
        if provider == "gemini":
            return await _call_gemini(t, system_prompt)
        if provider == "anthropic":
            return await _call_anthropic(t, system_prompt)
        if not await _ollama_available():
            raise RuntimeError("ollama not running")
        return await _call_ollama(t, system_prompt, model)

    try:
        reply = await call(text)
        return {"reply": reply, "provider": provider, "model": model}
    except (httpx.HTTPError, KeyError, IndexError, RuntimeError) as exc:
        error = str(exc) or f"{type(exc).__name__}"
        return {"reply": None, "provider": provider, "error": error}
