# Action list

Format: `{"action": "<ACTION>", "arg1": "val1", "arg2": "val2"}`

## From Server to Client

- connected
- room_left
- alert

### Server => Player

- name_rejected
- game_joined
- game_result
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

- ready
- turn
