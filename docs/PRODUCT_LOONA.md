# LOONA — producto v1 (cerrar para uso + venta)

**No es un taller de pestañas.** Entrega: repo + app 24/7 + guía visual Gumroad.  
Founder: Chuy. No verde menta. No tipografía de novela. No cabeza “alien”.

## Ritual de mañana — automático

Al abrir `LOONA.app`, el HUD pide `GET /api/briefing` y prepara el día sin un click-to-read:

1. Saluda a Chuy.
2. Resume la rutina del día y el siguiente compromiso.
3. Lee el clima de Monterrey desde Open-Meteo.
4. Selecciona noticias de IA con imágenes.
5. Prepara el speech con voz Dalia para reproducirlo en el flujo de inicio.

El usuario puede quedarse en World View y escuchar el briefing; la información no aparece como un muro de texto. Después, el HUD mantiene disponibles el timeline, TV imagen-only, voz MIC, Pulse compacto y chat.

## APIs live del producto

- `GET /api/briefing` — saludo, rutina, clima MTY, noticias IA y speech.
- `GET /api/weather` — Open-Meteo para Monterrey.
- `GET /api/calendar` — mes y `upcoming`, consumido como timeline; no letter-grid.
- `GET /api/news?topic=ai` — feed visual con imágenes de Xataka, El País y Wired.

Referencia de contratos: [`docs/API.md`](API.md).

## Vida, dashboards y marca

El botón **VIDA** abre [`/dash.html`](http://127.0.0.1:8766/dash.html), una shell de dashboards para salud, finanzas, ejercicio, alimentación, calendarios y mensajes. Sirve como siguiente piso del producto: la UI está lista para cablear fuentes reales, pero cualquier cifra placeholder no representa un saldo o métrica verificada.

El calendario de Vida se lee como timeline/lista de próximos eventos, no como una cuadrícula de letras. La superficie conserva el lenguaje LOONA: void negro, oro escaso, estrellas sparse, hairlines, glass y Syne + Outfit.

### Brand paths

- `brand/lockup.jpg` — lockup principal luna + LOONA.
- `brand/mark-crescent.jpg` — media luna y estrella.
- `brand/wordmark.jpg` — wordmark oro.
- `brand/app-icon.jpg` — icono de app.
- `brand/hero-space.jpg` — hero para landing/explainer.
- `hud/brand/` — copias servidas por el HUD.

La marca usa void `#000000`/`#070B12`, oro champagne, cobre/magenta/violeta en la cabeza y 40–55 estrellas como máximo. Nunca verde menta ni una Vía Láctea densa.

### Stack explainer

El explainer de producto se planifica en [`docs/video/STACK_EXPLAINER.md`](video/STACK_EXPLAINER.md) con guion en [`docs/video/GUION_EXPLAINER_240.md`](video/GUION_EXPLAINER_240.md): 16 bloques × 10 s, 16:9, voz ES-MX, stills reales del HUD, cursor/microinteracciones y transiciones match cut/UI morph/mockup. El pipeline previsto usa style key, `seed_audio`, clips `gemini_omni` y ensamblado final. El stack y guion están documentados; el render no se declara DONE.

## DoD global (Grok solo marca DONE cuando TODO esto es verde)

1. World View **contenido**: márgenes visibles, la cara NO se sale de un escenario glass. Como Zoey en la laptop, no fullscreen bleed.
2. **Glassmorphism** real (blur + borde hairline + sombra), no paneles opacos.
3. **Multicolor** en la cabeza (ámbar → coral → magenta → violeta → oro). No un solo cobre.
4. Tipo **moderno elegante** (Syne + Outfit o equivalente Google Fonts). Nada de Garamond/IBM Plex.
5. Movimiento **lento, estable** (solo yaw suave). Cero wobble alien en X.
6. Timeline día/semana/quincena/mes/año sin cuadrícula de letras.
7. Noticias con fotos + TV on/off; TV muestra solo imágenes.
8. Voz neural (Dalia), no speechSynthesis; morph de voz en HUD.
9. `~/Applications/LOONA.app` + LaunchAgent 24/7.
10. Repo listo para zip Gumroad: README, LICENSE, install, `.gitignore`, sin `.env`.
11. Telemetría **opt-in** de uso/desempeño (eventos locales + hook para estudio).
12. PDF Gumroad **visual** (screenshots/tutorial, no muro de texto) en `docs/GUMROAD_LOONA.pdf`.
13. Pulse compacto para actividad y estado, sin competir con World View.

## Write-paths

| Agente | Pane | Escribe | No toca |
|--------|------|---------|---------|
| Agy | wB:p1 | `hud/` `refs/product/` | `runtime/` `docs/GUMROAD*` |
| Claude | wB:p2 | `runtime/` `scripts/` `README.md` `LICENSE` telemetría | `hud/css` `hud/js/world.js` |
| Codex | wB:p3 | `docs/GUMROAD_*.md` `docs/GUMROAD_LOONA.pdf` `docs/HOW_IT_WAS_BUILT.md` | código HUD/runtime salvo citar paths |

## Loop

Hasta tu checklist local verde. Append `docs/STATUS.md`. No preguntes permiso entre ítems.
