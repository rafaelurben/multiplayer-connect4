# Action list

Format: `{"action": "<ACTION>", "name": "value"}`

## From Server to Client

- connected
- room_left

### Server => Player

- game_joined
- game_left
- turn_request

### Server => Spectator

- game_created
- game_state
- game_deleted

## From Client to Server

- join_room
- leave_room

### Player => Server

- turn
