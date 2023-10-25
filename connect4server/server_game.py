import logging
import asyncio
from aiohttp import web

from .server_base import BasicServer
from .player import Player
from .game import Game

log = logging.getLogger()


class GameServer(BasicServer):
    "Game server"

    def __init__(self, clientdir, public_url=None) -> None:
        self.clientdir = clientdir
        self.public_url = public_url

        self.spectator_ids = []
        self.master_id = None

        super().__init__()

    async def create_games(self):
        print("Creating games if there are enough players...")

        # TODO

    async def delete_game(self, game: Game):
        print("Closing game", game.id)

        # TODO

        if game.p1id in Player.everyone:
            Player.everyone[game.p1id].gameid = None
        if game.p2id in Player.everyone:
            Player.everyone[game.p2id].gameid = None

        await self.send_to_ids({"action": "game_deleted", "id": game.id}, self.spectator_ids + [game.p1id, game.p2id])

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

        unjoined_ids = set(self.websockets) - \
            set(Player.everyone) - set(self.spectator_ids)
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

        # TODO: Add game move actions

        return False

    async def handle_action_from_master(self, action, data, ws, wsid):
        """Handle action sent from master"""

        if action == 'leave_room':
            self.spectator_ids.remove(wsid)
            self.master_id = None
            log.info(
                '[WS] #%s: The game master left the room! The next spectator will become the new game master!', wsid)
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
                    return await ws.send_json({'action': 'alert', 'message': 'Invalid name! Only alphanumeric characters, spaces, underscores and dashes are allowed. (min 3, max 20 characters)'})

                player = Player(name, wsid)
                log.info('[WS] #%s joined as player "%s"', wsid, name)
                await self.send_to_joined({'action': 'player_joined', 'id': wsid, 'player': player.as_dict()})
            else:
                self.spectator_ids.append(wsid)
                log.info('[WS] #%s started spectating!', wsid)
                if self.master_id is None:
                    self.master_id = wsid
                    mode = 'master'
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

            # If the player was in a game, safely delete that game
            if player.gameid:
                await self.delete_game(Game.games[player.gameid])

            player.delete()
            await self.send_to_joined({'action': 'player_left', 'id': wsid})
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
                asyncio.sleep(1/10),
                self.tick(ticknum=ticknum),
            )
            ticknum += 1