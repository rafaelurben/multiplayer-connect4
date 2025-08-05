class GameSocket {
    constructor(game) {
        this.socket = undefined;
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
            case "ping": {
                console.log("[WS] Ping received!")
                return;
            }
            case "alert": {
                alert(json.message);
                return;
            }
            case "connected": {
                this.game.client.id = json.id;
                this.game.client.mode = "connected";
                this.game.public_url = json.public_url;

                if (location.search === "?master") this.joinAsSpectator();
                break;
            }
            case "ready_response": {
                this.game.ready = json.ready;
                break;
            }
            case "room_joined": {
                this.game.client.mode = json.mode;
                this.game.auto_matching = json.auto_matching_enabled;
                if (json.mode === "player") {
                    this.game.player = json.player;
                    this.game.state = "initial_join";
                    this.ready();
                } else {
                    this.game.players = json.players;
                    this.game.games = json.games;
                }
                break;
            }
            case "room_left": {
                this.game.client.mode = "connected";
                this.game.player = {};
                break;
            }
            case "name_rejected": {
                alert("Name rejected! Please try again. There might be a player with the same name already.");
                break;
            }
            case "auto_matching_toggled": {
                this.game.auto_matching = json.enabled;
                break;
            }
            // Player events
            case "game_joined": {
                this.game.opponent = json.opponent;
                this.game.game_id = json.gameid;
                this.game.result = "";
                this.game.state = "ingame_waiting";
                this.game.game_board = json.board;
                this.game.ready = false;
                break;
            }
            case "game_left": {
                this.game.state = "ended";
                break;
            }
            case "game_result": {
                this.game.result = json.state;
                this.game.state = "ended_result"
                this.game.game_board = json.board;
                break;
            }
            case "turn_request": {
                this.game.state = "ingame_turn";
                this.game.game_board = json.board;
                break;
            }
            case "turn_accepted": {
                this.game.state = "ingame_waiting";
                this.game.game_board = json.board;
                break;
            }
            case "invalid_turn": {
                alert("Something went wrong as you were able to submit an invalid turn!");
                break;
            }
            // Spectator events
            case "player_joined": {
                this.game.players[json.id] = json.player;
                break;
            }
            case "player_updated": {
                this.game.players[json.id] = {...this.game.players[json.id], ...json.player};
                break;
            }
            case "player_left": {
                delete this.game.players[json.id];
                break;
            }
            case "game_created": {
                this.game.games[json.id] = json.game;
                break;
            }
            case "game_updated": {
                this.game.games[json.id] = {...this.game.games[json.id], ...json.game};
                if (this.game.watched_game_id === json.game.id) {
                    this.game.renderWatchedGame();
                }
                break;
            }
            case "game_deleted": {
                this.game.games[json.id].is_finished = true;
                if (this.game.watched_game_id === json.game.id) {
                    this.game.renderWatchedGame();
                }
                break;
            }
            // Fallback
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
        this.send({"action": "join_room", "mode": location.search === "?master" ? "master" : "spectator"})
    }

    leave() {
        if (this.game.client.mode === "connected") {
            console.error("[WS] Not joined!");
            return;
        }

        if (this.game.client.mode !== "player" || (this.game.state && (this.game.state === "ready" ||
            this.game.state.startsWith("ended"))) || confirm("Are you sure you want to leave?")) {
            this.send({"action": "leave_room"});
        }
    }

    ready() {
        this.action('ready');
    }

    turn(num) {
        let data = {"column": num, "gameid": this.game.game_id};
        this.action("turn", data);
    }

    action(action, data) {
        this.send({"action": action, ...data});
    }
}
