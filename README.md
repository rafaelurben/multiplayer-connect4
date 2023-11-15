# multiplayer-connect4

Connect Four server & client in Python incl. web app.

## Server

```shell
python -m pip install -U pip requests aiohttp==3.9.0b0
python server.py
```

> [!NOTE]
> aiohttp 3.8.x funktioniert noch nicht mit Python 3.12, daher wird die Beta von 3.9.x verwendet

> [!NOTE]
> Die Installation von aiohttp benötigt möglicherweise die [C++ Build Tools](https://visualstudio.microsoft.com/de/visual-cpp-build-tools/) ("Desktopentwicklung mit C++")

## Client

Select your clientfile from ./connect4pyclients.

```shell
python -m pip install -U pip websockets
python CLIENTFILE.py
```
