# Brief Agy — HUD Apex Día 4–5 (`wB:p1`)

**Fecha:** 2026-08-14  
**Quién eres:** Agy. Write-path **solo** `hud/` + `refs/product/`.  
**No tocas:** `runtime/`, docs canónicos (`PENDIENTES`, `BANDA`, `API`, `STATUS`, `PAUSA`), Likinya, Electron, React.

Carga `/loona-ops` y `brand/BRAND.md`. Live: `http://127.0.0.1:8766`

## Hecho hoy (no reabrir)

Grok verify 10:22 MTY: HUD orbe liquid-glass + constelación + listen OK. No Dementor.  
Moods ya existen: `window.LoonaWorld.setMood('idle'|'listen'|'speak'|'alert')` y `?mood=`.  
Clock `#hud-clock` y fetch `/api/weather` ya están en `hud/js/os.js`.  
Eufy = NEED_HUMAN. **No esperes Eufy.** No screenshots de cámara.

## P0 ahora (Día 4–5 PLAN_CASA_APEX)

1. Pulir el **orbe** (presencia Apex): no humanoide, no esfera hueca/Dementor. Void + pocas estrellas SpaceX + oro champagne.
2. Moods **visibles** (idle / listen / speak / alert): badge `#hud-status`, body classes, morph del orbe. Si ya están, hazlos más cinemáticos, no web-genéricos.
3. Reloj + clima en HUD si el runtime ya sirve `/api/weather` (sí sirve). No inventes cifras; consume el API.
4. 5 screenshots **distintos** en `refs/product/` (nombres nuevos o overwrite claro). No pantalla de cámara. Sugeridos:
   - orbe idle
   - listen
   - speak
   - alert
   - HUD completo (reloj+clima+orbe, no zoom de cámara)
5. No React. No Electron. HTML+CSS+JS vanilla + Three.js CDN.

## Reporta

`DONE | BLOCKED | NEED_HUMAN | IN_PROGRESS` + paths de screenshots + 1 línea siguiente.  
Si herdr pide Allow: espera Yes de Chuy, no loops.
