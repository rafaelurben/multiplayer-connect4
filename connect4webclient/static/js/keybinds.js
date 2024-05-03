// Keybinds

function setupKeybinds(socket) {
    document.addEventListener("keydown", function (event) {
        if (event.ctrlKey || event.altKey || event.metaKey) {
            // Ignore keybinds if ctrl/alt/meta is pressed
            return;
        }
        if ($("input").is(":focus")) {
            // Ignore keybinds if input is focused
            return;
        }

        if (event.key === "f") {
            // f: Toggle full screen
            if (document.fullscreenElement === null) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        } else if (event.key === "l") {
            // l: Leave room
            socket.leave();
        } else if (event.key === "q") {
            // q: Show QR code
            $("#show_qrcode:not(:disabled):visible").click();
        } else if (event.key === "r") {
            // r: Ready
            $("#player-ready-btn:not(:disabled):visible").click();
        } else if (event.key === "a") {
            // a: Toggle auto matching
            $("#toggle_auto_matching:not(:disabled):visible").click();
        } else if (event.key === "1") {
            $('.player-turn-btn[data-col="0"]:not(:disabled):visible').click()
        } else if (event.key === "2") {
            $('.player-turn-btn[data-col="1"]:not(:disabled):visible').click()
        } else if (event.key === "3") {
            $('.player-turn-btn[data-col="2"]:not(:disabled):visible').click()
        } else if (event.key === "4") {
            $('.player-turn-btn[data-col="3"]:not(:disabled):visible').click()
        } else if (event.key === "5") {
            $('.player-turn-btn[data-col="4"]:not(:disabled):visible').click()
        } else if (event.key === "6") {
            $('.player-turn-btn[data-col="5"]:not(:disabled):visible').click()
        } else if (event.key === "7") {
            $('.player-turn-btn[data-col="6"]:not(:disabled):visible').click()
        } else {
            return;
        }

        event.preventDefault();
    });
}