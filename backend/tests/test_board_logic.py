from backend.game_logic.board import Board  # Only testing board structure now
import sys
import os

# Add the project root directory to sys.path (Fix Import Issues)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_board_initialization():
    """
    Ensures board positions are initialized correctly.
    """
    board = Board()

    print("🔹 Checking if all positions are initialized correctly...")

    # Check if board has exactly 24 positions
    assert len(board.positions) == 24, "❌ Board should have 24 positions"

    # Check if all positions are empty at the start
    for pos in board.positions:
        assert board.positions[pos] is None, f"❌ Position {pos} should be empty"

    print("✅ Board positions are correctly initialized!")


def test_board_placement():
    """
    Ensures that placing a piece updates the correct position.
    """
    board = Board()

    print("\n🔹 Placing Player 1's piece at position 0...")
    board.place_piece(0, "Player 1")

    assert board.positions[0] == "Player 1", "❌ Position 0 should be occupied by Player 1"
    print("✅ Position 0 correctly updated!")

    print("\n🔹 Placing Player 2's piece at position 5...")
    board.place_piece(5, "Player 2")

    assert board.positions[5] == "Player 2", "❌ Position 5 should be occupied by Player 2"
    print("✅ Position 5 correctly updated!")

    print("\n🔹 Attempting to place another piece at position 0 (should fail)...")
    result = board.place_piece(0, "Player 2")

    assert not result, "❌ Should not be able to place a piece in an already occupied position"
    assert board.positions[0] == "Player 1", "❌ Position 0 should still belong to Player 1"
    print("✅ Position 0 remains unchanged!")


if __name__ == "__main__":
    test_board_initialization()
    test_board_placement()
