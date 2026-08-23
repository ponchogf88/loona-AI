#!/usr/bin/env bash
# Route LOONA's Claude Code (cwd /Users/imac/loona) through DeepSeek
# while Anthropic weekly quota is exhausted, then restore Claude.
#
#   bash scripts/loona-claude-backend.sh on [RESTORE_ISO]
#   bash scripts/loona-claude-backend.sh off
#   bash scripts/loona-claude-backend.sh tick
#   bash scripts/loona-claude-backend.sh status
#
# Never prints API keys. Token is read from runtime/.env (DEEPSEEK_API_KEY)
# and written only to .claude/settings.local.json (chmod 600).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETTINGS="$ROOT/.claude/settings.local.json"
STATE="$ROOT/runtime/state/claude-backend.json"
ENV_FILE="$ROOT/runtime/.env"
LOG="$ROOT/runtime/logs/claude-backend.log"
CMD="${1:-status}"
RESTORE_ARG="${2:-}"

mkdir -p "$ROOT/.claude" "$ROOT/runtime/state" "$ROOT/runtime/logs"

log() {
  TZ=America/Monterrey date "+%Y-%m-%dT%H:%M:%S%z $*" >>"$LOG"
}

deepseek_key() {
  python3 - <<'PY'
from pathlib import Path
p = Path("/Users/imac/loona/runtime/.env")
if not p.exists():
    raise SystemExit(1)
for raw in p.read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    if k.strip() == "DEEPSEEK_API_KEY":
        val = v.strip().strip('"').strip("'")
        if val:
            print(val)
            raise SystemExit(0)
raise SystemExit(1)
PY
}

default_restore_iso() {
  python3 - <<'PY'
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
pt = ZoneInfo("America/Los_Angeles")
now = datetime.now(pt)
# Claude Code pane said this cycle resets 2026-08-15 11:00 (PT). Weekly +7d after that.
target = datetime(2026, 8, 15, 11, 0, tzinfo=pt)
while now >= target:
    target += timedelta(days=7)
print(target.isoformat())
PY
}

merge_env() {
  local mode="$1"  # on|off
  DEEPSEEK_API_KEY=""
  if [[ "$mode" == "on" ]]; then
    DEEPSEEK_API_KEY="$(deepseek_key)" || {
      echo "NEED_HUMAN: falta DEEPSEEK_API_KEY en runtime/.env"
      exit 2
    }
  fi
  MODE="$mode" KEY="$DEEPSEEK_API_KEY" SETTINGS="$SETTINGS" python3 - <<'PY'
import json, os
from pathlib import Path

path = Path(os.environ["SETTINGS"])
mode = os.environ["MODE"]
data = {}
if path.exists() and path.stat().st_size:
    data = json.loads(path.read_text(encoding="utf-8"))
env = dict(data.get("env") or {})
managed = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL",
    "CLAUDE_CODE_EFFORT_LEVEL",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW",
]
if mode == "on":
    key = os.environ["KEY"]
    env.update({
        "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
        "ANTHROPIC_AUTH_TOKEN": key,
        "ANTHROPIC_MODEL": "deepseek-v4-pro[1m]",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro[1m]",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro[1m]",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
        "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-flash",
        "CLAUDE_CODE_EFFORT_LEVEL": "max",
        "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "786432",
    })
    data["env"] = env
else:
    for k in managed:
        env.pop(k, None)
    if env:
        data["env"] = env
    else:
        data.pop("env", None)
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
os.chmod(path, 0o600)
print(path)
PY
}

write_state() {
  local backend="$1" restore="$2"
  BACKEND="$backend" RESTORE="$restore" STATE="$STATE" python3 - <<'PY'
import json, os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
path = Path(os.environ["STATE"])
payload = {
    "backend": os.environ["BACKEND"],
    "restore_at": os.environ["RESTORE"] or None,
    "updated": datetime.now(ZoneInfo("America/Monterrey")).isoformat(),
    "scope": "loona .claude/settings.local.json (solo cwd /Users/imac/loona)",
}
path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(path)
PY
}

should_restore() {
  python3 - <<'PY'
import json, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
p = Path("/Users/imac/loona/runtime/state/claude-backend.json")
if not p.exists():
    raise SystemExit(1)
data = json.loads(p.read_text(encoding="utf-8"))
if data.get("backend") != "deepseek":
    raise SystemExit(1)
iso = data.get("restore_at")
if not iso:
    raise SystemExit(1)
restore = datetime.fromisoformat(iso)
now = datetime.now(restore.tzinfo or ZoneInfo("America/Los_Angeles"))
raise SystemExit(0 if now >= restore else 1)
PY
}

probe_deepseek() {
  local key
  key="$(deepseek_key)" || return 2
  local code
  code="$(
    curl -sS -m 25 -o /tmp/loona-ds-probe.json -w '%{http_code}' \
      https://api.deepseek.com/anthropic/v1/messages \
      -H "x-api-key: ${key}" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{"model":"deepseek-v4-flash","max_tokens":8,"messages":[{"role":"user","content":"di ok"}]}'
  )" || code="000"
  python3 - <<'PY'
import json
from pathlib import Path
p = Path("/tmp/loona-ds-probe.json")
model = "?"
if p.exists():
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        model = data.get("model") or (data.get("error") or {}).get("type") or data.get("type") or "?"
    except Exception:
        model = "unreadable"
print(model)
PY
  rm -f /tmp/loona-ds-probe.json
  echo "$code"
}

case "$CMD" in
  on)
    restore="${RESTORE_ARG:-$(default_restore_iso)}"
    merge_env on >/dev/null
    write_state deepseek "$restore" >/dev/null
    log "backend=deepseek restore_at=$restore"
    probe="$(probe_deepseek)"
    http="${probe##*$'\n'}"
    model="${probe%%$'\n'*}"
    echo "DONE backend=deepseek restore_at=$restore probe_http=$http model=$model"
    echo "Claude wB:p2 toma esto al REINICIAR (settings de proyecto). No pegué keys."
    ;;
  off)
    merge_env off >/dev/null
    write_state anthropic "" >/dev/null
    log "backend=anthropic (quota restored / manual off)"
    echo "DONE backend=anthropic — Claude Code vuelve a la cuota Anthropic al reiniciar wB:p2."
    ;;
  tick)
    if should_restore; then
      "$0" off
    else
      echo "KEEP backend still deepseek (restore not due)"
    fi
    ;;
  status)
    if [[ -f "$STATE" ]]; then
      python3 - <<'PY'
import json
from pathlib import Path
print(Path("/Users/imac/loona/runtime/state/claude-backend.json").read_text())
PY
    else
      echo "no state — backend unset (Claude nativo)"
    fi
    if python3 - <<'PY'
import json
from pathlib import Path
p = Path("/Users/imac/loona/.claude/settings.local.json")
if not p.exists():
    raise SystemExit(1)
env = (json.loads(p.read_text()) or {}).get("env") or {}
url = env.get("ANTHROPIC_BASE_URL", "")
print("settings_base_url=" + (url or "(unset)"))
print("token_set=" + ("yes" if env.get("ANTHROPIC_AUTH_TOKEN") else "no"))
PY
    then :; fi
    ;;
  *)
    echo "uso: $0 on [RESTORE_ISO] | off | tick | status"
    exit 1
    ;;
esac
