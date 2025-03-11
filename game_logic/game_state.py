# ✅ What it Does?
# ✔ Calls Board to place/move pieces.
# ✔ Calls Rules to check mills, moves, and win conditions.
# ✔ Manages turns (ensures correct player plays next).
# ✔ Controls game phases (placement → movement).

# ❌ What it Does NOT Do?
# ✘ Doesn’t store positions (that’s Board).
# ✘ Doesn’t define rules (that’s Rules).
# ✘ Doesn’t handle UI/AI (that comes later).

from game_logic.board import Board
from game_logic.helpers import Player
from game_logic.rules import Rules
from helpers import Phase as phase


class GameState:
    def __init__(self):
        """Manages the Shax game state, including turns, piece placement, and movement."""
        self.board = Board()
        self.rules = Rules(self.board)
        self.players = ['Player 1', 'Player 2']
        self.current_phase = phase.PLACEMENT   # "placement" or "movement"
        self.players = [Player(1,"Player 1","green"), Player(2,"Player 2","yellow")]
        self.current_player = self.players[0]
        self.first_mill_player = None
        self.mills = []

    def switch_turn(self):
        """Switches turns between players."""
        self.current_player = self.players[0] if self.current_player == self.players[1] else self.players[1]

    def change_phase(self):
         if self.current_phase == phase.PLACEMENT:
            self.current_phase = phase.MOVEMENT
            return True
         return False


    def play_turn(self, position):
        """Handles turns for placement and movement."""
        if self.current_phase == phase.PLACEMENT:
            if self.place_piece(position, self.current_player):
                self.current_player.pieces -= 1

                # Check if a mill is formed before switching turn
                if self.rules.check_mill(self.board, position, self.current_player):
                    if not self.first_mill_player:
                        self.first_mill_player = self.current_player
                    return "Mill Formed!"

                # Transition to movement phase if all pieces are placed
                if (player for player in self.players if player.pieces==0):
                    self.current_phase = phase.MOVEMENT
                    return "Movement phase begins!"

                # Only switch turns after checking mill formation
                self.switch_turn()
                return "Piece placed"
            return "Invalid placement"

    def place_piece(self, position, player):
        """
        Places a piece on the board at the specified position if it's empty.
        :param position: The position index (0-23).
        :param player: 'Player 1' or 'Player 2'.
        :return: True if the piece was placed, False otherwise.
        """
        if position in self.board.positions and self.board.positions is None:
            self.board.positions = player
            return True, self
        return False

    def move_piece(self,from_pos,to_pos, player):
        if self.is_move_valid(from_pos,to_pos):
            self.board.positions[from_pos]=None
            self.board.positions[from_pos]=player
            return True
        return False

    """
    :helps a player to remove opponent piece
    """

    def capture(self,pos, player ):
        if player in self.mills and self.mills[0].used==False:
            if self.board.positions[pos]!=player and self.board.positions[pos] is not None:
                self.board.positions[pos]=None

    """
    :reset the game status
    """
    def reset(self):
        self.board = Board()
        return True

    """
    :returns valid moves for a player if requested 
    """
    def get_valid_move_player(self,player):
        return [move for move in self.board.positions if move % 2 == 0]

    """
    :returns all valid moves
    """
    def get_valid_moves(self):
        return [move for move in self.board.positions if move % 2 == 0]

    def is_move_valid(self, pos_1, pos_2):
        return pos_2 in self.board.adjacency[pos_1] and self.board.adjacency[pos_1] is None

    def get_game_state(self):
        return self