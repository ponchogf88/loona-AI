# LOONA Architecture

Self-hosted personal OS. Visual language inspired by Zoey OS (closed SaaS). Not a fork.

## Estado observable (2026-08-12)

- Este workspace contiene identidad, configuración y documentación.
- `config/loona.schema.json` y `config/loona.default.json` ya existen y son la fuente de verdad de los knobs.
- No hay archivos de implementación bajo `hud/` ni `runtime/` en el estado inspeccionado; por tanto, no se afirma que el HUD o la API estén operativos.
- La interfaz pendiente entre runtime y HUD está definida en [`docs/API.md`](API.md).

## Contenedores y ownership

- `hud/` — Agy: World View (Three.js particles), Config View, Knowledge View, chat panel. TODO: crear implementación y screenshots.
- `runtime/` — Claude Code: control plane local en `127.0.0.1` (FastAPI o OpenClaw Gateway). TODO: implementar `/api/health`, `/api/config`, `/api/knowledge` y `/api/chat` más guardrails.
- `config/` — Codex: JSON schema + defaults; `loona.schema.json` es contrato y `loona.default.json` es baseline.
- `identity/` — Codex: `SOUL.md` y `MEMORY.md`; no contiene secretos.
- `docs/` — gobernanza, harness, contratos y status.

## Flujos y límites

1. HUD obtiene salud, configuración y knowledge mediante `docs/API.md`.
2. `PUT /api/config` valida el objeto completo contra el schema antes de persistirlo.
3. `POST /api/chat` usa el provider configurado; el middleware bloquea lectura de secretos y publicación.
4. La red local enlaza a `127.0.0.1`; `runtime/` no toca `/Users/imac/likinya`.

## Hardware envelope

iMac Intel i5-6500, 24 GB, macOS 12.7.6. No Apple Silicon, no CUDA, no mlx. El HUD debe mantener partículas dentro de 6.000–16.000 y bajar densidad si FPS < 24.

## See also

[`docs/API.md`](API.md) · [`docs/LOONA_Plan_Ingenieria.pdf`](LOONA_Plan_Ingenieria.pdf) · [`docs/GOVERNANCE.md`](GOVERNANCE.md) · [`config/loona.schema.json`](../config/loona.schema.json)
