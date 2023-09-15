"Game class"

class Game:
    games = {}
    lastgameid = 0

    def __init__(self):
        self.lastgameid += 1
        self.gameid = self.lastgameid
        self.games[self.gameid] = self
    
    # TODO: Create game model
