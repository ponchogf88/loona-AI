# Stack canónico — SaaS video explainer LOONA

**Inyectar a toda la banda.** Un solo pipeline. No improvisar Ken Burns.

## Calidad (ver antes de generar)

1. [How to Make SaaS Explainer Videos with AI — Thomas Creates](https://www.youtube.com/watch?v=APyR9lTFVhI)  
   Higgsfield. Fake screen recording. Cursor que recorre. Microinteracciones 200–500 ms. Números reales. UI de **nuestro** producto, no una CRM inventada. Vibe Motion + stills del HUD real.
2. [Top 3 SaaS Video Transitions — MahdiEdits](https://www.youtube.com/watch?v=VAk5lMgzdl0)  
   Match cut · UI morph · mockup (el motion sigue adentro del iPhone/Mac). Speed graph pico **en** el corte.

Duración LOONA: **2:20–3:10**. Default: **16 bloques × 10 s = 2:40**.

## De dónde viene (Likinya)

Ya está pagado / ensayado en Likinya:

| Capa | Tool | LOONA |
|---|---|---|
| Stills de producto | HUD live + screenshots | `refs/product/` y `brand/hero-space.jpg` |
| Estilo / still cinematic | Higgsfield `nano_banana_2` o GPT Image | Style key Aevon-void + estrellas sparse |
| Motion UI | Higgsfield **Vibe Motion** (Thomas) | Cursor, hover, click, check |
| Clip 10 s | `gemini_omni` | Un clip por bloque |
| Voz | `seed_audio` (explainer) o edge-tts Dalia para prototipo | ES-MX, sin “en este video” |
| Ensamble | `higgsfield generate create explainer_video` | N pares audio+video |
| Fallback Liky | Seedance / Veo / CapCut | Solo si Higgsfield no da |

Docs Liky de origen (no copiar persona Likinya):  
`likinya/docs/pipeline/MOTION_VO_LIPSYNC_PIPELINE.md`  
`likinya/docs/pipeline/STACK_UGC_AVATAR_GRATIS.md`  
Skill: `higgsfield-video-explainer`

## Receta Higgsfield (explainer)

```
N = 16
preset o style key = Editorial Motion Graphics
  id: 56fc6472-33b7-45dc-83ff-80c71d40aec6
  O custom: negro void + oro champagne + 5 estrellas (Aevon/SpaceX)
aspect = 16:9
idioma = español
character = faceless (producto, no mascota)
subtitulos = off (LOONA ya habla; el video es UI)
```

Orden estricto del skill:

1. Style key (una imagen, se pega a todos los clips)
2. 16 líneas de narración (`GUION_EXPLAINER_240.md`)
3. 16 prompts de clip (inglés, SCENE/MOTION/AUDIO, sin texto en frame)
4. 16 `seed_audio` con **una** voz
5. 16 `gemini_omni` 10 s
6. `explainer_video` assemble

Nunca `video_explainer` monolítico. Nunca devolver clips sueltos.

## Transiciones (obligatorias en los prompts)

- Bloques 1→2, 8→9: **match cut** (la luna/mark se queda, el mundo cambia).
- Bloques 5→6, 10→11: **UI morph** (card se estira a dashboard).
- Bloques 14→15: **mockup** (el HUD sigue adentro de un iMac / iPhone).

Cursor falso + hover 300 ms en todo shot de interfaz.

## Estado 2026-08-12

`higgsfield account status` → **free plan, 0 credits**.  
Guión y stack listos. Render = **NEED_HUMAN: recargar créditos Higgsfield** (o Veo/Vids de Gemini Workspace si el founder prefiere no pagar Higgsfield hoy).

## Quién toca qué

| Agente | Write-path |
|---|---|
| Grok | Este doc + verify URL final |
| Agy | Stills reales del HUD + style key en `brand/` `refs/product/` |
| Codex | Guión / captions / timestamps |
| Claude | No monta el video. Solo QA visual si hay browser |

## Anti-patrones

- Ken Burns sobre un PNG y llamarlo explainer
- UI inventada que no es LOONA
- Letras de noticias en el TV (el producto no las muestra)
- Más de 55 estrellas en un frame
- Verde menta
