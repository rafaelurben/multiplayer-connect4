class GameSocket {
    constructor(game) {
        this.socket = undefined;
        this.wsid = undefined;
        this.game = game;

        this.connect();
    }

    connect() {
        let prot = location.protocol === "http:" ? "ws://" : "wss://";
        
        let newthis = this; // Ugly hack to get around the fact that "this" is not the same in the callback
        let newsock = new WebSocket(prot + location.host + "/ws");

        newsock.onopen = function (event) {
            console.log("[WS] Connection established!");
            newthis.game.updateUi();
        };

        newsock.onmessage = function (event) {
            let json = JSON.parse(event.data);
            console.debug("[WS] Data received:", json);
            newthis.onreceive(json);
        };

        newsock.onclose = function (event) {
            if (event.wasClean) {
                console.log(`[WS] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                // e.g. server process killed or network down
                // event.code is usually 1006 in this case
                console.warn('[WS] Connection died! Code:', event, 'Reason:', event.reason);
                alert(`[Error] Connection died! Code: ${event.code} - Reason: ${event.reason}`);
                location.reload();
            }
        };

        newsock.onerror = function (error) {
            console.warn("[WS] Error:", error);
        };

        this.socket = newsock;
    }

    onreceive(json) {
        switch (json.action) {
            case "alert": {
                alert(json.message);
                break;
            }
            case "connected": {
                this.wsid = json.id;
                this.game.client.id = json.id;
                this.game.client.mode = "connected";
                this.game.public_url = json.public_url;
                break;
            }
            case "room_joined": {
                this.game.client.mode = json.mode;
                if (json.mode === "player") {
                    this.game.player = json.player;
                }
                break;
            }
            case "room_left": {
                this.game.client.mode = "connected";
                this.game.player = {};
                break;
            }
            default: {
                console.warn("[WS] Unknown action received:", json);
            }
        }
        this.game.updateUi();
    }

    send(json) {
        this.socket.send(JSON.stringify(json));
        console.debug(`[WS] Sent:`, json);
    }

    joinAsPlayer(name) {
        if (this.game.client.mode !== "connected") {
            console.error("[WS] Already joined!");
            return;
        } else if (name === undefined) {
            name = document.getElementById("nameinput").value;
        }

        if (name === "") {
            alert("Please enter a name!");
            return;
        }

        this.send({"action": "join_room", "mode": "player", "name": name})
    }

    joinAsSpectator() {
        if (this.game.client.mode !== "connected") {
            console.error("[WS] Already joined!");
            return;
        }
        this.send({"action": "join_room", "mode": "spectator"})
    }

    leave() {
        if (this.game.client.mode === "connected") {
            console.error("[WS] Not joined!");
            return;
        }
        if (confirm("Are you sure you want to leave?")) {
            this.send({"action": "leave_room"});
        }
    }

    action(action, data) {
        this.send({"action": action, ...data});
    }
}
