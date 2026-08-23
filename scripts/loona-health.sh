#!/usr/bin/env bash
# LOONA — chequeo rápido de salud del control plane
set -euo pipefail

HOST="127.0.0.1"
PORT="8766"
URL="http://$HOST:$PORT/api/health"

TMP_BODY="$(mktemp)"
trap 'rm -f "$TMP_BODY"' EXIT

CODE="$(curl -sS -m 5 -o "$TMP_BODY" -w '%{http_code}' "$URL")" || {
  echo "[loona-health] BLOCKED: no se pudo contactar $URL"
  exit 1
}
BODY="$(cat "$TMP_BODY" 2>/dev/null || true)"

if [ "$CODE" = "200" ]; then
  echo "[loona-health] OK ($CODE): $BODY"
  exit 0
else
  echo "[loona-health] BLOCKED ($CODE): $BODY"
  exit 1
fi
