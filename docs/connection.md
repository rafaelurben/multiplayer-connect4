# Connection flow

At first, there is only one mode.

## Default mode

As soon as two clients are "waiting", a new game is created and assigned.

- Client 1 (c1) connects to server via socket
- Server accepts connection and sends c1 "waiting"
- Client 2 (c2) connects to server via socket
- Server accepts connection and sends c2 "waiting"
- Server creates game

### Game creation

- Server creates a new game instance
- Server broadcasts new game instance to all spectators
- Server tells c1 and c2 their new game id
- Server tells c1 to begin

### In game

- Server sends game ID, [current board](#data-board) and client's color to client
- Client answers with its turn (number between 0 and 6)
- Server validates turn
- Server broadcasts new board and newest turn to all spectators viewing
- (repeat for next player)

## Data Transmission

Via JSON: 

```json
{"action": "ACTION", "key1": "VALUE1", "KEY2": "VALUE2"}
```

### Data Board

A string with 6 rows

```js
"0000000\n0000000\n0000000\n0000000\n0010000\n0120200"
```
