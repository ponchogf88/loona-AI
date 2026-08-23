# LOONA — Harness de loop

Protocolo para que Agy, Claude Code y Codex **no se detengan** hasta su checklist local verde.

## Arranque de cada turno

```
1. cd /Users/imac/loona
2. Leer identity/SOUL.md
3. Leer docs/GOVERNANCE.md (tu write-path)
4. Leer docs/ROLES.md (tu rol)
5. Leer docs/STATUS.md (qué falta)
6. Ejecutar el siguiente ítem NO verde de TU checklist
7. Escribir evidencia en docs/STATUS.md
8. Si tu checklist no está 100% verde → volver a 6
```

## Checklists por agente

### Agy / Antigravity (`hud/`)

- [ ] `hud/index.html` + `hud/css/loona.css` + `hud/js/world.js` cargan sin build step
- [ ] Cabeza de partículas (Three.js Points), paleta teal→violeta, label LOONA
- [ ] Orbs companions alrededor (mínimo 3 placeholders: Brain, Memory, Ops)
- [ ] Botón KNOWLEDGE VIEW abre panel con texto de `identity/SOUL.md` (via /api/knowledge)
- [ ] Chat panel redimensionable (derecha)
- [ ] Config view con controles ligados a `config/loona.schema.json` (≥12)
- [ ] Activity widget (quién trabaja)
- [ ] Screenshot en `refs/hud/world.png` y `refs/hud/config.png`

### Claude Code (`runtime/`)

- [ ] Runtime local en `127.0.0.1` (FastAPI o OpenClaw gateway documentado)
- [ ] `GET /api/health` → `{ok:true,name:"LOONA"}`
- [ ] `GET /api/config` / `PUT /api/config` validan contra schema
- [ ] `GET /api/knowledge` sirve SOUL + MEMORY
- [ ] `POST /api/chat` habla con un provider (env key o Ollama)
- [ ] Guardrail middleware: block publish / read-secrets
- [ ] OpenClaw instalado **o** nota en STATUS de por qué se usa runtime propio
- [ ] Script `scripts/loona-up.sh` levanta HUD+API

### Codex (`docs/` `identity/` `config/`)

- [ ] `identity/MEMORY.md` con hechos del owner y hardware
- [ ] `config/loona.schema.json` + `config/loona.default.json`
- [ ] `docs/ARCHITECTURE.md` alineado al código real (no wishful)
- [ ] `docs/STATUS.md` con checkboxes vivos
- [ ] `docs/API.md` de los endpoints que Claude exponga
- [ ] No contradecir SOUL.md

## Formato de STATUS (append-only por turno)

```
## [ISO-8601 MTY] agente=<nombre> estado=IN_PROGRESS|DONE|BLOCKED|NEED_HUMAN
- hizo: ...
- evidencia: path o error exacto
- siguiente: ...
```

## Anti-stall

Si no puedes completar un ítem en 15 min: deja BLOCKED con el error exacto y pasa al siguiente ítem de TU lista. No te quedes puliendo.

Si el otro agente no entregó un contrato (ej. `/api/knowledge` no existe): implementa un **stub local** y documenta el contrato en STATUS. No esperes en silencio.
