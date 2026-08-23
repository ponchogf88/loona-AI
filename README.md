# LOONA

Personal OS local para Mac: una cara de partículas 3D en un escenario glass,
voz neural, noticias con foto, timeline día/semana/quincena/mes/año y un
cerebro configurable (DeepSeek, Gemini, xAI, Anthropic u Ollama local). Todo
corre en tu máquina — no es SaaS, no es un chatbot en una pestaña.

**No es Zoey OS.** Inspiración visual. Código propio. MIT.

## Requisitos

- Mac (Intel o Apple Silicon). En Intel: 16 GB RAM+ recomendado.
- macOS 12 (Monterey) o más nuevo.
- Google Chrome (LOONA.app abre una ventana `--app`, no una pestaña; sin Chrome cae a Safari).
- Python 3.11+ (el instalador crea su propio venv en `runtime/.venv`, no toca tu Python global).
- Opcional: [Ollama](https://ollama.com) instalado con un modelo ≤7B (ej. `llama3.2:3b`) si no vas a usar una API key de pago.

## Arranque (tester)

```bash
cd /Users/imac/loona
bash scripts/loona-up.sh          # cerebro en 127.0.0.1:8766
open ~/Applications/LOONA.app     # ventana de programa, no pestaña
```

`~/Applications/LOONA.app` es un app bundle liviano (AppleScript) que llama a
`scripts/loona-app.sh`: levanta el runtime si no está vivo y abre Chrome en
modo `--app` apuntando a `http://127.0.0.1:8766`.

24/7 al login: `bash scripts/loona-install-login.sh`
(instala un LaunchAgent `com.loona.runtime` que arranca `loona-up.sh` al
iniciar sesión y lo mantiene vivo con `KeepAlive`).
Quitar: `bash scripts/loona-uninstall.sh`

## Keys (nunca en git)

Copia `.env.example` → `runtime/.env`:

```bash
cp .env.example runtime/.env
```

```
DEEPSEEK_API_KEY=
GEMINI_API_KEY=
TELEGRAM_BOT_TOKEN=
```

(`.env.example` trae la lista completa de providers soportados — xAI,
Anthropic, OpenAI-compatible — todos opcionales.) Sin ninguna key, LOONA usa
Ollama local automáticamente. `runtime/.env` está en `.gitignore`; LOONA nunca
lee ni imprime su contenido (bloqueado por guardrail, ver abajo).

## Guardrails

LOONA nunca lee `.env`/API keys/llavero, nunca publica en redes y nunca corre
comandos destructivos por instrucción de chat — cualquier intento devuelve
`HTTP 403 guardrail_blocked` en vez de ejecutarse. Ver `runtime/guardrails.py`.

## Estudios de uso masivo

Opt-in, apagado por defecto (`config.study.enabled`, `false` de fábrica).

1. Prender: `curl -X POST http://127.0.0.1:8766/api/study -d '{"enabled":true}' -H 'Content-Type: application/json'`
   (o `PUT /api/config {"study":{"enabled":true}}`). Confirmar con `GET /api/study`.
2. Cada sesión escribe `runtime/state/usage.jsonl` (eventos opt-in, **sin texto de chat/tts**,
   solo tipo + metadata + latencia). Gitignored.
3. Ver agregado en vivo: `GET http://127.0.0.1:8766/api/metrics` → counts + p50/p95
   de `chat`/`tts` + uptime.
4. Exportar una ronda: copia el archivo tal cual —
   `cp runtime/state/usage.jsonl study/round-1/$(hostname).jsonl` — o súbelo donde
   lo centralice el estudio. Es JSON Lines: una línea = un evento, se puede
   procesar con `jq`/pandas sin parseo especial.
5. Protocolo completo de ronda de estudio: `docs/STUDY.md`.

## Desempeño — nota honesta

**v1 es single-operator local.** Un proceso FastAPI, sin auth, pensado para
correr en un Mac y ser usado por su dueño (o un puñado de testers en la misma
red). `runtime/limits.py` pone un piso de seguridad: 40 requests/min por IP y
máximo 4 chats simultáneos (el resto recibe `HTTP 429` y debe reintentar) —
esto evita que un loop o un estudio con varios testers a la vez tumbe el
iMac, no convierte a LOONA en un servicio multi-tenant. Para eso: `ROADMAP.md`.

## Stack

FastAPI + HUD (Three.js) + DeepSeek/Gemini/xAI/Anthropic/Ollama + edge-tts (Dalia es-MX) + LaunchAgent.

Guía de construcción: `docs/HOW_IT_WAS_BUILT.md`  
Listing Gumroad: `docs/GUMROAD_LISTING.md`  
PDF visual: `docs/GUMROAD_LOONA.pdf`  
Roadmap: `ROADMAP.md`
