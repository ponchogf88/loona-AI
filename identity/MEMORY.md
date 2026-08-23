# MEMORY.md — LOONA

## Hechos estables

- Owner: Chuy.
- Ubicación y zona horaria: Monterrey, América/Monterrey.
- Equipo: iMac Intel i5-6500, 24 GB de RAM, macOS Monterey 12.7.6.
- Workspace: space herdr **LOONA** (`wB`) en `/Users/imac/loona`.
- `P1 Likinya` (`/Users/imac/likinya`) está fuera de alcance y no se toca.

## Identidad de producto (estable)

- LOONA es el OS personal de Chuy. No se llama Jarvis. No clona Zoey.
- Inspiración visual/mando: Apex (Reznikov, reznikov-engineering.com/apex), Zoey (cara/morph), Jarvis (presencia).
- Hardware de esta casa: Nest Hub 2 = boca (Cast TTS, no Bluetooth). Eufy Indoor Cam E30 4K T8417 = ojo (1 frame al wake o “qué ves”). Cámara del escritorio = Capture/espejo.
- Soltek (`wC`, `/Users/imac/soltek`) es otro proyecto. No mezclar write-paths ni producto.

## Stack vivo

- Trabajo: `/Users/imac/loona`. Casa iCloud (sin `.env`): `~/Desktop/Projects/LOONA`.
- Live: `http://127.0.0.1:8766` (HUD) y `/dash.html` (shell, no datos reales).
- Cerebro: Gemini (cuenta `lic.jagf87@gmail.com`) / DeepSeek / Ollama fallback. Voz: edge-tts `es-MX-DaliaNeural`.
- Informes automáticos 10:00 y 23:00 MTY (`com.loona.informe`). Improve 07:10 (`com.loona.improve`).

## PAUSA 2026-08-13

Chuy pidió PARK para reabrir la terminal y grabar. Handoff canónico: `docs/PAUSA.md`.  
Al cortar: Claude tenía `runtime/cast.py` empezado (discover + quote TTS) **sin** cablear en `app.py`. No existen aún `/api/devices`, `/api/cast/tts` ni `/api/eyes/*`.  
Resume solo con la palabra **REANUDAR**.

## Límites de memoria

- Este archivo contiene hechos operativos estables, no secretos ni claves.
- Las claves deben permanecer en el llavero o en `runtime/.env` gitignored; nunca se copian aquí.

## Registro de sesión — 2026-08-16

- Corte detallado: `docs/CORTE_SESION_20260816.md`.
- Se documentaron los cortes LOONA del 14–15 de agosto: Cast/devices/desktop snap 200; Eufy con cuenta configurada pero RTSP ausente; Día 6 cerrado con `POST /api/cast/card` 200 en Choza; Día 7 queda como loop voz + tarjeta.
- Se alinearon `docs/API.md`, `docs/PENDIENTES.md`, `docs/BANDA_CEREBRO_LOONA.md`, `docs/STATUS.md`, `docs/PAUSA.md` y `docs/QUIEN_HIZO_QUE.md`.
- Agy pertenece a `wB:p1`; los stills desktop fueron rechazados y los stills HUD+orbe posteriores fueron aprobados. Claude pertenece a `wB:p2`; Codex a `wB:p3`.
- Se exploró publicar LOONA en el repositorio privado `https://github.com/ponchogf88/loona-AI`, pero no se inicializó Git, no se creó commit, no se añadió remoto y no se subieron archivos. `gh` no quedó autenticado.
- Likinya `w2` y Productos `wD` permanecen PARK y separados de LOONA.
