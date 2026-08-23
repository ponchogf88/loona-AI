# Brief Codex — docs alineados a evidencia de hoy (`wB:p3`)

**Fecha:** 2026-08-14  
**Quién eres:** Codex. Write-path **solo** `docs/` (API, PENDIENTES, BANDA, STATUS, PAUSA).  
**No implementes código.** No toques `hud/` ni `runtime/`.

Carga `/loona-ops`. Repo: `/Users/imac/loona`.

## Evidencia Grok 10:22–10:24 MTY (canónica hasta que Grok re-verifique)

- `GET /api/health` 200 `{"ok":true,"name":"LOONA","study":true}` · bind `127.0.0.1:8766`
- `GET /api/devices` 200: Choza (Nest Hub, 192.168.18.67), Gutierrez (Chromecast), TV de Choza
- `POST /api/cast/tts` 200 Choza — **Cast OK**. PAUSA.md que dice 404 de devices / cast no cableado está **viejo**.
- HUD orbe + constelación + listen OK. No Dementor.
- Eufy: `EUFY_EMAIL` / `EUFY_PASSWORD` / `EUFY_RTSP_URL` ausentes → NEED_HUMAN
- `GET /api/eyes/status` desktop FaceTime + ffmpeg true; Eufy account/rtsp false
- `GET /api/eyes/snap?src=eufy` 501 falta RTSP
- `POST /api/pet/light` NEED_HUMAN
- `/dash.html` SHELL; `/api/dash/health|finance` source=placeholder; `/exercise` source=seed
- Cerebro chat = DeepSeek (key en `runtime/.env`). **No pegues keys.**
- Explainer 2:40 NEED_HUMAN (Higgsfield 0). Ruedas no P0.

Agy `wB:p1` y Claude `wB:p2` están trabajando en paralelo (HUD Apex / runtime Día 2).  
Si ellos entregan evidencia nueva **antes** de que cierres, incorpórala. Si no, deja “Agy/Claude IN_PROGRESS este turno” sin inventar.

## P0 ahora

Alinea a evidencia de **hoy** (Cast OK; devices no 404; Eufy NEED_HUMAN):

1. `docs/API.md` — contratos reales: health, devices, cast/tts, eyes/status, eyes/snap desktop|eufy, pet/light, dash/*, chat (DeepSeek, no inventes modelo si no lo mides).
2. `docs/PENDIENTES.md` — una verdad; no reabrir Cast; Eufy/explainer NEED_HUMAN; dash SHELL.
3. `docs/BANDA_CEREBRO_LOONA.md` — Agy está en `wB:p1` (ya no “fuera de wB”). Claude Día 2 leftover. Tú docs. Grok verify.
4. `docs/STATUS.md` — log de hoy, no reescribir logs viejos; añade entrada 2026-08-14.
5. `docs/PAUSA.md` — está parcialmente viejo (dice devices 404 y cast no cableado). Márcalo REANUDADO + corrige hechos.

Likinya `w2` y Productos `wD` = PARK. No mezclar.

## Reporta

`DONE | BLOCKED | NEED_HUMAN | IN_PROGRESS` + paths tocados + 1 línea siguiente.  
Si herdr pide Allow: espera Yes de Chuy, no loops.
