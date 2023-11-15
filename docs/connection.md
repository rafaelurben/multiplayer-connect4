# Connection flow

## Player flow

- Client 1 (c1) connects to server via websocket
- Server confirms (`connected`)
- Server broadcasts new player to every spectator (`player_joined`)
- Client 1 (c1) sends `join_room {mode: player, name: ...}` to tell the server they want to play
- Server confirms (`room_joined`) or rejects (`name_rejected`)
- Client 1 (c1) sends `ready`
- Same for Client 2 (c2)
- → [Game creation]([#game-creation)

### Game creation

In default mode (currently the only one), the server waits for two players to be ready, then creates a new game instance.

- Server creates a new game instance
- Server broadcasts new game instance to every joined player (`game_created`)
- Server tells c1 and c2 their new game id (`game_joined`)
- → [In game](#in-game)

### In game

- Server sends game ID and [current board](#data-board) to client (`turn_request`)
- Client answers with their column (number between 0 and 6) (`turn`)
- Server validates turn or rejects it (`turn_accepted` or `invalid_turn`)
- Server broadcasts new board to every spectator (`game_state`)
- If end of game is detected: [Game end](#game-end)
- Else: (repeat for next player)

### Game end

- Server tells c1 and c2 their result (`game_result`)
- Server tells c1 and c2 they left the game (`game_left`)
- Server broadcasts game deletion to every spectator (`game_deleted`)

## Data Transmission

Via JSON: 

```json
{"action": "ACTION", "key1": "VALUE1", "KEY2": "VALUE2"}
```

### Data Board

A string with 6 rows. For players, 1 is always the player that receives the data.

```js
"0000000\n0000000\n0000000\n0000000\n0010000\n0120200"
```
