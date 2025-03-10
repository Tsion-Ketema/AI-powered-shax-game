# ✅ What it Does?
# ✔ Defines valid game moves
# ✔ Checks if a mill is formed
# ✔ Checks if the game is over

# ❌ What it Does NOT Do?
# ✘ Doesn’t place/move pieces (that’s the board’s job).
# ✘ Doesn’t manage turns (that’s GameState).


class Rules:
    def __init__(self, board):
        self.board = board

    def check_mill(self, board, position, player):
        """
        Checks if a player has formed a mill (three consecutive pieces in a valid mill).
        """
        print(f"🔍 Checking mill for {player} at position {position}")

        for mill in self.board.mills:
            if position in mill:
                print(f"   ➡ Checking mill: {mill}")
                occupied_positions = [board.positions[p] for p in mill]
                print(f"   ➡ Current mill positions: {occupied_positions}")

                # Check if all three positions in the mill belong to the same player
                if all(pos == player for pos in occupied_positions):
                    print("✅ Mill Formed!")
                    return True  # A valid mill is formed

        print("❌ No mill formed.")
        return False  # No valid mill found
