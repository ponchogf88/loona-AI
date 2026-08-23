#!/usr/bin/env bash
# LOONA — levanta el control plane FastAPI en 127.0.0.1:8766
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/runtime"
VENV_DIR="$RUNTIME_DIR/.venv"
LOG_DIR="$RUNTIME_DIR/logs"
PID_FILE="$RUNTIME_DIR/.pid"
HOST="127.0.0.1"
PORT="8766"

mkdir -p "$LOG_DIR"

if [ ! -d "$VENV_DIR" ]; then
  echo "[loona-up] creando venv en $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

if [ "${LOONA_SKIP_PIP:-}" != "1" ]; then
  echo "[loona-up] instalando dependencias"
  "$VENV_DIR/bin/python" -m pip install --quiet --upgrade pip
  "$VENV_DIR/bin/python" -m pip install --quiet -r "$RUNTIME_DIR/requirements.txt"
fi

if curl -fsS -m 1 "http://$HOST:$PORT/api/health" >/dev/null 2>&1; then
  echo "[loona-up] ya viva en http://$HOST:$PORT"
  exit 0
fi

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "[loona-up] pid viejo, reiniciando"
  kill "$(cat "$PID_FILE")" 2>/dev/null || true
  sleep 1
fi

cd "$RUNTIME_DIR"
if [ -f "$RUNTIME_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$RUNTIME_DIR/.env"
  set +a
fi
nohup "$VENV_DIR/bin/python" -m uvicorn app:app --host "$HOST" --port "$PORT" \
  > "$LOG_DIR/server.log" 2>&1 &
echo $! > "$PID_FILE"

sleep 1
if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "[loona-up] LOONA runtime arriba en http://$HOST:$PORT (PID $(cat "$PID_FILE"))"
  echo "[loona-up] logs: $LOG_DIR/server.log"
else
  echo "[loona-up] ERROR: el proceso no arrancó, revisa $LOG_DIR/server.log" >&2
  exit 1
fi
