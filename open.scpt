tell application "Google Chrome"
    activate
    if (count every window) = 0 then
        make new window
    end if
    set URL of active tab of front window to "http://127.0.0.1:8766"
    delay 2
end tell
