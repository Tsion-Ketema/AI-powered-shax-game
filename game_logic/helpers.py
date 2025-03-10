class Mill:
    def __init__(self):
        self.pos_one=None
        self.pos_two=None
        self.pos_three=None
        self.player=None
        self.used=False



class Player:
    def __init__(self, name,color, piece_count = 12):
        self.name=name
        self.color=color
        self.pieces=piece_count
