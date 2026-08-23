#!/usr/bin/env bash
# Abre LOONA como programa (ventana Chrome --app), no como pestaña.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export LOONA_SKIP_PIP="${LOONA_SKIP_PIP:-1}"
"$ROOT/scripts/loona-up.sh"

URL="http://127.0.0.1:8766"
for i in 1 2 3 4 5 6 7 8; do
  if curl -fsS -m 1 "$URL/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.4
done

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ -x "$CHROME" ]; then
  exec "$CHROME" --app="$URL" --new-window
fi
open -a Safari "$URL"
