import tkinter as tk
from tkinter import messagebox
from backend.game_logic import *
import sys

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
        self.root.title("Shax Game")
        self.canvas = tk.Canvas(root, width=600, height=600, bg="sandy brown")
        self.canvas.pack()

        # Add Status Labels
        self.status_label = tk.Label(
            root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack()

        self.draw_board_lines()
        self.draw_positions()

        self.board = ["x"] * 24
        self.phase = "placement"
        self.turn = "human"
        self.selected = None
        self.placement_moves = 0
        self.removal_phase = False
        self.mills_formed = {"human": 0, "ai": 0}
        self.opening_done = False

        # Capture tracking
        self.human_captures = 0
        self.ai_captures = 0

        self.canvas.bind("<Button-1>", self.handle_click)
        self.update_board()

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

        # Update the game status label
        self.update_status()
        self.root.update()

    def update_status(self):
        """Updates the game status text."""
        human_pieces = numOfPieces(self.board, "1")
        ai_pieces = numOfPieces(self.board, "2")
        turn_text = "Human" if self.turn == "human" else "AI"

        status_text = (
            f"Turn: {turn_text}  |  Human Pieces: {human_pieces}  |  AI Pieces: {ai_pieces}  "
            f"|  Human Captures: {self.human_captures}  |  AI Captures: {self.ai_captures}"
        )
        self.status_label.config(text=status_text)

    def handle_click(self, event):
        for pos, (x, y) in pos_coords.items():
            if (event.x - x)**2 + (event.y - y)**2 <= 15**2:
                if self.phase == "placement":
                    self.handle_placement(pos)
                elif self.phase == "opening":
                    self.handle_opening(pos)
                elif self.phase == "movement":
                    self.handle_movement(pos)
                return

    def handle_placement(self, pos):
        if self.board[pos] != "x":
            messagebox.showinfo("Invalid Move", "This position is occupied.")
            return

        self.board[pos] = "1"
        if isMill(pos, self.board):
            self.mills_formed["human"] += 1
            # self.removal_phase = False

        self.placement_moves += 1
        self.update_board()

        if self.placement_moves == 24:
            self.phase = "opening"
            messagebox.showinfo(
                "Opening Phase", "Now each player removes one opponent piece.")
        else:
            self.ai_place()

    def handle_movement(self, pos):
        if self.turn == "human":
            if self.selected is None:
                if self.board[pos] != "1" and not self.removal_phase:
                    messagebox.showinfo("Invalid Selection",
                                        "Select one of your pieces.")
                elif self.board[pos] != "1" and self.removal_phase:
                    self.handle_removal(pos)
                elif self.board[pos] == "1" and not self.removal_phase:
                    self.selected = pos
                    self.canvas.create_oval(pos_coords[pos][0]-12, pos_coords[pos][1]-12,
                                            pos_coords[pos][0] +
                                            12, pos_coords[pos][1]+12,
                                            outline="red", width=3, tag="highlight")
            else:
                if self.board[pos] != "x":
                    messagebox.showinfo(
                        "Invalid Move", "Destination occupied.")
                    self.canvas.delete("highlight")
                    self.selected = None
                    return
                if pos not in adjacentLocations(self.selected) and numOfPieces(self.board, "1") != 3:
                    messagebox.showinfo(
                        "Invalid Move", "Move must be to an adjacent spot.")
                    self.canvas.delete("highlight")
                    self.selected = None
                    return
                self.board[self.selected] = "x"
                self.board[pos] = "1"
                self.canvas.delete("highlight")
                self.selected = None
                self.update_board()
                if isMill(pos, self.board):
                    messagebox.showinfo(
                        "Mill Formed", "You formed a mill! Remove one of AI's pieces.")
                    self.removal_phase = True
                    return
                else:
                    self.check_win_conditions()
                    self.turn = "ai"
                    self.root.after(500, self.ai_move)
        else:
            return

    def handle_removal(self, pos):
        """Handles the removal of an opponent's piece when a mill is formed."""
        if self.board[pos] == "2":  # Check if the piece belongs to AI
            self.board[pos] = "x"
            self.human_captures += 1  # Increase human's capture count
            self.update_board()
            self.removal_phase = False  # End the removal phase
            self.turn = "ai"  # Switch turn to AI
            self.root.after(500, self.ai_move)  # AI makes its move
        else:
            messagebox.showinfo("Invalid Selection",
                                "Select an AI piece to remove.")

    def handle_opening(self, pos):
        if self.board[pos] == "2":
            self.board[pos] = "x"
            self.human_captures += 1  # Increase human's capture count
            self.update_board()
            self.opening_done = True
            self.phase = "movement"
            messagebox.showinfo(
                "Movement Phase", "Players can now move pieces.")

    def ai_place(self):
        evaluation, move = minimax(
            self.board, depth,  alpha, beta, True, False)
        if evaluation == float('-inf'):
            messagebox.showinfo("Game Over", "You win!")
            self.root.quit()
        else:
            self.board[move] = '2'
        self.placement_moves += 1
        self.update_board()
        if self.placement_moves < 24:
            self.turn = "human"
        else:
            self.phase = "movement"
            self.removal_phase = True

    def ai_move(self):
        evaluation, move = minimax(self.board, depth,  alpha, beta, True, True)
        if evaluation == float('-inf'):
            messagebox.showinfo("Game Over", "You win!")
            self.root.quit()
        else:
            source, dest = move
            self.board[source] = 'x'
            self.board[dest] = '2'
        self.update_board()
        self.check_win_conditions()
        self.turn = "human"

    def check_win_conditions(self):
        human_pieces = numOfPieces(self.board, "1")
        ai_pieces = numOfPieces(self.board, "2")

        if ai_pieces < 3:
            messagebox.showinfo("Game Over", "You win!")
            self.root.quit()
        elif human_pieces < 3:
            messagebox.showinfo("Game Over", "You lose!")
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = MorrisGame(root)
    root.mainloop()
