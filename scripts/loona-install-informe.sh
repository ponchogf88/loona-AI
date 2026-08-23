#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.loona.informe.plist"
chmod +x "$ROOT/scripts/loona-informe.sh"
mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/runtime/logs"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.loona.informe</string>
  <key>ProgramArguments</key>
  <array>
    <string>$ROOT/scripts/loona-informe.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict>
      <key>Hour</key><integer>10</integer>
      <key>Minute</key><integer>0</integer>
    </dict>
    <dict>
      <key>Hour</key><integer>23</integer>
      <key>Minute</key><integer>0</integer>
    </dict>
  </array>
  <key>StandardOutPath</key><string>$ROOT/runtime/logs/informe.out.log</string>
  <key>StandardErrorPath</key><string>$ROOT/runtime/logs/informe.err.log</string>
</dict>
</plist>
EOF
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "com.loona.informe → 10:00 y 23:00 hora local (MTY)"
