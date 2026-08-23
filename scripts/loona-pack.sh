#!/usr/bin/env bash
# Zip de venta / testers. Sin .env ni logs ni venv.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/dist"
mkdir -p "$DEST"
STAMP=$(date +%Y%m%d)
ZIP="$DEST/LOONA-v1-$STAMP.zip"
rm -f "$ZIP"
cd "$ROOT/.."
zip -r "$ZIP" loona \
  -x "loona/runtime/.env" \
  -x "loona/runtime/.env.*" \
  -x "loona/runtime/.venv/*" \
  -x "loona/runtime/state/*" \
  -x "loona/runtime/logs/*" \
  -x "loona/runtime/.pid" \
  -x "loona/**/__pycache__/*" \
  -x "loona/dist/*"
echo "[pack] $ZIP"
ls -lh "$ZIP"
