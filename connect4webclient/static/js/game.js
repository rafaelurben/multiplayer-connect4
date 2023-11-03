
class Game {
    constructor() {
        this.client = {
            mode: undefined,
            id: undefined,
        }
        this.player = {
            name: undefined,
            team: undefined,
            id: undefined,
        }

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

    handleStateUpdate() {
        this.updateUi();
    }

}
