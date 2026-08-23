"""
Gemini Multimodal Live API Bridge for LOONA
Provides full-duplex real-time audio, vision, and TTS over WebSockets.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import websockets
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("loona.live")
logger.setLevel(logging.INFO)

ROOT = Path(__file__).resolve().parent.parent
SOUL_PATH = ROOT / "identity" / "SOUL.md"
LIVE_API_URL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"

def get_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        # Check runtime/.env
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return key

def get_system_instruction() -> str:
    soul = ""
    if SOUL_PATH.exists():
        soul = SOUL_PATH.read_text(encoding="utf-8")
    return (
        "Eres LOONA, el sistema operativo personal y copiloto inteligente con personalidad viva. "
        "Interactúas con el usuario en tiempo real mediante voz y visión. "
        "Sé natural, concisa, empática, ágil y reflexiva. Habla en español de México con tono cálido y tecnológico.\n\n"
        f"{soul}"
    )

async def handle_live_websocket(websocket: WebSocket, voice: str = "Aoede"):
    await websocket.accept()
    api_key = get_gemini_key()

    if not api_key:
        await websocket.send_json({
            "type": "error",
            "message": "Falta GEMINI_API_KEY en runtime/.env para conectar a Gemini Live API."
        })
        await websocket.close()
        return

    gemini_ws_url = f"{LIVE_API_URL}?key={api_key}"
    print(f"[Live] 🌐 Conectando a Gemini Live API (Voz: {voice})...", flush=True)

    try:
        async with websockets.connect(gemini_ws_url) as gemini_ws:
            # 1. Enviar Setup inicial a Gemini Live
            setup_msg = {
                "setup": {
                    "model": "models/gemini-2.0-flash-exp",
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {
                                    "voiceName": voice  # Aoede, Puck, Charon, Fenrir, Kore
                                }
                            }
                        }
                    },
                    "systemInstruction": {
                        "parts": [{"text": get_system_instruction()}]
                    }
                }
            }
            await gemini_ws.send(json.dumps(setup_msg))
            
            # Recibir confirmación de setup
            initial_resp = await gemini_ws.recv()
            print(f"[Live] ✅ Setup inicial confirmado por Gemini Live", flush=True)
            await websocket.send_json({"type": "ready", "voice": voice, "model": "gemini-2.0-flash-exp"})

            # 2. Tarea para recibir de Cliente y enviar a Gemini Live
            async def client_to_gemini():
                try:
                    while True:
                        raw_data = await websocket.receive_text()
                        data = json.loads(raw_data)
                        msg_type = data.get("type")

                        if msg_type == "audio":
                            # PCM 16kHz audio base64
                            audio_b64 = data.get("data")
                            if audio_b64:
                                payload = {
                                    "realtimeInput": {
                                        "mediaChunks": [
                                            {
                                                "mimeType": "audio/pcm;rate=16000",
                                                "data": audio_b64
                                            }
                                        ]
                                    }
                                }
                                await gemini_ws.send(json.dumps(payload))

                        elif msg_type == "image":
                            # JPEG camera frame base64
                            image_b64 = data.get("data")
                            if image_b64:
                                payload = {
                                    "realtimeInput": {
                                        "mediaChunks": [
                                            {
                                                "mimeType": "image/jpeg",
                                                "data": image_b64
                                            }
                                        ]
                                    }
                                }
                                await gemini_ws.send(json.dumps(payload))

                        elif msg_type == "text":
                            text_content = data.get("text")
                            if text_content:
                                payload = {
                                    "clientContent": {
                                        "turns": [
                                            {
                                                "role": "user",
                                                "parts": [{"text": text_content}]
                                            }
                                        ],
                                        "turnComplete": True
                                    }
                                }
                                await gemini_ws.send(json.dumps(payload))

                except (WebSocketDisconnect, asyncio.CancelledError):
                    pass
                except Exception as e:
                    print(f"[Live] ⚠️ Error en client_to_gemini: {e}", flush=True)

            # 3. Tarea para recibir de Gemini Live y enviar al Cliente
            async def gemini_to_client():
                try:
                    async for message in gemini_ws:
                        resp = json.loads(message)
                        server_content = resp.get("serverContent")
                        if not server_content:
                            continue

                        # Interrupción detectada (usuario habló mientras Gemini hablaba)
                        if server_content.get("interrupted"):
                            await websocket.send_json({"type": "interrupted", "value": True})

                        model_turn = server_content.get("modelTurn")
                        if model_turn:
                            for part in model_turn.get("parts", []):
                                # Audio chunk en tiempo real (PCM 24kHz)
                                inline_data = part.get("inlineData")
                                if inline_data and inline_data.get("mimeType", "").startswith("audio/"):
                                    await websocket.send_json({
                                        "type": "audio",
                                        "data": inline_data.get("data"),
                                        "rate": 24000
                                    })
                                elif "data" in part and part.get("mimeType", "").startswith("audio/"):
                                    await websocket.send_json({
                                        "type": "audio",
                                        "data": part.get("data"),
                                        "rate": 24000
                                    })
                                
                                # Texto transcript
                                if "text" in part and part["text"]:
                                    await websocket.send_json({
                                        "type": "text",
                                        "text": part["text"]
                                    })

                        if server_content.get("turnComplete"):
                            await websocket.send_json({"type": "turn_complete", "value": True})

                except (WebSocketDisconnect, asyncio.CancelledError):
                    pass
                except Exception as e:
                    print(f"[Live] ⚠️ Error en gemini_to_client: {e}", flush=True)

            # Correr ambas tareas concurrentemente
            t1 = asyncio.create_task(client_to_gemini())
            t2 = asyncio.create_task(gemini_to_client())
            
            done, pending = await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
            for p in pending:
                p.cancel()

    except Exception as exc:
        print(f"[Live] ❌ Error conectando a Gemini Live: {exc}", flush=True)
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
