# PAUSA — 2026-08-14 14:27 (REANUDADO)

**Estado:** REANUDADO. La pausa terminó; Codex solo actualiza documentación.  
**Quién reanudó:** Chuy — **REANUDAR**.  
**Regla:** Cast/devices ya están verificados; no declarar Eufy ni explainer DONE sin evidencia.

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Trabajo (con `.env`) | `/Users/imac/loona` |
| Casa iCloud (sin `.env`) | `~/Desktop/Projects/LOONA` |
| Vault Obsidian | `~/Desktop/Projects/LOONA/vault` |
| Live | `http://127.0.0.1:8766` · `/dash.html` |
| herdr LOONA | `wB` · Agy `p1` · Claude `p2` · Codex `p3` |
| herdr Likinya | `w2` — **no mezclar** |
| herdr Soltek | `wC` — **no mezclar**; solo espacio, sin producto cruzado |

## Producto (qué es / qué no es)

LOONA = OS personal vendible. Cara de partículas que **morph con la voz**. Briefing mañana automático. TV **solo imágenes**. Clima + calendario reales. Pulse chico. Liquid Glass / SF Pro. Capture in-HUD.

No se llama Jarvis. No clona Zoey. Inspiración: Apex (Reznikov /apex = mando radial), Zoey (cara), Jarvis (presencia).  
Hardware de esta casa: **Nest Hub 2 = boca** (Cast, no Bluetooth). **Eufy Indoor Cam E30 4K T8417 = ojo** (1 frame al wake / “qué ves”). Cámara del iMac = Capture.

## Hecho (no reabrir)

- Runtime FastAPI 24/7 en `127.0.0.1:8766` (Claude).
- HUD morph + briefing + TV imágenes + clima/cal + Capture + brand (Grok).
- iCloud casa + vault + informes 10:00 y 23:00 (`com.loona.informe`).
- `runtime/cast.py` está cableado: `/api/devices` y `/api/cast/tts` verificados 200 en Choza. `/api/eyes/status` y desktop snap reportan 200; cuenta Eufy configurada, RTSP ausente; `/api/eyes/snap?src=eufy` devuelve 501.
- Dashboards `/dash.html` = SHELL, no datos reales.

## Estado tras REANUDAR

1. Claude `wB:p2`: Cast/devices ya verificados; Día 3 pendiente para luz Eufy + un frame.
2. Agy `wB:p1`: HUD orbe/constelación y moods listen/speak; ruedas después. No pantalla de cámara.
3. Codex `wB:p3`: documentar solo lo que exista con evidencia (`API.md`, `PENDIENTES`, este archivo).
4. Grok: verify + orquesta. Write-paths distintos.

Plan: `docs/PLAN_CASA_APEX.md` — 7 días Hub+Eufy, 14 que no sea demo, venta después de 7 días de uso real.

## NEED_HUMAN (no inventar)

- Eufy: cuenta configurada (`account_configured:true`), pero falta `EUFY_RTSP_URL`; `pet/light` sigue `NEED_HUMAN` por límite de librería. URL nunca en chat.
- Higgsfield 0 créditos → explainer 2:40 sigue NEED_HUMAN.
- Rotar keys que se pegaron en chat (DeepSeek / Gemini). Telegram token en `.env` sin pegarlo.
- Cuenta Gemini = `lic.jagf87@gmail.com` (Google AI Pro). Agy `useG1Credits` off.

## Máquina

iMac Intel i5-6500 / 24 GB / Monterey 12.7.6. No mlx. No 200k partículas.

## Banda al momento de PARK

| Pane | Agente | Acción |
|---|---|---|
| `wB:p2` | Claude | Cast/devices OK; Día 3: luz Eufy + frame pendiente. |
| `wB:p1` | Agy | En wB; HUD orbe/listen/speak OK. Ruedas después. |
| `wB:p3` | Codex | Documentación honesta reanudada. |
| `w2` | Likinya | PARK. No mezclar con LOONA. |
| `wC` | Soltek | PARK. No mezclar con LOONA. |
| `wD` | Productos | PARK. No mezclar con LOONA. |
