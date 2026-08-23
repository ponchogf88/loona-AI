# Brief Agy — REJECT stills, rehacer HUD-only (`wB:p1`)

**Fecha:** 2026-08-14 14:27 MTY  
**Write-path:** `hud/` + `refs/product/` únicamente.

Grok verify rechazó tus 5 PNG de las 10:42. **No son stills de producto.**

Son capturas del **escritorio entero** (Finder, herdr, Hermes verde, calendario Lilly, TV de noticias). `05-hud-complete.png` ni siquiera muestra el HUD. `hud/js` y `hud/css` **no se tocaron** (mtime 13 ago).

## Rechazado

- `refs/product/01-orb-idle.png`
- `refs/product/02-orb-listen.png`
- `refs/product/03-orb-speak.png`
- `refs/product/04-orb-alert.png`
- `refs/product/05-hud-complete.png`

## P0 ahora (sin curl, sin Allow si puedes)

1. Abre Chrome **solo** en `http://127.0.0.1:8766/?mood=idle` (luego listen, speak, alert). Fullscreen o ventana HUD a pantalla completa. **Cero** Finder/herdr/calendario/otras apps.
2. Captura **solo la ventana/viewport del HUD**. En macOS: `screencapture -l <ChromeWindowID>` o screenshot de pestaña, **nunca** `screencapture` del desktop entero.
3. Sobrescribe esos 5 paths. El 5º = HUD completo (orbe + reloj + clima + dock), todavía solo viewport.
4. Si vas a pulir orbe/moods: edita `hud/css/loona.css` + `hud/js/world.js` de verdad. Si ya está bien, no finjas polish: entrega stills limpios.

No React. No Electron. No cámara. No Likinya. No `runtime/`.  
Si Allow: espera Yes y **sigue en archivos HUD** sin más curl.

Reporta: `DONE|BLOCKED|NEED_HUMAN` + 5 paths + 1 línea.
