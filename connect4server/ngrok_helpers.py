import subprocess
import requests
import time
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def is_ngrok_available() -> bool:
    "Check if ngrok is available"

    try:
        result = subprocess.run(["ngrok", "version"], check=False, stdout=subprocess.DEVNULL)
        return result.returncode == 0
    except FileNotFoundError:
        return False

class NgrokTunnel():
    def __init__(self, port: int = 80, web_addr: str = "localhost:4040"):
        self.port = port
        self.web_addr = web_addr
        self.tunnel = None

    def __open(self):
        self.tunnel = subprocess.Popen(["ngrok", "http", str(self.port)], stdout=subprocess.DEVNULL)

    def __close(self):
        self.tunnel.kill()

    def _get_url(self, tries=3, retry_wait_s=3, request_timeout=5) -> str:
        "Get the ngrok tunnel url"

        i = 1
        while True:
            try:
                response = requests.get(f"http://{self.web_addr}/api/tunnels", timeout=request_timeout)
                data = response.json()
                url = data["tunnels"][0]["public_url"]
                return url
            except (requests.exceptions.ConnectionError, IndexError, KeyError) as exc:
                if i == tries:
                    raise RuntimeError(f"Failed to get ngrok tunnel url after {tries} tries.") from exc

            print(f"Failed to get ngrok tunnel url, retrying in {retry_wait_s} seconds... ({i}/{tries})")
            time.sleep(retry_wait_s)
            i += 1

    def __enter__(self):
        self.__open()
        return self._get_url()

    def __exit__(self, exc_type, exc_value, traceback):
        self.__close()

    def __del__(self):
        self.__close()
