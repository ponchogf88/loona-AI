#!/usr/bin/env bash
# Copia el proyecto a iCloud Desktop/Projects/LOONA sin secretos ni venv.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$HOME/Desktop/Projects/LOONA"
mkdir -p "$DEST/repo" "$DEST/vault" "$DEST/brand"

rsync -a --delete \
  --exclude '.venv/' \
  --exclude 'runtime/.env' \
  --exclude 'runtime/.env.*' \
  --exclude 'runtime/state/tts/' \
  --exclude 'runtime/__pycache__/' \
  --exclude '**/__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'runtime/.pid' \
  --exclude 'runtime/logs/*.log' \
  --exclude '.git/' \
  --exclude 'dist/*.zip' \
  "$ROOT/" "$DEST/repo/"

# Brand a la raíz iCloud para que se vea en Finder
rsync -a "$ROOT/brand/" "$DEST/brand/"

# Vault: todos los md + brand notes
mkdir -p "$DEST/vault/wiki" "$DEST/vault/brand" "$DEST/vault/video" "$DEST/vault/dashboards" "$DEST/vault/identity" "$DEST/vault/log" "$DEST/vault/ops" "$DEST/ops" "$DEST/informes"
rsync -a --include '*/' --include '*.md' --exclude '*' "$ROOT/docs/" "$DEST/vault/wiki/"
rsync -a --include '*/' --include '*.md' --exclude '*' "$ROOT/identity/" "$DEST/vault/identity/"
rsync -a --include '*.md' --exclude '*' "$ROOT/brand/" "$DEST/vault/brand/" 2>/dev/null || true
cp -f "$ROOT/README.md" "$DEST/vault/wiki/README-repo.md" 2>/dev/null || true
cp -f "$ROOT/ROADMAP.md" "$DEST/vault/wiki/ROADMAP.md" 2>/dev/null || true
mkdir -p "$ROOT/docs/ops"
for f in INVESTIGACIONES PLAN-DE-ACCION RESULTADOS TIEMPO-Y-TOKENS; do
  if [ -f "$ROOT/docs/ops/${f}.md" ]; then
    cp -f "$ROOT/docs/ops/${f}.md" "$DEST/ops/${f}.md"
    cp -f "$ROOT/docs/ops/${f}.md" "$DEST/vault/ops/${f}.md"
  fi
done
[ -f "$ROOT/docs/QUIEN_HIZO_QUE.md" ] && cp -f "$ROOT/docs/QUIEN_HIZO_QUE.md" "$DEST/ops/QUIEN-HIZO-QUE.md"
[ -f "$ROOT/docs/PENDIENTES.md" ] && cp -f "$ROOT/docs/PENDIENTES.md" "$DEST/ops/QUE-FALTA.md"
cp -f "$ROOT/docs/VAULT_HOME.md" "$DEST/vault/00-HOME.md"
cp -f "$ROOT/docs/VISION.md" "$DEST/vault/01-VISION.md"
cp -f "$ROOT/docs/PENDIENTES.md" "$DEST/vault/02-PENDIENTES.md"
cp -f "$ROOT/docs/BITACORA.md" "$DEST/vault/03-BITACORA.md"
cp -f "$ROOT/docs/QUIEN_HIZO_QUE.md" "$DEST/vault/04-QUIEN-HIZO-QUE.md"
cp -f "$ROOT/docs/video/STACK_EXPLAINER.md" "$DEST/vault/video/STACK_EXPLAINER.md"
cp -f "$ROOT/docs/video/GUION_EXPLAINER_240.md" "$DEST/vault/video/GUION_EXPLAINER_240.md"
cp -f "$ROOT/docs/dashboards/README.md" "$DEST/vault/dashboards/README.md"
cp -f "$ROOT/brand/BRAND.md" "$DEST/vault/brand/BRAND.md"

cat > "$DEST/00-ABRE-ESTO.md" <<'EOF'
# LOONA — carpeta iCloud (casa del proyecto)

Escritorio → Projects → **LOONA**. Esto se sincroniza a iCloud.

## Mapa (ábrelo así)

| Carpeta / archivo | Qué es |
|---|---|
| `00-ABRE-ESTO.md` | Este mapa |
| `ops/INVESTIGACIONES.md` | Qué investigamos y de dónde |
| `ops/PLAN-DE-ACCION.md` | Qué sigue, en orden |
| `ops/RESULTADOS.md` | Qué ya existe |
| `ops/QUE-FALTA.md` | Pendientes P0 |
| `ops/QUIEN-HIZO-QUE.md` | Grok / Agy / Claude / Codex / Chuy |
| `ops/TIEMPO-Y-TOKENS.md` | Horas y tokens aprox |
| `INFORME-ULTIMO.md` | Último corte automático |
| `informes/` | Cortes 10:00 y 23:00 todos los días |
| `brand/` | Logo, lockup, mark, app icon, .icns |
| `repo/` | Código **sin** `.env` ni venv |
| `vault/` | Obsidian — Open folder as vault |

## Live

- HUD: http://127.0.0.1:8766
- Vida: http://127.0.0.1:8766/dash.html
- App: `~/Applications/LOONA.app`
- Trabajo con keys: `/Users/imac/loona` (nunca copies `.env` aquí)

## Reloj

LaunchAgent `com.loona.informe` → **10:00 y 23:00** hora del iMac (MTY).
También `com.loona.improve` a las 07:10 (health + briefing).
EOF

echo "sync → $DEST"
