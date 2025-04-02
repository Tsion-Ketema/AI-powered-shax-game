from ai_minimax import *
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
        self.root.title("Minimax_vs_minimax")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="sandy brown")
        self.canvas.pack()

        self.status_label = tk.Label(
            root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack()

        self.draw_board_lines()
        self.draw_positions()

        self.board = ["x"] * 24
        self.phase = "placement"
        self.turn = "ai"
        self.placement_moves = 0
        self.first_mill = None
        self.removal_phase = False
        self.mills_formed = {"ai": 0, "ai2": 0}
        self.opening_count = 4
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.depth = 4
        self.max_turns = 200
        self.move_count = 0

        self.ai_captures = 0
        self.ai2_captures = 0

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
            self.canvas.create_text(x, y - 25, text=str(pos), fill="black")
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill=color, outline="black", width=2, tag="piece")

        self.update_status()
        self.root.update()

    def update_status(self):
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
            _, move = minimax(self.board, self.depth,
                              self.alpha, self.beta, True, False)
            self.board[move] = '1'
            print(f"AI placed a piece at {move}")
            if isMill(move, self.board):
                for m in mills:
                    if move in m and all(self.board[p] == '1' for p in m):
                        print(f"AI formed a mill with positions {m}")
                        break
        elif self.turn == "ai2":
            _, move = minimax(self.board, self.depth,
                              self.alpha, self.beta, False, False)
            self.board[move] = '2'
            print(f"AI2 placed a piece at {move}")
            if isMill(move, self.board):
                for m in mills:
                    if move in m and all(self.board[p] == '2' for p in m):
                        print(f"AI2 formed a mill with positions {m}")
                        break

        self.placement_moves += 1
        self.update_board()

        if self.placement_moves < 24:
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_place)
        else:
            self.phase = "opening"
            self.turn = "ai"
            self.root.after(500, self.ai_remove)

    def ai_remove(self):
        opponent = "1" if self.turn == "ai2" else "2"
        for pos, piece in enumerate(self.board):
            if piece == opponent:
                self.board[pos] = "x"
                print(f"{self.turn} removed opponent's piece at position {pos}")
                if self.turn == "ai":
                    self.ai_captures += 1
                else:
                    self.ai2_captures += 1
                break

        self.update_board()
        self.opening_count -= 1

        if self.opening_count == 0:
            self.phase = "movement"
            self.turn = "ai"
            self.root.after(500, self.ai_move)
        else:
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_remove)

    def ai_move(self):
        print(f"AI Move: Turn: {self.turn}, Phase: {self.phase}")

        self.move_count += 1
        if self.move_count > self.max_turns:
            messagebox.showinfo(
                "Game Over", "Game ended due to maximum move count.")
            self.root.quit()
            return

        player = "1" if self.turn == "ai" else "2"
        moves = get_possible_moves_player(self.board, player)

        if not moves:
            print(f"{self.turn} has no moves. Switching to opponent.")
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_move)
            return

        eval_value, move = minimax(self.board[:], self.depth, float(
            '-inf'), float('inf'), player == "1", True)

        if move is None:
            print(f"{self.turn} could not find a move.")
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_move)
            return

        src, dst = move
        print(f"{self.turn} moved from {src} to {dst}")
        self.board[src] = "x"
        self.board[dst] = player
        self.update_board()

        if isMill(dst, self.board):
            print(f"{self.turn} formed a mill at position {dst}")
            for m in mills:
                if dst in m and all(self.board[p] == player for p in m):
                    print(f"{self.turn} formed a mill with positions {m}")
                    break
            self.turn = "ai" if player == "1" else "ai2"
            self.root.after(500, self.ai_remove)
            return

        self.check_win_conditions()
        self.turn = "ai2" if self.turn == "ai" else "ai"
        self.root.after(500, self.ai_move)

    def check_win_conditions(self):
        p1 = numOfPieces(self.board, "1")
        p2 = numOfPieces(self.board, "2")
        if p1 < 3:
            messagebox.showinfo("Game Over", "AI2 wins!")
            self.root.quit()
        elif p2 < 3:
            messagebox.showinfo("Game Over", "AI wins!")
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = MorrisGame(root)
    root.mainloop()
