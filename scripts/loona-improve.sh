#!/usr/bin/env bash
# Mejora continua LOONA: health, briefing cache, heartbeat al vault.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="$HOME/Desktop/Projects/LOONA/vault"
LOG="$ROOT/runtime/logs/improve.log"
STAMP="$(TZ=America/Monterrey date +%Y-%m-%dT%H:%M:%S%z)"
mkdir -p "$(dirname "$LOG")" "$VAULT/log"

{
  echo "=== $STAMP ==="
  if curl -fsS -m 3 http://127.0.0.1:8766/api/health >/dev/null; then
    echo "health OK"
    curl -fsS -m 20 http://127.0.0.1:8766/api/briefing >/dev/null && echo "briefing warmed" || echo "briefing FAIL"
    curl -fsS -m 8 http://127.0.0.1:8766/api/weather >/dev/null && echo "weather warmed" || echo "weather FAIL"
  else
    echo "runtime down — intentando loona-up"
    LOONA_SKIP_PIP=1 "$ROOT/scripts/loona-up.sh" || true
  fi
} >>"$LOG" 2>&1

NOTE="$VAULT/log/$(TZ=America/Monterrey date +%Y-%m-%d).md"
if [ ! -f "$NOTE" ]; then
  printf '# %s\n\n- heartbeat improve.sh %s\n' "$(TZ=America/Monterrey date +%F)" "$STAMP" >"$NOTE"
else
  echo "- heartbeat improve.sh $STAMP" >>"$NOTE"
fi

# Re-sync docs → vault (no secrets)
if [ -x "$ROOT/scripts/loona-sync-icloud.sh" ]; then
  "$ROOT/scripts/loona-sync-icloud.sh" >>"$LOG" 2>&1 || true
fi
echo "improve done $STAMP" >>"$LOG"
