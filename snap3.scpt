tell application "Google Chrome"
    tell active tab of front window
        execute javascript "document.body.classList.add('is-speaking'); if(window.LoonaWorld && window.LoonaWorld.listen) window.LoonaWorld.listen();"
        delay 1
    end tell
end tell
