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
        }
    }

    renderPlayerUI() {
        $("#player-opponent").text(`${this.opponent.name} (${this.opponent.id})`);

        let $readyBtn = $("#player-ready-btn");
        $readyBtn.attr('disabled', this.state.startsWith("ingame"));

        let $resultText = $("#player-result");
        $resultText.text(this.result === "won" ? "You won!" : this.result === "lost" ? "You lost!" : this.result === "tie" ? "It's a tie!" : "Game cancelled!");
    }

    renderGameBoard() {
        $(".player-turn-btn").attr('disabled', true);

        let tableRows = this.getRenderedBoardTableRows();
        let $tbody = $("#player-board-table tbody");
        $tbody.children().remove('tr.board-row');
        $tbody.append(...tableRows);
    }

    getRenderedBoardTableRows() {
        let canPlay = this.client.mode === "player" && this.state === "ingame_turn";

        let resultRows = [];
        let boardRows = this.game_board.trim().split("\n");

        // Keep track of whether a column has already had a coin in it
        let colsHaveCoins = new Array(boardRows[0].length).fill(false);

        // Loop through the board rows in reverse order (start from bottom to find first empty cell)
        for (let rowIndex = boardRows.length - 1; rowIndex >= 0; rowIndex--) {
            let boardRow = boardRows[rowIndex].trim();

            let $tr = $('<tr>', {class: "board-row"});
            for (let colIndex = 0; colIndex < boardRow.length; colIndex++) {
                let teamNum = boardRow[colIndex];

                let $td = $("<td>", {class: "board-cell"});
                let $coin = $('<div>', {class: `board-coin t${teamNum}-bg`});

                if (canPlay && teamNum === "0") {
                    if (!colsHaveCoins[colIndex]) {
                        $coin.addClass('board-coin-clickable');
                        $td.on('click', () => {sock.turn(colIndex)});
                        colsHaveCoins[colIndex] = true;

                        // enable corresponding column button
                        $(`.player-turn-btn[data-col="${colIndex}"]`).prop('disabled', false);
                    }
                }

                $td.append($coin);
                $tr.append($td);
            }
            resultRows.unshift($tr);
        }
        return resultRows;
    }
}
