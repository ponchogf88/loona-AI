#!/usr/bin/env bash
# Install LaunchAgent that restores Claude Code to Anthropic when quota resets.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.loona.claude-backend.plist"
chmod +x "$ROOT/scripts/loona-claude-backend.sh"
mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/runtime/logs"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.loona.claude-backend</string>
  <key>ProgramArguments</key>
  <array>
    <string>$ROOT/scripts/loona-claude-backend.sh</string>
    <string>tick</string>
  </array>
  <key>StartInterval</key><integer>900</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$ROOT/runtime/logs/claude-backend.out.log</string>
  <key>StandardErrorPath</key><string>$ROOT/runtime/logs/claude-backend.err.log</string>
</dict>
</plist>
EOF
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "com.loona.claude-backend → tick cada 15 min; al pasar restore_at vuelve a Claude"
