import tkinter as tk
from tkinter import messagebox
import random
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.utils import isMill, numOfPieces, adjacentLocations
from backend.ai_mcts import monte_carlo_tree_search, get_possible_moves_player
from backend.ai_minimax import minimax

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
        self.root.title("MCTS vs Minimax")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="sandy brown")
        self.canvas.pack()

        self.status_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack()

        self.draw_board_lines()
        self.draw_positions()

        self.board = ["x"] * 24
        self.phase = "placement"
        self.turn = "1"  # 1 = MCTS, 2 = Minimax
        self.placement_moves = 0
        self.removal_phase = False
        self.first_mill = None
        self.opening_count = 0
        self.max_turns = 150
        self.move_count = 0

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
        self.canvas.delete("piece")
        radius = 12
        for pos, (x, y) in pos_coords.items():
            piece = self.board[pos]
            color = "green" if piece == "1" else "yellow" if piece == "2" else "white"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill=color, outline="black", width=2, tag="piece")
        self.update_status()
        self.root.update()

    def update_status(self):
        p1 = numOfPieces(self.board, "1")
        p2 = numOfPieces(self.board, "2")
        self.status_label.config(text=f"Turn: Player {self.turn} | MCTS (1): {p1} | Minimax (2): {p2} | Phase: {self.phase}")

    def start_game(self):
        self.root.after(500, self.play_step)

    def play_step(self):
        if self.move_count > self.max_turns:
            print("Max turns reached. Game Over.")
            return

        if self.phase == "placement":
            self.placement_phase()
        elif self.phase == "opening":
            self.handle_opening_phase()
        elif self.phase == "movement":
            if self.removal_phase:
                self.remove_opponent_piece()
            else:
                self.movement_phase()

        self.root.after(500, self.play_step)

    def placement_phase(self):
        player = self.turn
        move = monte_carlo_tree_search(self.board, player, False, 1000) if player == "1" \
            else minimax(self.board, 3, float('-inf'), float('inf'), True, False)[1]

        if move is not None:
            self.board[move] = player
            print(f"Player {player} placed at {move}")
            self.update_board()
            if isMill(move, self.board) and self.first_mill is None:
                self.first_mill = player

        self.placement_moves += 1
        if self.placement_moves >= 24:
            self.phase = "opening"
            self.opening_count = 2
            print("All pieces placed. Starting opening phase.")
            messagebox.showinfo("Phase Transition", "All pieces placed. Starting opening phase.")

        self.turn = "2" if player == "1" else "1"

    def handle_opening_phase(self):
        if self.removal_phase:
            self.remove_opponent_piece()
            return

        if self.first_mill:
            self.turn = self.first_mill
        else:
            self.turn = "2"

        self.removal_phase = True

    def movement_phase(self):
        player = self.turn
        self.move_count += 1

        # Check if player has fewer than 3 pieces
        if numOfPieces(self.board, player) < 3:
            winner = "2" if player == "1" else "1"
            print(f"Player {player} has fewer than 3 pieces. Game Over.")
            print(f"Winner: Player {winner} ({'Minimax' if winner == '2' else 'MCTS'})")
            messagebox.showinfo("Game Over", f"Player {winner} wins! Player {player} has fewer than 3 pieces.")
            return

        possible_moves = get_possible_moves_player(self.board, player)
        if not possible_moves:
            print(f"Player {player} has no valid moves. Game Over.")
            winner = "2" if player == "1" else "1"
            print(f"Winner: Player {winner} ({'Minimax' if winner == '2' else 'MCTS'})")
            messagebox.showinfo("Game Over", f"Player {winner} wins! Player {player} has no valid moves.")
            return

        move = monte_carlo_tree_search(self.board, player, True, 1000) if player == "1" \
            else minimax(self.board, 3, float('-inf'), float('inf'), True, True)[1]

        if move:
            src, dst = move
            self.board[src] = "x"
            self.board[dst] = player
            print(f"Player {player} moved from {src} to {dst}")
            self.update_board()
            if isMill(dst, self.board):
                print(f"Player {player} formed a mill!")
                self.removal_phase = True
                return

        self.turn = "2" if player == "1" else "1"

    def remove_opponent_piece(self):
        opponent = "2" if self.turn == "1" else "1"
        for i, piece in enumerate(self.board):
            if piece == opponent:
                self.board[i] = "x"
                print(f"Player {self.turn} removed Player {opponent}'s piece at {i}")
                break
        self.update_board()
        self.removal_phase = False
        self.opening_count -= 1
        if self.phase == "opening" and self.opening_count == 0:
            self.phase = "movement"
            print("Opening phase over. Starting movement phase.")
            messagebox.showinfo("Phase Transition", "Opening phase complete. Starting movement phase.")
        else:
            self.turn = "2" if self.turn == "1" else "1"

if __name__ == "__main__":
    root = tk.Tk()
    game = MorrisGame(root)
    root.mainloop()
