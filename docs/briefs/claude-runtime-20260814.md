# Brief Claude — runtime Día 2 leftover + Día 3 gated (`wB:p2`)

**Fecha:** 2026-08-14  
**Quién eres:** Claude. Write-path **solo** `runtime/` (+ restart `loona-up` si hace falta).  
**No tocas:** `hud/css`, `hud/js`, docs canónicos (eso es Codex), Likinya.

Carga `/loona-ops`. Live: `http://127.0.0.1:8766` bind **solo** `127.0.0.1` (nunca `0.0.0.0`).

## Hecho hoy (no reabrir)

Grok verify 10:22 MTY:
- `GET /api/health` 200 · `GET /api/devices` 200 Choza 192.168.18.67
- `POST /api/cast/tts` 200 Choza
- `POST /api/chat` ya hace `asyncio.create_task(cast.cast_tts(speak))` — confirma que **todas** las bocas hablan
- Eufy `account_configured:false` · `EUFY_*` ausentes → **NEED_HUMAN**. No inventes env. No pegues keys/RTSP.
- Dash `/api/dash/*` placeholders honestos. `/dash.html` = SHELL (no finjas datos).

## P0 ahora

1. **Día 2 leftover:** cada `speak()` / chat / pet-talk que hable también Cast a Choza. Evidencia curl de:
   - `POST /api/chat` (un mensaje inocuo) → 200 + confirmaste que dispara Cast (log o side-effect)
   - `POST /api/cast/tts` `{"text":"Loona orquesta."}` → 200 Choza
   - Si hay otro path de voz (`/api/amigo`, `/api/viva`, `/api/pet` talk) que aún no casta: cablealo. Si ya casta: evidencia y no reescribas.
2. **Día 3 gated (no te pares):**
   - `POST /api/pet/light` y `GET /api/eyes/snap?src=eufy`: si faltan `EUFY_*`, deja **NEED_HUMAN** (501/flag). No inventes cuenta.
   - `GET /api/eyes/snap?src=desktop` **debe funcionar** (FaceTime/ffmpeg). Evidencia curl: `ok`, `src=desktop`, bytes > 0.
3. **Dash honestos:** `/api/dash/health|finance|exercise` — placeholder ≠ dato real. Si ya es honesto, no toques. Si algún campo finge “live”, márcalo `source=placeholder|seed`.
4. Reinicia solo si cambiaste código: `LOONA_SKIP_PIP=1 bash scripts/loona-up.sh`. Confirma bind `127.0.0.1:8766`.

## Reporta

`DONE | BLOCKED | NEED_HUMAN | IN_PROGRESS` + curls (status + json recortado, sin keys) + 1 línea siguiente.  
Si herdr pide Allow: espera Yes de Chuy, no loops.  
**No esperes Eufy para entregar Día 2 + desktop snap.**
