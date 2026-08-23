---
name: loona-ops
description: >
  DNA táctico de LOONA (P2 del studio). Cargar antes de tocar HUD, runtime,
  brand, vault, explainer o dashboards. No es Likinya.
---

# LOONA ops

Repo de trabajo: `/Users/imac/loona`  
Casa iCloud: `~/Desktop/Projects/LOONA`  
Vault: `~/Desktop/Projects/LOONA/vault`  
Live: `http://127.0.0.1:8766` · dashboards: `/dash.html`

## Qué es

OS personal de Chuy. Cara de partículas que **morph con la voz**. Briefing de mañana automático. TV de noticias **solo imágenes**. Clima + calendario. Pulse chico. Dashboards de vida.

No te llamas Jarvis. No clonas Zoey. No mezclas write-paths con `/Users/imac/likinya`.

## Brand (obligatorio)

Leer `brand/BRAND.md`.  
Void negro + **pocas** estrellas tipo SpaceX (brillan, se mueven lento, sin ruido).  
Oro champagne. Syne + Outfit. Lockup `brand/lockup.jpg`.  
Inspiración Aevon: https://dribbble.com/shots/27478902-Aevon-Framer-Template-for-AI-Automation-Agencies

## Video explainer (obligatorio)

Leer `docs/video/STACK_EXPLAINER.md` y `docs/video/GUION_EXPLAINER_240.md`.

Calidad:

- https://www.youtube.com/watch?v=APyR9lTFVhI (Higgsfield SaaS, cursor, micro-UI)
- https://www.youtube.com/watch?v=VAk5lMgzdl0 (match cut, UI morph, mockup)

Duración 2:20–3:10. Default 16×10 s. Stack = Higgsfield explainer (mismo que Likinya para motion) + Vibe Motion para UI.  
Hoy: **0 créditos Higgsfield** → no fingir que el MP4 existe.

## Write-paths

| Quién | Escribe |
|---|---|
| Agy | `hud/` visual, `refs/product/`, stills brand |
| Claude | `runtime/` |
| Codex | `docs/` (excepto este skill si Grok lo mantiene) |
| Grok | orquesta, verify, vault/iCloud scripts, brand lock |

## Casa e informe

iCloud: `~/Desktop/Projects/LOONA`  
Ops (todos leen): `docs/ops/` = investigaciones, plan, resultados, tokens.  
**Informe automático 10:00 y 23:00 MTY** (`com.loona.informe` → `informes/` + `INFORME-ULTIMO.md`). No lo borres. No declares tokens nuevos si el script no los midió.

## P0 vivo

`docs/PENDIENTES.md` · `docs/BANDA_CEREBRO_LOONA.md` · `docs/VISION.md` · `docs/ops/`

## Nunca

- Inventar saldos, kilos o DMs
- Pegar API keys
- Estrellas densas / mint / giro de adorno
- Letras de noticia en la TV
- Declarar explainer DONE sin URL de MP4
