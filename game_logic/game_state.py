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
from game_logic.rules import Rules


class GameState:
    def __init__(self):
        """Manages the Shax game state, including turns, piece placement, and movement."""
        self.board = Board()
        self.rules = Rules()
        self.players = ['Player 1', 'Player 2']
        self.current_phase = "placement"  # "placement" or "movement"
        self.player_pieces = {'Player 1': 12, 'Player 2': 12}
        self.current_player = "Player 1"
        self.first_mill_player = None

    def switch_turn(self):
        """Switches turns between players."""
        self.current_player = "Player 2" if self.current_player == "Player 1" else "Player 1"

    def play_turn(self, position):
        """Handles turns for placement and movement."""
        if self.current_phase == "placement":
            if self.board.place_piece(position, self.current_player):
                self.player_pieces[self.current_player] -= 1

                # Check if a mill is formed before switching turn
                if self.rules.check_mill(self.board, position, self.current_player):
                    if not self.first_mill_player:
                        self.first_mill_player = self.current_player
                    return "Mill Formed!"

                # Transition to movement phase if all pieces are placed
                if sum(self.player_pieces.values()) == 0:
                    self.current_phase = "movement"
                    return "Movement phase begins!"

                # Only switch turns after checking mill formation
                self.switch_turn()
                return "Piece placed"
            return "Invalid placement"
