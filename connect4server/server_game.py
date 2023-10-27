import logging
import asyncio
from aiohttp import web

from connect4server.server_base import BasicServer
from connect4server.player import Player
from connect4server.game import Game

log = logging.getLogger()


class GameServer(BasicServer):
    """Game server"""

    def __init__(self, clientdir, public_url=None) -> None:
        self.clientdir = clientdir
        self.public_url = public_url

        self.spectator_ids = []
        self.master_id = None

        super().__init__()

    async def create_games(self):
        """
        Called after a player joins or a game ends.
        Creates new games if there are 2 or more players waiting.
        """

        print("[Game] Trying to create games!")

        players = list(filter(lambda p: not p.is_in_game(), Player.everyone.values()))
        while len(players) >= 2:
            p1: Player = players.pop()
            p2: Player = players.pop()
            game = Game(p1, p2)

            log.debug(f"[Game] Created game {game.id}")

            await self.send_to_spectators(
                {"action": "game_created", "gameid": game.id, "p1": p1.as_dict(), "p2": p2.as_dict()})
            await self.send_to_spectators(
                {"action": "game_state", "gameid": game.id, "board": game.p1board(), "next": game.next_player})

            await self.send_to_one(
                {"action": "game_joined", "gameid": game.id, "opponent": p2.as_dict()}, p1.id)
            await self.send_to_one(
                {"action": "game_joined", "gameid": game.id, "opponent": p1.as_dict()}, p2.id)

            await self.send_to_one(
                {"action": "turn_request", "gameid": game.id, "board": game.p1board()},
                p1.id)

    async def delete_game(self, game: Game):
        """Called after a player disconnects or a game ends"""

        log.debug(f"[Game] Deleting game {game.id}")
        game.delete()

        await self.send_to_ids(
            {"action": "game_left", "gameid": game.id}, [game.p1.id, game.p2.id])
        await self.send_to_spectators(
            {"action": "game_deleted", "gameid": game.id})

        await self.create_games()

    # Websocket actions

    async def send_to_spectators(self, data):
        """Send data to all spectators"""

        await self.send_to_ids(data, ids=self.spectator_ids)

    async def send_to_joined(self, data):
        """Send data to all clients who joined the game as player or spectator"""

        joined_ids = set(Player.everyone) | set(self.spectator_ids)
        await self.send_to_ids(data, ids=joined_ids)

    async def send_to_unjoined(self, data):
        """Send data to all clients who are neither player nor spectator"""

        unjoined_ids = set(self.websockets) - set(Player.everyone) - set(self.spectator_ids)
        await self.send_to_ids(data, ids=unjoined_ids)

    # Websocket handlers

    async def handle_action_from_player(self, action, data, ws, wsid):
        """Handle action sent from a joined player"""

        if action == 'leave_room':
            log.info('[WS] #%s left the room! ("%s")',
                     wsid, Player.everyone[wsid].name)
            del Player.everyone[wsid]
            await self.send_to_joined({'action': 'player_left', 'id': wsid})
            return await ws.send_json({'action': 'room_left'})
        elif action == 'turn':
            player = Player.everyone[wsid]
            try:
                gameid = int(data.get("gameid"))
                col = int(data.get("column"))
            except ValueError:
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'not an integer'})

            if player.gameid != gameid:
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'not your game'})
            game = Game.games[gameid]

            if wsid == game.p1.id:
                pnum = 1
            elif wsid == game.p2.id:
                pnum = 2
            else:
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'player not found'})

            if not game.validate_turn(pnum, col):
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'turn not valid'})

            game.make_turn(pnum, col)

            thisboard = game.p1board() if pnum == 1 else game.p2board()
            otherboard = game.p2board() if pnum == 1 else game.p1board()

            await self.send_to_one(
                {"action": "turn_accepted", "board": thisboard},
                wsid)
            await self.send_to_spectators(
                {"action": "game_state", "gameid": game.id, "board": game.p1board(), "next": game.next_player})

            if game.check_for_end():
                await self.send_to_spectators(
                    {"action": "game_ended", "gameid": game.id, "winning_nr": game.winning_nr,
                     "winning_name": game.winning_name}
                )
                await self.delete_game(game)

            await self.send_to_one(
                {"action": "turn_request", "gameid": game.id, "board": otherboard},
                game.p2.id if pnum == 1 else game.p1.id)
            return True

        return False

    async def handle_action_from_master(self, action, data, ws, wsid):
        """Handle action sent from master"""

        if action == 'leave_room':
            self.spectator_ids.remove(wsid)
            self.master_id = None
            log.info(
                '[WS] #%s: The game master left the room! The next spectator '
                'will become the new game master!', wsid)
            return await ws.send_json({'action': 'room_left'})

        # TODO: Add actions like kick player etc.

        return False

    async def handle_action_from_spectator(self, action, data, ws, wsid):
        """Handle action sent from spectators (except master)"""

        if action == 'leave_room':
            self.spectator_ids.remove(wsid)
            log.info('[WS] #%s stopped spectating!', wsid)
            return await ws.send_json({'action': 'room_left'})
        return False

    async def handle_action_from_unjoined(self, action, data, ws, wsid):
        """Handle action sent from a player that hasn't joined yet"""

        if action == 'join_room':  # join the lobby as player or spectator
            mode = data['mode']

            if mode == 'player':
                name = data['name']
                if not Player.name_check(name):
                    return await ws.send_json({'action': 'alert',
                                               'message': 'Invalid name! Only alphanumeric characters, spaces, '
                                                          'underscores and dashes are allowed. (min 3, '
                                                          'max 20 characters)'})

                player = Player(name, wsid)
                log.info('[WS] #%s joined as player "%s"', wsid, name)
                await self.send_to_spectators({'action': 'player_joined', 'id': wsid, 'player': player.as_dict()})
                await self.create_games()
            else:
                self.spectator_ids.append(wsid)
                log.info('[WS] #%s started spectating!', wsid)
                if self.master_id is None:
                    self.master_id = wsid
                    log.info('[WS] #%s is now the game master!', wsid)

            return True
        return False

    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

        await super().handle_message_json(data, ws, wsid)

        action = data.pop('action', None)

        if action == 'message':
            return await self.send_to_all({'action': 'message', 'from_id': wsid, 'message': data['message']})

        if wsid in Player.everyone:
            if await self.handle_action_from_player(action, data, ws, wsid) is not False:
                return
        elif wsid == self.master_id:
            if await self.handle_action_from_master(action, data, ws, wsid) is not False:
                return
        elif wsid in self.spectator_ids:
            if await self.handle_action_from_spectator(action, data, ws, wsid) is not False:
                return
        else:
            if await self.handle_action_from_unjoined(action, data, ws, wsid) is not False:
                return

        await ws.send_json({'action': 'alert', 'message': '[Error] Invalid action!'})

    async def handle_connect(self, ws, wsid):
        """Handle client connection."""

        await super().handle_connect(ws, wsid)

        await ws.send_json({
            'action': 'connected',
            'id': wsid,
            'public_url': self.public_url,
        })

    async def handle_disconnect(self, ws, wsid):
        """Handle client disconnection."""

        if wsid in Player.everyone:
            player = Player.everyone[wsid]
            log.info('[WS] #%s ("%s") disconnected!', wsid, player.name)

            # If the player was in a game, delete that game
            if player.gameid:
                await self.delete_game(Game.games[player.gameid])

            player.delete()
            await self.send_to_spectators({'action': 'player_left', 'id': wsid})
        elif wsid in self.spectator_ids:
            log.info('[WS] #%s (spectator) disconnected!', wsid)
            self.spectator_ids.remove(wsid)

            if wsid == self.master_id:
                log.info(
                    '[WS] Master disconnected! The next spectator will become the new game master!')
                self.master_id = None

    # Config

    def get_routes(self) -> list:
        """Get the routes for the http server"""

        async def handle_index_page(request):
            return web.FileResponse(self.clientdir / 'index.html')

        return [
            web.get(
                '/', handle_index_page),
            web.static(
                '/static', self.clientdir / 'static'),
        ]

    # Gameloop

    async def tick(self, ticknum):
        """This loop could be used to ping players or check if there are games with too long inactive times"""

        # TODO
        ...

    async def gameloop(self):
        """The main game loop"""

        ticknum = 0

        while True:
            await asyncio.gather(
                asyncio.sleep(1 / 10),
                self.tick(ticknum=ticknum),
            )
            ticknum += 1


if __name__ == "__main__":
    print("You need to run the server.py file in the root folder of this repo!")
