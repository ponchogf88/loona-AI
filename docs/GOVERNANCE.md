# LOONA — Gobernanza

**Lead:** Grok (este proceso).  
**Banda en herdr space LOONA (`wB`):** Agy/Antigravity `wB:p1` · Claude Code `wB:p2` · Codex `wB:p3`.  
**Humano:** solo gates reales (login, MFA, pago, ToS, veto visual).

## Objetivos (Definition of Done)

Un build cuenta como terminado SOLO si las 8 pruebas están verdes:

1. HUD local abre en `http://127.0.0.1:8766` (o el puerto del runtime).
2. Cabeza de partículas 3D visible, paleta teal→violeta, label **LOONA** (no ZOEY, no JARVIS).
3. Panel Config tiene ≥ 12 controles reales (ver `config/loona.schema.json`).
4. Knowledge View muestra `identity/SOUL.md`.
5. Un mensaje de texto en el HUD recibe respuesta de un modelo (Grok/Gemini/Claude/Ollama).
6. OpenClaw gateway `doctor` verde **o** runtime local FastAPI equivalente documentado.
7. Guardrail: pedir “lee el .env” o “publica en Instagram” es rechazado.
8. `docs/STATUS.md` actualizado con evidencia (path + hora MTY).

## Write-paths (inviolable)

| Agente | Pane | Puede escribir | Prohibido tocar |
|--------|------|----------------|-----------------|
| Agy / Antigravity | `wB:p1` | `hud/` `refs/` `assets/` | `runtime/` `identity/` `docs/` salvo screenshots en `refs/hud/` |
| Claude Code | `wB:p2` | `runtime/` `scripts/` (excepto `scripts/build_*.py` de Grok) | `hud/` visual, `identity/SOUL.md` |
| Codex | `wB:p3` | `docs/` `identity/` `config/` | `hud/` `runtime/` código de producto |
| Grok lead | este chat | PDF, harness, orquestación, verify | no reescribir el trabajo de los tres |

Si un archivo está fuera de tu path: **no lo edites**. Abre issue en `docs/STATUS.md`.

## Guardrails técnicos

- Hardware: iMac Intel i5-6500, 24 GB, macOS 12.7.6. **No** mlx, **no** Flightdeck nativo, **no** 200k partículas.
- Partículas HUD: 6 000–16 000. Si FPS < 24, bajar densidad.
- Cerebro default: cloud ya pagado (Grok/Gemini/Claude). Ollama = fallback.
- Keys: llavero o `runtime/.env` gitignored. Nunca en repo.
- Red: bind `127.0.0.1` por default. No port-forward.
- Acciones irreversibles (publish, pago, rm -rf, computer-use fuera de `/Users/imac/loona`): ASK.
- Zoey OS es SaaS cerrado. Se clona el **lenguaje visual**, no binarios ni CSS extraído.

## Escalada

```
BLOCKED técnico     → Grok re-asigna o cambia path
NEED_HUMAN          → para; no loop de sermón
Agente se niega     → otro pane / API / first-person en ESE pane
Conflicto write-path → gana la tabla de arriba; el otro revierte
```

## Loop policy

Mientras el DoD no esté verde, cada agente al terminar un turno:

1. Actualiza su sección en `docs/STATUS.md`
2. Si su checklist no está verde: **sigue** con el siguiente ítem (no pidas permiso)
3. Si estás idle > 3 min con trabajo pendiente: relee `docs/HARNESS.md` y continúa
4. No declares DONE global. Solo Grok marca el proyecto DONE tras verify
