from ai import *
from utils import *
from tkinter import messagebox
import tkinter as tk
import random

# Position coordinates for the board
pos_coords = {
    0: (40, 40), 1: (280, 40), 2: (520, 40), 3: (120, 120), 4: (280, 120),
    5: (440, 120), 6: (200, 200), 7: (280, 200), 8: (360, 200), 9: (40, 280),
    10: (120, 280), 11: (200, 280), 12: (360, 280), 13: (440, 280), 14: (520, 280),
    15: (200, 360), 16: (280, 360), 17: (360, 360), 18: (120, 440), 19: (280, 440),
    20: (440, 440), 21: (40, 520), 22: (280, 520), 23: (520, 520)
}


class MorrisGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Shax Game by AI Crackers")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="sandy brown")
        self.canvas.pack()

        # Add Status Labels
        self.status_label = tk.Label(
            root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack()

        self.draw_board_lines()
        self.draw_positions()

        # Game state
        self.board = ["x"] * 24
        self.phase = "placement"
        self.turn = "ai"  # Start with AI
        self.placement_moves = 0
        self.first_mill = None
        self.removal_phase = False
        self.mills_formed = {"ai": 0, "ai2": 0}
        self.opening_count = 2  # Two removals per player in the opening phase
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.depth = 5

        # Capture tracking
        self.ai_captures = 0
        self.ai2_captures = 0

        # Start the game loop
        self.start_game()

    def draw_board_lines(self):
        self.canvas.create_rectangle(40, 40, 520, 520, width=2)
        self.canvas.create_rectangle(120, 120, 440, 440, width=2)
        self.canvas.create_rectangle(200, 200, 360, 360, width=2)
        self.canvas.create_line(280, 40, 280, 200, width=2)
        self.canvas.create_line(520, 280, 360, 280, width=2)
        self.canvas.create_line(280, 520, 280, 360, width=2)
        self.canvas.create_line(40, 280, 200, 280, width=2)

    def draw_positions(self):
        radius = 12
        for pos, (x, y) in pos_coords.items():
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill="white", outline="black", width=2)

    def update_board(self):
        """Redraw the board based on the current state."""
        self.canvas.delete("piece")
        radius = 12
        for pos, (x, y) in pos_coords.items():
            piece = self.board[pos]
            color = "green" if piece == "1" else "yellow" if piece == "2" else "white"
            self.canvas.create_text(x, y - 25, text=str(pos), fill="black")
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill=color, outline="black", width=2, tag="piece")

        # Update the game status label
        self.update_status()
        self.root.update()

    def update_status(self):
        """Updates the game status text."""
        ai_pieces = numOfPieces(self.board, "1")
        ai2_pieces = numOfPieces(self.board, "2")
        turn_text = "AI" if self.turn == "ai" else "AI2"
        status_text = (
            f"Turn: {turn_text}  |  AI Pieces: {ai_pieces}  |  AI2 Pieces: {ai2_pieces}  "
            f"|  AI Captures: {self.ai_captures}  |  AI2 Captures: {self.ai2_captures}  | Phase: {self.phase}"
        )
        self.status_label.config(text=status_text)

    def start_game(self):
        self.turn = "ai"
        self.phase = "placement"
        self.root.after(500, self.ai_place)

    def ai_place(self):
        if self.turn == "ai":
            evaluation, move = minimax(
                self.board, self.depth, self.alpha, self.beta, True, False)
            self.board[move] = '1'  # AI places a piece
        elif self.turn == "ai2":
            evaluation, move = minimax(
                self.board, self.depth, self.alpha, self.beta, False, False)
            self.board[move] = '2'  # AI2 places a piece

        self.placement_moves += 1
        self.update_board()

        if self.placement_moves < 24:
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_place)
        else:
            self.phase = "opening"
            self.handle_opening_phase()

    def handle_opening_phase(self):
        """
        Handle the opening phase where both players remove pieces.
        Each player removes two pieces before transitioning to the movement phase.
        """
        if self.first_mill == "ai":
            self.turn = "ai"
            self.root.after(500, self.ai_remove)
        elif self.first_mill == "ai2":
            self.turn = "ai2"
            self.root.after(500, self.ai_remove)
        else:
            self.turn = "ai"
            self.root.after(500, self.ai_remove)

    def ai_remove(self):
        """
        AI removal routine: remove one of the opponent's pieces.
        Prioritize removing a human piece that blocks the AI from forming a mill,
        and ensure there is another AI piece that can later move into the vacant space.
        """
        # Step 1: Search for blocking human pieces
        for pos, piece in enumerate(self.board):
            if piece == "2":  # Check AI pieces
                for adj_pos in adjacentLocations(pos):
                    if self.board[adj_pos] == "2":  # Check adjacent AI piece
                        for mill in mills:
                            if pos in mill and adj_pos in mill:  # Both AI pieces are part of the same mill
                                blocking_pos = [
                                    p for p in mill if p != pos and p != adj_pos][0]
                                # Check if the third position is a human piece
                                if self.board[blocking_pos] == "1":
                                    if any(self.board[backup_pos] == "2" for backup_pos in adjacentLocations(blocking_pos)):
                                        # Remove the blocking human piece
                                        self.board[blocking_pos] = "x"
                                        print(
                                            f"AI removed blocking piece at {blocking_pos}")
                                        self.ai_captures += 1
                                        self.update_after_removal()
                                        return

        # Step 2: Fallback to removing the first available human piece
        for pos, piece in enumerate(self.board):
            if piece == "1":  # Find the first human piece
                print(
                    f"No blocking piece found. Removing first available piece at {pos}")
                self.board[pos] = "x"
                self.ai_captures += 1
                break

        # Update the game state after removal
        self.update_after_removal()

    def update_after_removal(self):
        """
        Updates the game state after a piece is removed.
        """
        self.update_board()
        self.removal_phase = False
        if self.phase == "opening":
            self.opening_count -= 1
            if self.opening_count == 0:
                self.phase = "movement"
                self.turn = "ai2" if self.turn == "ai" else "ai"
                self.root.after(500, self.ai_move)
            else:
                self.turn = "ai2" if self.turn == "ai" else "ai"
                self.root.after(500, self.ai_remove)
        else:
            self.check_win_conditions()
            self.turn = "human"

    def ai_move(self):
        print(f"AI Move: Current Turn: {self.turn}, Phase: {self.phase}")
        if self.turn == "ai":
            moves = get_possible_moves_player(self.board, "1")
            print(f"AI Possible Moves: {moves}")
            if not moves:
                print("AI has no moves. Switching to AI2.")
                self.turn = "ai2"
                self.root.after(500, self.ai_forced_move_no_capture)
                return
            evaluation, move = minimax(
                self.board, self.depth, self.alpha, self.beta, True, True)
            print(f"AI Chosen Move: {move}, Evaluation: {evaluation}")
            if move is None:
                print("AI could not find a valid move. Switching to AI2.")
                self.turn = "ai2"
                self.root.after(500, self.ai_forced_move_no_capture)
                return
            source, dest = move
            print(f"AI Moving from {source} to {dest}")
            self.board[source] = 'x'
            self.board[dest] = '1'
        elif self.turn == "ai2":
            moves = get_possible_moves_player(self.board, "2")
            print(f"AI2 Possible Moves: {moves}")
            if not moves:
                print("AI2 has no moves. Switching to AI.")
                self.turn = "ai"
                self.root.after(500, self.ai_forced_move_no_capture)
                return
            evaluation, move = minimax(
                self.board, self.depth, self.alpha, self.beta, False, True)
            print(f"AI2 Chosen Move: {move}, Evaluation: {evaluation}")
            if move is None:
                print("AI2 could not find a valid move. Switching to AI.")
                self.turn = "ai"
                self.root.after(500, self.ai_forced_move_no_capture)
                return
            source, dest = move
            print(f"AI2 Moving from {source} to {dest}")
            self.board[source] = 'x'
            self.board[dest] = '2'

        self.update_board()

        if isMill(dest, self.board):
            print(
                f"Mill formed at {dest} by {self.turn}. Entering removal phase.")
            self.removal_phase = True
            self.root.after(500, self.ai_remove)
            return

        self.check_win_conditions()
        self.turn = "ai2" if self.turn == "ai" else "ai"
        print(f"Turn switched to: {self.turn}")
        self.root.after(500, self.ai_move)

    def ai_forced_move_no_capture(self):
        """
        Handle forced moves when a player is blocked.
        During these moves, no captures occur, even if a mill is formed.
        """
        if self.turn == "ai":
            moves = get_possible_moves_player(self.board, "1")
            if not moves:
                self.turn = "ai2"
                self.root.after(500, self.ai_move)
                return
            source, dest = random.choice(moves)
            self.board[source] = 'x'
            self.board[dest] = '1'
        elif self.turn == "ai2":
            moves = get_possible_moves_player(self.board, "2")
            if not moves:
                self.turn = "ai"
                self.root.after(500, self.ai_move)
                return
            source, dest = random.choice(moves)
            self.board[source] = 'x'
            self.board[dest] = '2'

        self.update_board()
        self.check_win_conditions()
        self.turn = "ai2" if self.turn == "ai" else "ai"
        self.root.after(500, self.ai_move)

    def check_win_conditions(self):
        ai_pieces = numOfPieces(self.board, "1")
        ai2_pieces = numOfPieces(self.board, "2")
        if ai_pieces < 3:
            messagebox.showinfo("Game Over", "AI2 wins!")
            self.root.quit()
        elif ai2_pieces < 3:
            messagebox.showinfo("Game Over", "AI wins!")
            self.root.quit()


# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = MorrisGame(root)
    root.mainloop()
