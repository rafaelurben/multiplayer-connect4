# Connection flow

Currently, there is only one mode.

## Default mode

- Client 1 (c1) connects to server via websocket
- Server confirms with `{'action': 'connected', 'id': '<ID>'}`
- Client 1 (c1) sends `{'action': 'join_room', 'mode': 'player', 'name': '<NAME>'}` to tell the server they want to play
- Server confirms with `{'action': 'player_joined', 'id': '<ID>'}`
- Same for Client 2 (c2)
- Server sees that enough (2) players are waiting => [Game creation]([#game-creation)

### Game creation

- Server creates a new game instance
- Server broadcasts new game instance to every joined player
- Server tells c1 and c2 their new game id
- Server tells c1 to begin

### In game

- Server sends game ID, [current board](#data-board) and client's color to client
- Client answers with their column (number between 0 and 6)
- Server validates turn
- Server broadcasts new board and newest turn to every joined player
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
