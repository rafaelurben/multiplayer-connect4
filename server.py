"""Run the py4connect server"""

import logging
import sys
import asyncio
from pathlib import Path

from connect4server.server_game import GameServer
from connect4server.ngrok_helpers import NgrokTunnel, is_ngrok_available

# Setup logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
log.addHandler(stream)


def main(*args, **kwargs):
    """Run the server"""

    server = GameServer(*args, **kwargs)

    try:
        loop.run_until_complete(server.start())
        loop.run_until_complete(server.gameloop())
    except KeyboardInterrupt:
        loop.run_until_complete(server.stop())
        loop.close()


# Main part - only called if file is run directly (not via import)
if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    clientdir = Path(__file__).parent / 'connect4webclient'

    if "--ngrok" in sys.argv:
        if is_ngrok_available():
            log.info("[Server] Opening ngrok tunnel...")
            with NgrokTunnel() as ngrok_url:
                log.info("[Server] Tunnel URL: %s", ngrok_url)
                main(clientdir, public_url=ngrok_url)
        else:
            log.warning(
                "[Server] ngrok is not in PATH! Please install it from https://ngrok.com/download or add it to PATH.")
            log.info("[Server] Starting server without ngrok tunnel.")

    url = os.environ.get('PUBLIC_URL', 'http://localhost')
    log.info(f"[Server] URL: {url}")
    main(clientdir, public_url=url if "--public" in sys.argv else None)
