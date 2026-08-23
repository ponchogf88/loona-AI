tell application "Google Chrome"
    activate
    tell active tab of front window
        execute javascript "location.reload(true);"
        delay 2
    end tell
end tell
