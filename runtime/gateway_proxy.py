"""
Local Failover AI Gateway for Claude Code & Multimodal Workflows
Acts as an Anthropic-compatible reverse proxy with transparent multi-provider failover:
Gemini 2.5/2.0 -> DeepSeek -> OpenRouter / Groq -> Ollama Local.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator

import httpx
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# Load environment from runtime/.env or current directory
ENV_CANDIDATES = [
    Path(__file__).resolve().parent / ".env",
    Path("/Users/imac/loona/runtime/.env"),
    Path.home() / ".env",
]

for env_path in ENV_CANDIDATES:
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v

app = FastAPI(title="Local AI Failover Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_active_providers() -> list[dict[str, Any]]:
    providers = []
    
    # 1. Gemini (Priority 1)
    if os.getenv("GEMINI_API_KEY"):
        providers.append({
            "name": "Gemini 2.5 Flash",
            "type": "gemini",
            "model": "gemini-2.5-flash",
            "api_key": os.getenv("GEMINI_API_KEY"),
        })
        providers.append({
            "name": "Gemini 2.0 Flash",
            "type": "gemini",
            "model": "gemini-2.0-flash",
            "api_key": os.getenv("GEMINI_API_KEY"),
        })

    # 2. DeepSeek (Priority 2)
    if os.getenv("DEEPSEEK_API_KEY"):
        providers.append({
            "name": "DeepSeek Chat",
            "type": "openai",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        })

    # 3. Groq (Priority 3 if configured)
    if os.getenv("GROQ_API_KEY"):
        providers.append({
            "name": "Groq Llama 3.3 70B",
            "type": "openai",
            "base_url": "https://api.groq.com/openai/v1",
            "model": "llama-3.3-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY"),
        })

    # 4. OpenRouter (Priority 4 if configured)
    if os.getenv("OPENROUTER_API_KEY"):
        providers.append({
            "name": "OpenRouter Free/Open",
            "type": "openai",
            "base_url": "https://openrouter.ai/api/v1",
            "model": "google/gemini-2.0-flash-exp:free",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
        })

    # 5. Ollama Local (Fallback)
    providers.append({
        "name": "Ollama Local (127.0.0.1:11434)",
        "type": "openai",
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "llama3.2:3b",
        "api_key": "ollama",
    })
    
    return providers


def parse_anthropic_request(body: dict[str, Any]) -> tuple[str | None, list[dict[str, str]], int, float]:
    system_prompt = None
    sys_field = body.get("system")
    if isinstance(sys_field, str):
        system_prompt = sys_field
    elif isinstance(sys_field, list):
        parts = []
        for p in sys_field:
            if isinstance(p, dict) and "text" in p:
                parts.append(p["text"])
            elif isinstance(p, str):
                parts.append(p)
        system_prompt = "\n".join(parts)

    messages = []
    for m in body.get("messages", []):
        role = m.get("role", "user")
        content = m.get("content", "")
        if isinstance(content, str):
            messages.append({"role": role, "content": content})
        elif isinstance(content, list):
            text_blocks = []
            for b in content:
                if isinstance(b, dict) and b.get("type") == "text":
                    text_blocks.append(b.get("text", ""))
                elif isinstance(b, str):
                    text_blocks.append(b)
            messages.append({"role": role, "content": "\n".join(text_blocks)})

    max_tokens = body.get("max_tokens", 4096)
    temperature = body.get("temperature", 0.7)
    return system_prompt, messages, max_tokens, temperature


async def call_gemini(provider: dict[str, Any], system_prompt: str | None, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> str:
    key = provider["api_key"]
    model = provider["model"]
    
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
        
    payload: dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        }
    }
    if system_prompt:
        payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(url, params={"key": key}, json=payload)
        if resp.status_code == 429:
            raise HTTPException(status_code=429, detail="Gemini Rate Limit Exceeded")
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def call_openai_compat(provider: dict[str, Any], system_prompt: str | None, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> str:
    url = f"{provider['base_url'].rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"}
    
    payload_messages = []
    if system_prompt:
        payload_messages.append({"role": "system", "content": system_prompt})
    payload_messages.extend(messages)
    
    payload = {
        "model": provider["model"],
        "messages": payload_messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code == 429:
            raise HTTPException(status_code=429, detail=f"{provider['name']} Rate Limit Exceeded")
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def stream_anthropic_sse(text: str, model: str) -> AsyncGenerator[str, None]:
    msg_id = f"msg_{uuid.uuid4().hex[:16]}"
    
    # 1. message_start
    start_event = {
        "type": "message_start",
        "message": {
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "content": [],
            "model": model,
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 1}
        }
    }
    yield f"event: message_start\ndata: {json.dumps(start_event)}\n\n"
    await asyncio.sleep(0.01)
    
    # 2. content_block_start
    block_start = {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": ""}
    }
    yield f"event: content_block_start\ndata: {json.dumps(block_start)}\n\n"
    
    # 3. content_block_delta in chunks
    chunk_size = 32
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        delta_event = {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": chunk}
        }
        yield f"event: content_block_delta\ndata: {json.dumps(delta_event)}\n\n"
        await asyncio.sleep(0.005)
        
    # 4. content_block_stop
    block_stop = {"type": "content_block_stop", "index": 0}
    yield f"event: content_block_stop\ndata: {json.dumps(block_stop)}\n\n"
    
    # 5. message_delta
    msg_delta = {
        "type": "message_delta",
        "delta": {"stop_reason": "end_turn", "stop_sequence": None},
        "usage": {"output_tokens": len(text) // 4}
    }
    yield f"event: message_delta\ndata: {json.dumps(msg_delta)}\n\n"
    
    # 6. message_stop
    yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"


@app.post("/v1/messages")
@app.post("/messages")
async def messages_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    system_prompt, messages, max_tokens, temperature = parse_anthropic_request(body)
    stream = body.get("stream", False)
    
    providers = get_active_providers()
    last_error = None
    response_text = None
    winning_provider = None

    for p in providers:
        try:
            print(f"[Gateway] 🔄 Probando nodo: {p['name']} ({p.get('model')})...", flush=True)
            if p["type"] == "gemini":
                response_text = await call_gemini(p, system_prompt, messages, max_tokens, temperature)
            else:
                response_text = await call_openai_compat(p, system_prompt, messages, max_tokens, temperature)
            
            winning_provider = p
            print(f"[Gateway] ✅ Éxito con proveedor: {p['name']}", flush=True)
            break
        except Exception as err:
            print(f"[Gateway] ⚠️ Fallo en {p['name']}: {err}. Conmutando al siguiente nodo...", flush=True)
            last_error = err
            continue

    if response_text is None:
        raise HTTPException(
            status_code=503,
            detail=f"Todos los conectores de IA fallaron. Último error: {str(last_error)}"
        )

    out_model = body.get("model", "claude-opus-free")
    
    if stream:
        return StreamingResponse(
            stream_anthropic_sse(response_text, out_model),
            media_type="text/event-stream"
        )

    # Standard JSON Response
    msg_id = f"msg_{uuid.uuid4().hex[:16]}"
    return JSONResponse(content={
        "id": msg_id,
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ],
        "model": out_model,
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": len(response_text) // 4
        }
    })


@app.get("/health")
@app.get("/")
async def health():
    providers = get_active_providers()
    return {
        "status": "online",
        "service": "Claude Code Failover Gateway",
        "active_nodes": [f"{p['name']} ({p.get('model')})" for p in providers],
        "port": 8080,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Iniciando Local AI Failover Gateway en http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
