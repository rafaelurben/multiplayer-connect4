# Action list

Format: `{"action": "<ACTION>", "name": "value"}`

## Server =>

- connect
- room_left

### Server => Player

- turn_request

### Server => Spectator

- game_created
- game_state
- game_deleted

## => Server

- join_room
- leave_room

### Player => Server

- turn
