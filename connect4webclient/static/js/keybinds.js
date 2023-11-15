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
            $("#show_qrcode").click();
        } else if (event.key === "r") {
            $("#player-ready-btn").click();
        } else if (event.key === "1") {
            $('.player-turn-btn[data-col="0"]').click()
        } else if (event.key === "2") {
            $('.player-turn-btn[data-col="1"]').click()
        } else if (event.key === "3") {
            $('.player-turn-btn[data-col="2"]').click()
        } else if (event.key === "4") {
            $('.player-turn-btn[data-col="3"]').click()
        } else if (event.key === "5") {
            $('.player-turn-btn[data-col="4"]').click()
        } else if (event.key === "6") {
            $('.player-turn-btn[data-col="5"]').click()
        } else if (event.key === "7") {
            $('.player-turn-btn[data-col="6"]').click()
        } else {
            return;
        }

        event.preventDefault();
    });
}