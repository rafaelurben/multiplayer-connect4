class Game {
    constructor() {
        this.client = {
            mode: undefined,
            id: undefined,
        }
        this.player = {
            name: undefined,
            id: undefined,
        }
        this.opponent = {
            name: undefined,
            id: undefined
        }
        this.game_id = undefined;
        this.result = "";
        this.__game_board = undefined;

        this.players = {};

        this.__state = undefined;
        this.__ready = false;

        this.__public_url = undefined;
    }

    get state() {
        return this.__state;
    }

    set state(value) {
        this.__state = value;
        this.updateUi();
    }

    get ready() {
        return this.__ready;
    }

    set ready(isReady) {
        this.__ready = isReady;

        let $readyBtn = $("#player-ready-btn");
        $readyBtn.toggleClass("btn-success", !isReady);
        $readyBtn.toggleClass("btn-danger", isReady);
        $readyBtn.html(isReady ? "Ready" : "Press <kbd>r</kbd> when ready");

        $("#player-ready-display").toggleClass("hidden", !isReady);
    }

    get game_board() {
        return this.__game_board;
    }

    set game_board(value) {
        this.__game_board = value;
        this.renderGameBoard();
    }

    get public_url() {
        return this.__public_url;
    }

    set public_url(value) {
        this.__public_url = value;
        if (value !== undefined && value !== null) {
            $("#show_qrcode").removeClass("hidden");
            $("#show_qrcode").attr("disabled", false);
            let apibase = "https://api.qrserver.com/v1/create-qr-code/?format=svg&qzone=1&size=500x500&color=fff&bgcolor=212529&data="
            let url = apibase + encodeURIComponent(this.public_url);
            $("#qrcode_image").attr("src", url);
            $("#qrcode_link").attr("href", this.public_url);
        }
    }

    set auto_matching(value) {
        // Master:
        let $btn = $("#toggle_auto_matching");
        $btn.html(value ? "Disable <u>a</u>uto matching" : "Enable <u>a</u>uto matching");
        $btn.toggleClass("btn-success", !value);
        $btn.toggleClass("btn-danger", value);
        // Player:
        $("#player-waiting-text").text(value ? "Waiting for another player..." : "Waiting for the host to match you with another player...");
    }

    updateUi() {
        $(`.modeblock:not(#mode_${this.client.mode})`).addClass("hidden");
        $(`.modeblock.mode_${this.client.mode}`).removeClass("hidden");
        $(`.stateblock:not(#state_${this.state})`).addClass("hidden");
        $(`.stateblock.state_${this.state}`).removeClass("hidden");

        if (this.client.mode === "connected") {
            $("#header_status").text(`Connected (#${this.client.id})`);
        } else if (this.client.mode === "player") {
            $("#header_status").html(`Playing as <b>${this.player.name}\xa0(#${this.client.id})</b>`);
            this.renderPlayerUI();
        } else if (this.client.mode === "spectator" || this.client.mode === "master") {
            if (this.client.mode === "master") {
                $("#header_status").text(`Hosting (#${this.client.id})`);
            } else {
                $("#header_status").text(`Spectating (#${this.client.id})`);
            }

            this.renderSpectatorLobby();
        }
    }

    renderPlayerUI() {
        $("#player-opponent").text(`${this.opponent.name} (${this.opponent.id})`);

        let $readyBtn = $("#player-ready-btn");
        $readyBtn.attr('disabled', this.state.startsWith("ingame"));

        let $resultText = $("#player-result");
        $resultText.text(this.result === "won" ? "You won!" : this.result === "lost" ? "You lost!" : this.result === "tie" ? "It's a tie!" : "Game cancelled!");
    }

    renderSpectatorLobby() {
        let kickplayerelem = $("#kick_player");
        let playerlistelem = $("#playerlist");
        playerlistelem.empty();
        for (let player of Object.values(this.players)) {
            // Create a new player element if it doesn't exist
            let playerelem = $(`<div id="playerlist_player${player.id}" class="playerlist_player rounded-3">
                <i>(${player.id})</i> ${player.name}
            </div>`);
            playerlistelem.append(playerelem);

            playerelem.off('dragover');
            playerelem.off('dragleave');
            playerelem.off('drop');
            if (this.client.mode === "master") {
                playerelem.on('dragover', (e) => {
                    e.preventDefault();
                    e.currentTarget.classList.add("dragover");
                });
                playerelem.on('dragleave', (e) => {
                    e.preventDefault();
                    e.currentTarget.classList.remove("dragover");
                });
                playerelem.on('drop', (e) => {
                    e.preventDefault();
                    e.currentTarget.classList.remove("dragover");
                    let draggedPlayerId = e.originalEvent.dataTransfer.getData("playerId");
                    let droppedPlayerId = player.id;
                    window.sock.action("match_players", {p1id: draggedPlayerId, p2id: droppedPlayerId})
                });
            }

            if (this.client.mode === "master") {
                playerelem.attr("draggable", "true");
                playerelem.on('dragstart', (e) => {
                    e.originalEvent.dataTransfer.setData("playerId", player.id);
                    kickplayerelem.attr('class', 'btn btn-outline-danger');
                });
                playerelem.on('dragend', (e) => {
                    kickplayerelem.attr('class', 'd-none');
                });
            }
        }

        kickplayerelem.off('dragover');
        kickplayerelem.off('dragleave');
        kickplayerelem.off('drop');
        if (this.client.mode === "master") {
            kickplayerelem.on('dragover', (e) => {
                e.preventDefault();
                kickplayerelem.attr('class', 'btn btn-danger');
            });
            kickplayerelem.on('dragleave', (e) => {
                e.preventDefault();
                kickplayerelem.attr('class', 'btn btn-outline-danger');
            });
            kickplayerelem.on('drop', (e) => {
                e.preventDefault();
                kickplayerelem.attr('class', 'd-none');
                let playerid = e.originalEvent.dataTransfer.getData("playerId");
                window.sock.action("kick_player", { pid: playerid })
            });
        }
    }


    renderGameBoard() {
        $(".player-turn-btn").attr('disabled', true);

        let $table = $("#player-board-table");
        $table.children().remove('.board-cell');
        $table.append(...this.getRenderedBoardCells());
    }

    getRenderedBoardCells() {
        let canPlay = this.client.mode === "player" && this.state === "ingame_turn";

        let resultCells = [];
        let boardRows = this.game_board.trim().split("\n");

        // Keep track of whether a column has already had a coin in it
        let colsHaveCoins = new Array(boardRows[0].length).fill(false);

        // Loop through the board rows in reverse order (start from bottom to find first empty cell)
        for (let rowIndex = boardRows.length - 1; rowIndex >= 0; rowIndex--) {
            let boardRow = boardRows[rowIndex].trim();

            for (let colIndex = boardRow.length - 1; colIndex >= 0; colIndex--) {
                let teamNum = boardRow[colIndex];

                let $cell = $("<td>", {class: "board-cell"});
                let $coin = $('<div>', {class: `board-coin t${teamNum}-bg`});

                if (canPlay && teamNum === "0") {
                    if (!colsHaveCoins[colIndex]) {
                        $coin.addClass('board-coin-clickable');
                        $cell.on('click', () => {sock.turn(colIndex)});
                        colsHaveCoins[colIndex] = true;

                        // enable corresponding column button
                        $(`.player-turn-btn[data-col="${colIndex}"]`).prop('disabled', false);
                    }
                }

                $cell.append($coin);
                resultCells.unshift($cell);
            }
        }
        return resultCells;
    }
}
