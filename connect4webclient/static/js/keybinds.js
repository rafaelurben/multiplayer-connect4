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
            event.preventDefault();
            if (document.fullscreenElement === null) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        } else if (event.key === "l") {
            // l: Leave room
            event.preventDefault();
            socket.leave();
        } else if (event.key === "q") {
            // q: Show QR code
            event.preventDefault();
            $("#show_qrcode").click();
        }
    });
}