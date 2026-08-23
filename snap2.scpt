tell application "Google Chrome"
    tell active tab of front window
        execute javascript "if(document.querySelector('.crew button')) document.querySelector('.crew button').classList.add('on');"
        delay 1
    end tell
end tell
