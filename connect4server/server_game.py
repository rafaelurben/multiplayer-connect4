import logging
import asyncio
import random
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

        self.auto_matching_enabled = True

        self.spectator_ids = []
        self.master_id = None

        super().__init__()

    async def create_game(self, p1: Player, p2: Player) -> Game:
        if p1.gameid is not None or p2.gameid is not None:
            raise

        game = Game(p1, p2)

        await self.send_to_spectators(
            {"action": "game_created", "id": game.id, "game": game.as_dict()})
        await self.send_to_spectators(
            {"action": "game_updated", "id": game.id, "game": game.as_dict()})
        await self.send_to_spectators(
            {"action": "player_updated", "id": p1.id, "player": p1.as_dict()})
        await self.send_to_spectators(
            {"action": "player_updated", "id": p2.id, "player": p2.as_dict()})

        await self.send_to_one(
            {"action": "game_joined", "gameid": game.id, "opponent": p2.as_dict(), "board": game.p1board()}, p1.id)
        await self.send_to_one(
            {"action": "game_joined", "gameid": game.id, "opponent": p1.as_dict(), "board": game.p2board()}, p2.id)

        await self.send_to_one(
            {"action": "turn_request", "gameid": game.id, "board": game.p1board()}, p1.id)

        return game

    async def auto_match_if_enabled(self):
        """
        Called after a player joins or a game ends.
        Creates new games if there are 2 or more players waiting.
        Does nothing if auto matching is disabled.
        """

        if not self.auto_matching_enabled:
            return

        print("[Game] Trying to automatically match players...")

        players = list(filter(lambda p: p.is_ready, Player.everyone.values()))
        while len(players) >= 2:
            p1: Player = players.pop(random.randint(0, len(players) - 1))
            p2: Player = players.pop(random.randint(0, len(players) - 1))

            await self.create_game(p1, p2)

    async def delete_game(self, game: Game):
        """Called after a player disconnects or a game ends"""

        game.delete()

        await self.send_to_ids(
            {"action": "game_left", "gameid": game.id}, [game.p1.id, game.p2.id])
        await self.send_to_spectators(
            {"action": "game_deleted", "id": game.id})
        await self.send_to_spectators(
            {"action": "player_updated", "id": game.p1.id, "player": game.p1.as_dict()})
        await self.send_to_spectators(
            {"action": "player_updated", "id": game.p2.id, "player": game.p2.as_dict()})

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
            player = Player.get(wsid)
            player.delete()
            log.info('[WS] #%s left the room! ("%s")',
                     player.id, player.name)
            if player.gameid:
                await self.delete_game(Game.games[player.gameid])
            await self.send_to_spectators({'action': 'player_left', 'id': wsid})
            return await ws.send_json({'action': 'room_left'})
        elif action == 'ready':
            player = Player.get(wsid)
            player.is_ready = not player.is_ready
            if player.is_ready:
                await self.auto_match_if_enabled()
            await self.send_to_spectators({'action': 'player_updated', "id": player.id, "player": player.as_dict()})
            return await ws.send_json({'action': 'ready_response', 'ready': player.is_ready})
        elif action == 'turn':
            player = Player.get(wsid)

            try:
                gameid = int(data.get("gameid"))
                col = int(data.get("column"))
            except TypeError:
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'not an integer'})

            if player.gameid != gameid:
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'not your game'})
            game = Game.games[gameid]

            pnum = game.get_pnum(player)
            if pnum is None:
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'player not found'})

            if not game.validate_turn(pnum, col):
                return await ws.send_json({'action': 'invalid_turn', 'reason': 'turn not valid'})

            game.make_turn(pnum, col)

            p1board = game.p1board()
            p2board = game.p2board()

            otherid = game.p2.id if pnum == 1 else game.p1.id

            thisboard = p1board if pnum == 1 else p2board
            otherboard = p2board if pnum == 1 else p1board

            await self.send_to_one(
                {"action": "turn_accepted", "board": thisboard}, wsid)
            await self.send_to_spectators({"action": "game_updated", "id": game.id, "game": game.as_dict()})

            if game.is_finished:  # if game ended
                # Notify client if won, lost or tie
                await self.send_to_one(
                    {"action": "game_result", "gameid": game.id, "board": p1board,
                     "state": "won" if game.winning_nr == 1 else "lost" if game.winning_nr == 2 else "tie"},
                    game.p1.id)
                await self.send_to_one(
                    {"action": "game_result", "gameid": game.id, "board": p2board,
                     "state": "won" if game.winning_nr == 2 else "lost" if game.winning_nr == 1 else "tie"},
                    game.p2.id)

                # Notify spectators and delete game
                await self.send_to_spectators(
                    {"action": "game_ended", "gameid": game.id,
                     "winning_nr": game.winning_nr, "winner": game.winner.as_dict(), "board": p1board}
                )
                await self.delete_game(game)
            else:
                await self.send_to_one(
                    {"action": "turn_request", "gameid": game.id, "board": otherboard},
                    otherid)
            return True

        return False

    async def handle_action_from_master(self, action, data, ws, wsid):
        """Handle action sent from master"""

        if action == 'leave_room':
            self.spectator_ids.remove(wsid)
            self.master_id = None
            log.info(
                '[WS] #%s: The game master left the room!', wsid)
            await ws.send_json({'action': 'room_left'})
            return True
        elif action == 'toggle_auto_matching':
            self.auto_matching_enabled = not self.auto_matching_enabled
            log.info('Auto matching has been toggled an is now %s!' % ("ON" if self.auto_matching_enabled else "OFF"))
            await self.send_to_joined({'action': 'auto_matching_toggled', 'enabled': self.auto_matching_enabled})
            await self.auto_match_if_enabled()
            return True
        elif action == "match_players":
            try:
                p1 = Player.get(int(data.get("p1id")))
                p2 = Player.get(int(data.get("p2id")))

                if p1.id == 0 or p2.id == 0:
                    await ws.send_json(
                        {'action': 'alert', 'message': "Couldn't find players!"}
                    )
                elif p1.gameid is not None or p2.gameid is not None:
                    await ws.send_json(
                        {'action': 'alert', 'message': "One of the selected players is already in a game!"})
                elif p1.id == p2.id:
                    await ws.send_json(
                        {'action': 'alert', 'message': "Cannot match players with themselves!"}
                    )
                else:
                    await self.create_game(p1, p2)
            except (ValueError, IndexError):
                await ws.send_json({'action': 'alert', 'message': "Failed to get players by id!"})
            return True
        elif action == 'kick_player':
            try:
                player = Player.get(int(data.get("pid")))
                player.delete()
                log.info('[WS] #%s was kicked from the room! ("%s")',
                         player.id, player.name)

                # If the player was in a game, delete that game
                if player.gameid:
                    await self.delete_game(Game.games[player.gameid])

                await self.send_to_spectators({'action': 'player_left', 'id': player.id})
                await self.send_to_one({'action': 'room_left'}, player.id)
                return await self.send_to_one(
                    {'action': 'alert', 'message': '[Info] You have been kicked from the room!'}, player.id)
            except (ValueError, IndexError):
                await ws.send_json({'action': 'alert', 'message': "Failed to get player by id!"})

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
                if not Player.is_valid_name(name):
                    return await ws.send_json({'action': 'name_rejected',
                                               'message': 'Invalid name! Only alphanumeric characters, spaces, '
                                                          'underscores and dashes are allowed. (min 3, '
                                                          'max 20 characters)'})

                player = Player(name, wsid)
                log.info('[WS] #%s joined as player "%s"', wsid, name)
                await ws.send_json({
                    'action': 'room_joined',
                    'mode': 'player',
                    'player': player.as_dict(),
                    'auto_matching_enabled': self.auto_matching_enabled,
                })
                await self.send_to_spectators({'action': 'player_joined', 'id': wsid, 'player': player.as_dict()})
            else:
                self.spectator_ids.append(wsid)
                log.info('[WS] #%s started spectating!', wsid)
                if self.master_id is None and mode == 'master':
                    self.master_id = wsid
                    log.info('[WS] #%s is now the game master!', wsid)
                else:
                    mode = "spectator"

                await ws.send_json({
                    'action': 'room_joined',
                    'mode': mode,
                    'auto_matching_enabled': self.auto_matching_enabled,
                    'players': {p.id: p.as_dict() for p in Player.everyone.values()},
                    'games': {g.id: g.as_dict() for g in Game.games.values()},
                })

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
            player = Player.get(wsid)
            player.delete()
            log.info('[WS] #%s ("%s") disconnected!', wsid, player.name)

            # If the player was in a game, delete that game
            if player.gameid:
                await self.delete_game(Game.games[player.gameid])

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
        """Currently used to ping all clients every 10 seconds"""

        await self.send_to_all({'action': 'ping', 'ticknum': ticknum})

    async def gameloop(self):
        """The main game loop"""

        ticknum = 0

        while True:
            await asyncio.gather(
                asyncio.sleep(10),
                self.tick(ticknum=ticknum),
            )
            ticknum += 1


if __name__ == "__main__":
    print("You need to run the server.py file in the root folder of this repo!")
