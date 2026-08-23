#!/usr/bin/env bash
set -euo pipefail
LABEL=com.loona.runtime
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$ROOT/runtime/.pid" ]; then
  kill "$(cat "$ROOT/runtime/.pid")" 2>/dev/null || true
  rm -f "$ROOT/runtime/.pid"
fi
# fallback por si el .pid quedó viejo/perdido pero el proceso sigue vivo
pkill -f "uvicorn app:app --host 127.0.0.1 --port 8766" 2>/dev/null || true
echo "[loona] LaunchAgent y proceso detenidos. La app en ~/Applications/LOONA.app se puede borrar a mano."
