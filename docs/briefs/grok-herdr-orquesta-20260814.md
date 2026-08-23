# Plan orquesta — Grok herdr LOONA (`wB:p4`)

**Fecha:** 2026-08-14  
**Quién eres:** Grok Lead/Verify en herdr workspace **LOONA `wB`**.  
**No eres:** el Grok de este chat Hermes, ni Likinya `w2`, ni Productos `wD`.

Chuy: orquesta a **todos** los panes de `wB`. Un write-path por agente. No abandones.

## Carga

1. `/loona-ops`
2. `docs/PENDIENTES.md` · `docs/BANDA_CEREBRO_LOONA.md` · `docs/PLAN_CASA_APEX.md` · `docs/ROLES.md`
3. Brief verify de hoy: `docs/briefs/grok-continua-20260814.txt`

## Panes (solo estos)

| Pane | Agente | Write-path | No toca |
|---|---|---|---|
| `wB:p1` | Agy | `hud/` visual (orbe, moods, Apex polish) | `runtime/`, docs canónicos |
| `wB:p2` | Claude | `runtime/` (cast/eyes/pet/dash APIs) | `hud/css`, `hud/js` |
| `wB:p3` | Codex | `docs/` (API, PENDIENTES, BANDA, STATUS) | código HUD/runtime |
| `wB:p4` | Tú (Grok) | orquesta + verify + `docs/briefs/` | no reescribas HUD/runtime de los otros |

Likinya `w2` y Productos `wD` = **PARK**. No les mandes prompts.

## Hecho hoy (no reabrir)

Verify 10:22 MTY:
- `GET /api/health` 200 · bind `127.0.0.1:8766`
- Choza Nest Hub `192.168.18.67` · `POST /api/cast/tts` 200
- HUD orbe + constelación + listen OK. No Dementor.
- Eufy `account_configured:false` · `EUFY_*` ausentes → **NEED_HUMAN**
- `/dash.html` = SHELL
- Cerebro chat = DeepSeek (key ya en `runtime/.env`). No la pegues.

## P0 — despacha en paralelo (paths distintos)

Usa:

```bash
herdr agent prompt wB:p1 "…"
herdr agent prompt wB:p2 "…"
herdr agent prompt wB:p3 "…"
```

Si un pane dice Allow: **NEED_HUMAN** (Chuy da Yes). No loops.

### Agy `wB:p1` — HUD Apex (Día 4–5, sin esperar Eufy)

- Orbe (no humanoide, no esfera hueca/Dementor).
- Moods listen / speak / alert / idle visibles.
- Reloj + clima en HUD si el runtime ya los sirve.
- 5 screenshots **distintos** en `refs/product/` (no pantalla de cámara).
- No React. No Electron. No Likinya.

### Claude `wB:p2` — runtime (Día 2 leftover + Día 3 gated)

- Cada `speak()` / chat que hable también Cast a Choza (Día 2). Evidencia curl.
- `/api/pet/light` y `/api/eyes/snap?src=eufy`: si faltan `EUFY_*`, deja **NEED_HUMAN** y no inventes env.
- Desktop snap `src=desktop` debe funcionar (FaceTime/ffmpeg).
- Dash `/api/dash/*`: honestos (placeholder ≠ dato real).
- Bind solo `127.0.0.1:8766`. Reinicia si hace falta.

### Codex `wB:p3` — docs

- Alinea `API.md` / `PENDIENTES.md` / `BANDA_CEREBRO_LOONA.md` / `STATUS.md` / `PAUSA.md` a evidencia de **hoy** (Cast OK; devices no 404; Eufy NEED_HUMAN).
- No implementes código.

## Tú (verify) después de que contesten

1. `herdr agent read wB:p1 --lines 40` (igual p2, p3).
2. Curl health / devices / cast / eyes. HUD en browser si puedes.
3. Actualiza `BANDA_CEREBRO_LOONA.md` + `PENDIENTES.md`.
4. Reporta: `DONE | BLOCKED | NEED_HUMAN | IN_PROGRESS` + evidencia + siguiente 1 línea.

## Fuera de alcance

- Hermes CLI / MacBook gateway / Desktop Hermes.
- Explainer MP4 (Higgsfield 0). Ruedas. iCloud Desktop upload.
- Pegar keys / RTSP. 24/7 stream Eufy.
- Contratar SaaS. Mezclar Soltek/Likinya.

## NEED_HUMAN real (no bloquees al resto)

Chuy pone en `runtime/.env` (sin chat): `EUFY_EMAIL`, `EUFY_PASSWORD`, `EUFY_RTSP_URL` (menú NAS T8417).  
Hasta entonces: Agy y Codex **siguen**. Claude no se queda parado esperando Eufy.

Arranca ya. No preguntes. Despacha los 3 prompts.
