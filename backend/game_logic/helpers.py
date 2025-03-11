from enum import Enum


class Mill:
    def __init__(self):
        self.mill_id=None
        self.player=None
        self.used=False



class Player:
    def __init__(self, player_id, name, color, piece_count = 12):
        self.id = player_id
        self.name=name
        self.color=color
        self.pieces=piece_count

class Phase(Enum):
    PLACEMENT=1
    MOVEMENT=2

