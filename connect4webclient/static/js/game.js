
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
        this.game_board = "0000000\n0000000\n0000000\n0000000\n0000000\n0000000\n";

        this.__state = undefined;

        this.public_url = undefined;
    }

    get state() { return this.__state; }
    set state(value) { this.__state = value; this.handleStateUpdate(); }

    updateUi() {
        $(`.modeblock:not(#mode_${this.client.mode})`).addClass("hidden");
        $(`.modeblock.mode_${this.client.mode}`).removeClass("hidden");
        $(`.stateblock:not(#state_${this.state})`).addClass("hidden");
        $(`.stateblock.state_${this.state}`).removeClass("hidden");

        if (this.client.mode === "connected") {
            $("#header_status").text(`Connected (#${this.client.id})`);
        } else
        if (this.client.mode === "player") {
            $("#header_status").text(`Playing as ${this.player.name}\xa0(#${this.client.id})`);
            this.renderPlayerGame();
        } else
        if (this.client.mode === "spectator" || this.client.mode === "master") {
            if (this.client.mode === "master") {
                $("#header_status").text(`Hosting (#${this.client.id})`);
            } else {
                $("#header_status").text(`Spectating (#${this.client.id})`);
            }
        }

        if (this.public_url !== undefined && this.public_url !== null) {
            $("#show_qrcode").removeClass("hidden");
            let apibase = "https://api.qrserver.com/v1/create-qr-code/?format=svg&qzone=1&size=500x500&color=fff&bgcolor=212529&data="
            let url = apibase + encodeURIComponent(this.public_url);
            $("#qrcode_image").attr("src", url);
            $("#qrcode_link").attr("href", this.public_url);
        }
    }

    renderPlayerGame() {
        $("#player-opponent").text(`${this.opponent.name} (${this.opponent.id})`);

        let $readyBtn = $("#player-ready-btn");
        let isReady = !this.state.startsWith('ended');
        $readyBtn.attr('disabled', isReady);
        $readyBtn.toggleClass("btn-success", !isReady);
        $readyBtn.toggleClass("btn-danger", isReady);
        $readyBtn.text(isReady ? "Ready" : "Press to be ready");

        let $resultText = $("#player-result");
        $resultText.text(this.result === "won" ? "You won!" : this.result === "lost" ? "You lost!!" : this.result === "tie" ? "It's a tie!" : "Game cancelled!");

        if (this.state.startsWith("ingame")) {
            let tablerows = this.getRenderedBoardTableRows();
            console.log("tablerows", tablerows);
            let $tbody = $("#board-table");
            $tbody.children().remove('tr.board-row');
            $tbody.append(...tablerows);

            if (this.state === "ingame_turn") {
                $(".player-turn-btn").attr('disabled', false);
                // $(".player-turn-btn").forEach(btn => btn);
                // todo: disable correct btns
            } else {
                $(".player-turn-btn").attr('disabled', true);
            }
        }
    }

    getRenderedBoardTableRows() {
        let rows = [];
        this.game_board.trim().split("\n").forEach(boardRow => {
            console.log(boardRow);
            let $tr = $('<tr>', {class: "board-row"});
            for (const c of boardRow) {
                $tr.append($("<td>", {class: `t${c}-bg`}));
            }
            rows.push($tr);
        })
        return rows;
    }

    handleStateUpdate() {
        this.updateUi();
    }

}
