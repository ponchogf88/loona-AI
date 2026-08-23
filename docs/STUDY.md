# Estudio de uso — protocolo v1

## Qué medimos

| Evento | Dónde | Qué NO se guarda |
|--------|-------|------------------|
| `session_start` | HUD load | — |
| `chat` | POST /api/chat | el texto |
| `tts` | GET /api/tts | el texto largo |
| `news_open` | HUD noticias | URLs de artículos no |

Archivo: `runtime/state/usage.jsonl`  
Agregado vivo: `GET /api/metrics` → counts + p50/p95 chat/tts + uptime.

## Cómo correr una ronda (10–30 testers, un Mac o varios)

1. Instalar LOONA.app + `loona-install-login.sh`
2. Confirmar `study.enabled: true` (`GET /api/config`)
3. Tarea fija 15 min: abrir app → 3 chats → NOTICIAS → timeline semana/quincena → MIC
4. Exportar `usage.jsonl` + `GET /api/metrics`
5. Encuesta 5 preguntas (otro doc / Notion): ¿premium? ¿voz? ¿mareo 3D? ¿abrirían diario?

## Desempeño si “lo usan muchos”

v1 = **un operador por máquina**. El rate limit evita que un loop mate el iMac.

Si N laptops: cada una tiene su JSONL. Junta en una carpeta `study/round-1/`.

No escales a un VPS público sin auth. ROADMAP.md.

## Criterio de “listo para pruebas”

- App abre sin terminal
- Health 200
- Chat responde (DeepSeek u otro)
- Metrics incrementan tras una sesión
- Un tester no ve `.env` ni keys
