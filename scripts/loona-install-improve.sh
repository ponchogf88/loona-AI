#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.loona.improve.plist"
chmod +x "$ROOT/scripts/loona-improve.sh" "$ROOT/scripts/loona-sync-icloud.sh"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.loona.improve</string>
  <key>ProgramArguments</key>
  <array>
    <string>$ROOT/scripts/loona-improve.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>7</integer>
    <key>Minute</key><integer>10</integer>
  </dict>
  <key>StandardOutPath</key><string>$ROOT/runtime/logs/improve.out.log</string>
  <key>StandardErrorPath</key><string>$ROOT/runtime/logs/improve.err.log</string>
</dict>
</plist>
EOF
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "LaunchAgent com.loona.improve → 07:10 América/Monterrey (reloj local)"
