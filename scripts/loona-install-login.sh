#!/usr/bin/env bash
# Instala LaunchAgent: el cerebro de LOONA queda 24/7 desde el login.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.loona.runtime"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key><false/>
  </dict>
  <key>WorkingDirectory</key><string>${ROOT}/runtime</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${ROOT}/scripts/loona-up.sh</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>LOONA_SKIP_PIP</key><string>1</string>
    <key>PATH</key><string>/usr/local/bin:/usr/bin:/bin:${HOME}/.local/bin</string>
  </dict>
  <key>StandardOutPath</key><string>${ROOT}/runtime/logs/launchd.out.log</string>
  <key>StandardErrorPath</key><string>${ROOT}/runtime/logs/launchd.err.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "[loona] 24/7 instalado: $PLIST"
echo "[loona] El servidor vive al encender el iMac."
echo "[loona] La ventana se abre con ~/Applications/LOONA.app"
