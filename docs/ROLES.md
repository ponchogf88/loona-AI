# LOONA — Roles de la banda

Skill de proyecto: `loona-ops`. Brand y explainer son ley, no opinión.

## Grok (Lead / Verify)

- Orquesta, escribe plan PDF, harness, gobierna.
- Verifica DoD. Único que declara proyecto DONE.
- No reescribe HUD ni runtime de los otros.

## Agy — Antigravity CLI (`wB:p1`) — HUD / World View

**Quiere:** que LOONA se *vea* como Zoey, de otro color, con más perillas.

**Hace:** World View 3D, partícula-cabeza, companions orbs, Knowledge View UI, Config View, chat panel, activity widget, theme tokens.

**No hace:** instalar OpenClaw, escribir SOUL, publicar.

**Refs visuales:** `refs/zoey/` (frames del screen recording 2026-08-12). Paleta: fondo `#070B12`, acento `#5EEAD4` → `#7C5CFF`, label LOONA.

**Stack UI:** HTML + CSS + JS vanilla + Three.js CDN. Sin React si se puede. Sin Electron el día 1 (browser localhost).

## Claude Code (`wB:p2`) — Runtime / Orchestration

**Quiere:** un proceso local que el HUD pueda hablar.

**Hace:** OpenClaw onboard **o** FastAPI `runtime/` si OpenClaw pelea con Monterey/Intel. Endpoints health/config/knowledge/chat. Guardrails. `loona-up.sh`. Bridge de modelo (Grok/Gemini/Claude/Ollama).

**No hace:** CSS de la cabeza 3D. No toca likinya.

**Prioridad de cerebro:** env `LOONA_PROVIDER` = `openai-compatible`. Base URL configurable. Default: intentar Ollama `qwen2.5:3b` si no hay key; si hay `GEMINI_API_KEY` / `XAI_API_KEY` / `ANTHROPIC_API_KEY`, usar esa.

## Codex (`wB:p3`) — Spec / Config / Memoria

**Quiere:** una sola verdad en markdown + JSON schema.

**Hace:** MEMORY.md, schema de config (más opciones que Zoey), API.md, STATUS vivo, alinear ARCHITECTURE al código.

**No hace:** implementar Three.js ni el server más allá de stubs documentales.

## Contratos entre roles

```
Codex  --schema-->  Claude (valida PUT /api/config)
Claude --/api/*-->  Agy (fetch)
Agy    --refs/hud/*.png--> Grok (verify visual)
Todos  --STATUS.md--> Grok (loop)
```
