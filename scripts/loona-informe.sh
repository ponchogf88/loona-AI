#!/usr/bin/env bash
# Informe LOONA 10:00 y 23:00 América/Monterrey.
# No imprime secrets. No abre Finder (eso es humano).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$HOME/Desktop/Projects/LOONA"
VAULT="$DEST/vault"
INF="$DEST/informes"
TZN="America/Monterrey"
DAY="$(TZ=$TZN date +%Y-%m-%d)"
HM="$(TZ=$TZN date +%H%M)"
STAMP="$(TZ=$TZN date +%Y-%m-%dT%H:%M:%S%z)"
SLOT="noche"
H="$(TZ=$TZN date +%H)"
if [ "$H" -lt 16 ]; then SLOT="manana"; fi

mkdir -p "$INF" "$VAULT/log" "$VAULT/ops" "$DEST/ops"
OUT="$INF/${DAY}-${HM}-${SLOT}.md"
LATEST="$DEST/INFORME-ULTIMO.md"

HEALTH="DOWN"
if curl -fsS -m 3 http://127.0.0.1:8766/api/health >/dev/null 2>&1; then
  HEALTH="UP"
else
  if [ -x "$ROOT/scripts/loona-up.sh" ]; then
    LOONA_SKIP_PIP=1 "$ROOT/scripts/loona-up.sh" >/dev/null 2>&1 || true
    sleep 2
    curl -fsS -m 3 http://127.0.0.1:8766/api/health >/dev/null 2>&1 && HEALTH="UP (restarted)" || HEALTH="DOWN"
  fi
fi

BRAND_N=$(find "$ROOT/brand" -type f ! -name '.DS_Store' 2>/dev/null | wc -l | tr -d ' ')
DOCS_N=$(find "$ROOT/docs" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
SHOTS=$(ls -1 "$ROOT/refs/product"/*.png 2>/dev/null | wc -l | tr -d ' ')
HIGGS="$(higgsfield account status 2>/dev/null | head -1 || echo 'higgsfield n/d')"
PEND="$ROOT/docs/PENDIENTES.md"
[ -f "$PEND" ] || PEND="$ROOT/docs/ops/PLAN-DE-ACCION.md"

{
  echo "# Informe LOONA · $DAY $SLOT"
  echo
  echo "- **Cuando:** $STAMP"
  echo "- **Quién corre:** LaunchAgent \`com.loona.informe\` (10:00 y 23:00 MTY)"
  echo "- **Runtime:** $HEALTH · http://127.0.0.1:8766"
  echo "- **Higgsfield:** $HIGGS"
  echo "- **Brand files:** $BRAND_N · **docs md:** $DOCS_N · **product png:** $SHOTS"
  echo
  echo "## Qué sigue / falta"
  echo
  if [ -f "$PEND" ]; then
    sed -n '1,40p' "$PEND"
  else
    echo "(sin PENDIENTES.md)"
  fi
  echo
  echo "## Quién hizo qué"
  echo
  if [ -f "$ROOT/docs/QUIEN_HIZO_QUE.md" ]; then
    sed -n '1,25p' "$ROOT/docs/QUIEN_HIZO_QUE.md"
  fi
  echo
  echo "## Tokens / tiempo (ledger)"
  echo
  if [ -f "$ROOT/docs/ops/TIEMPO-Y-TOKENS.md" ]; then
    echo "Ver [[TIEMPO-Y-TOKENS]] — el script no inventa un número nuevo de tokens."
  fi
  echo
  echo "## Heartbeat"
  echo
  echo "- informe $STAMP slot=$SLOT health=$HEALTH"
} >"$OUT"

cp "$OUT" "$LATEST"
cp "$OUT" "$VAULT/log/${DAY}-${SLOT}.md"

# sync casa iCloud (sin .env)
if [ -x "$ROOT/scripts/loona-sync-icloud.sh" ]; then
  "$ROOT/scripts/loona-sync-icloud.sh" >/dev/null 2>&1 || true
fi

# copiar ops canónicos a la raíz iCloud para Finder
for f in INVESTIGACIONES PLAN-DE-ACCION RESULTADOS TIEMPO-Y-TOKENS; do
  [ -f "$ROOT/docs/ops/${f}.md" ] && cp "$ROOT/docs/ops/${f}.md" "$DEST/ops/${f}.md"
  [ -f "$ROOT/docs/ops/${f}.md" ] && cp "$ROOT/docs/ops/${f}.md" "$VAULT/ops/${f}.md"
done
[ -f "$ROOT/docs/QUIEN_HIZO_QUE.md" ] && cp "$ROOT/docs/QUIEN_HIZO_QUE.md" "$DEST/ops/QUIEN-HIZO-QUE.md"
[ -f "$ROOT/docs/PENDIENTES.md" ] && cp "$ROOT/docs/PENDIENTES.md" "$DEST/ops/QUE-FALTA.md"

echo "$OUT"
