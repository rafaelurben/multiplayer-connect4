# Action list

Format: `{"action": "<ACTION>", "name": "value"}`

## From Server to Client

- connected
- room_left

### Server => Player

- game_joined
- game_left
- invalid_turn
- turn_request
- turn_accepted

### Server => Spectator

- game_created
- game_state
- game_deleted
- player_joined
- player_left

## From Client to Server

- join_room
- leave_room

### Player => Server

- turn
