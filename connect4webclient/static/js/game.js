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

        this.__public_url = undefined;
    }

    get state() {
        return this.__state;
    }

    set state(value) {
        this.__state = value;
        this.updateUi();
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
        let isReady = !this.state.startsWith('ended');
        $readyBtn.attr('disabled', isReady);
        $readyBtn.toggleClass("btn-success", !isReady);
        $readyBtn.toggleClass("btn-danger", isReady);
        $readyBtn.text(isReady ? "Ready" : "Press to be ready");

        let $resultText = $("#player-result");
        $resultText.text(this.result === "won" ? "You won!" : this.result === "lost" ? "You lost!!" : this.result === "tie" ? "It's a tie!" : "Game cancelled!");
    }

    renderGameBoard() {
        let tableRows = this.getRenderedBoardTableRows();
        let $tbody = $("#player-board-table tbody");
        $tbody.children().remove('tr.board-row');
        $tbody.append(...tableRows);

        if (this.state === "ingame_turn") {
            $(".player-turn-btn").attr('disabled', false);
            // $(".player-turn-btn").forEach(btn => btn);
            // todo: disable correct btns
        } else {
            $(".player-turn-btn").attr('disabled', true);
        }
    }

    getRenderedBoardTableRows() {
        let rows = [];
        this.game_board.trim().split("\n").forEach(boardRow => {
            let $tr = $('<tr>', {class: "board-row"});
            for (const c of boardRow) {
                let $td = $("<td>", {class: "board-cell"});
                $td.append($('<div>', {class: `board-coin t${c}-bg`}));
                $tr.append($td);
            }
            rows.push($tr);
        })
        return rows;
    }
}
