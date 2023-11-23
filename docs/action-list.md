# Action list

Format: `{"action": "<ACTION>", "arg1": "val1", "arg2": "val2"}`

## From Server to Client

- connected
- room_joined (mode: player/spectator/master)
- room_left
- alert (message)
- ping
- auto_matching_toggled

### Server => Player

- name_rejected
- ready_response
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

### Master => Server

- toggle_auto_matching