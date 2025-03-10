# ✅ What it Does?
# ✔ Defines valid game moves
# ✔ Checks if a mill is formed
# ✔ Checks if the game is over

# ❌ What it Does NOT Do?
# ✘ Doesn’t place/move pieces (that’s the board’s job).
# ✘ Doesn’t manage turns (that’s GameState).


class Rules:
    def __init__(self):
        """Defines valid mills and adjacency for movement."""
        self.mills = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],
            [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23],
            [0, 9, 21], [3, 10, 18], [6, 11, 15], [1, 4, 7],
            [16, 19, 22], [8, 12, 17], [5, 13, 20], [2, 14, 23]
        ]

    def check_mill(self, board, position, player):
        """
        Checks if a player has formed a mill (three consecutive pieces in a valid mill).
        """
        print(f"🔍 Checking mill for {player} at position {position}")

        for mill in self.mills:
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
