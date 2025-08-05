function renderBoardCells(board, {canPlay = false, spectator = true}) {
    let resultCells = [];
    let boardRows = board.trim().split("\n");

    // Keep track of whether a column has already had a coin in it
    let colsButtonAdded = new Array(boardRows[0].length).fill(false);

    // Loop through the board rows in reverse order (start from bottom to find first empty cell)
    for (let rowIndex = boardRows.length - 1; rowIndex >= 0; rowIndex--) {
        let boardRow = boardRows[rowIndex].trim();

        for (let colIndex = boardRow.length - 1; colIndex >= 0; colIndex--) {
            let playerNum = boardRow[colIndex];

            let $cell = $("<div>", {class: "board-cell"});
            let $coin = $('<div>', {class: `board-coin t${playerNum}-bg`});

            if (canPlay && playerNum === "0") {
                if (!colsButtonAdded[colIndex]) {
                    $coin.addClass('board-coin-clickable');
                    $cell.on('click', () => {
                        sock.turn(colIndex)
                    });
                    colsButtonAdded[colIndex] = true;
                }
            }

            $cell.append($coin);
            resultCells.unshift($cell);
        }
    }

    // Add buttons on top
    if (!spectator) {
        for (let i = colsButtonAdded.length - 1; i >= 0; i--) {
            let disabledAttr = canPlay && colsButtonAdded[i] ? "" : "disabled";
            resultCells.unshift($(`<div class="board-header-cell">
                <button class="player-turn-btn btn btn-sm btn-light" onclick="sock.turn(${i})" data-col="${i}" ${disabledAttr}>↓</button>
            </div>`))
        }
    }
    return resultCells;
}