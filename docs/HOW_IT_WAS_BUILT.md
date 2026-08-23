# Cómo se construyó LOONA

Guía corta para el comprador/clonador.

- **Stack:** HUD local HTML/CSS/JavaScript + Three.js Points; configuración JSON Schema; control plane FastAPI en `runtime/`.
- **Workspace:** herdr space `LOONA` (`wB`) en `/Users/imac/loona`; `hud/` es visual, `runtime/` API, `identity/` memoria.
- **Cerebro:** DeepSeek por endpoint compatible con OpenAI; Ollama queda como fallback. Las claves viven en `runtime/.env` y no entran al zip.
- **Voz:** `edge-tts`, voz Dalia Neural `es-MX`; no `speechSynthesis`.
- **Noticias y tiempo:** RSS + `og:image`; timeline de día, semana, quincena, mes y año.
- **24/7:** `~/Applications/LOONA.app` + LaunchAgent `com.loona.runtime`.
- **Estudio:** `runtime/usage.jsonl` (o la ruta configurada por `LOONA_USAGE_LOG`) guarda eventos opt-in: vista, chat, MIC, TV, timeline, duración, FPS y provider. `/api/metrics` resume sin exponer prompts ni claves.

Diagramas: `refs/diagrams/`. Producto: `docs/PRODUCT_LOONA.md`.
