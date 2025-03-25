from ai import *
from utils import *
from tkinter import messagebox
import tkinter as tk
import random


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
        self.root.title("Shax game by AI crackers")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="sandy brown")
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
        self.first_mill = None
        self.removal_phase = False
        self.mills_formed = {"human": 0, "ai": 0}
        self.opening_count = 2
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.depth = 6
        self.blocked = False

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
            f"|  Human Captures: {self.human_captures}  |  AI Captures: {self.ai_captures}  | Phase: {self.phase}"
        )
        self.status_label.config(text=status_text)

    def handle_click(self, event):
        for pos, (x, y) in pos_coords.items():
            if (event.x - x)**2 + (event.y - y)**2 <= 15**2:
                if self.phase == "placement":
                    self.handle_placement(pos)
                elif self.phase == "opening":
                    self.handle_removal(pos)
                elif self.phase == "movement":
                    self.handle_movement(pos)
                return

    def handle_placement(self, pos):

        if self.board[pos] != "x":
            messagebox.showinfo("Invalid Move", "This position is occupied.")
            return

        self.board[pos] = "1"
        if isMill(pos, self.board):
            if self.first_mill is None:
                self.first_mill = "human"
            self.mills_formed["human"] += 1

        self.placement_moves += 1
        self.update_board()

        if self.placement_moves == 24:
            self.phase = "opening"
            self.handle_opening_phase()
        else:
            self.ai_place()

    def handle_movement(self, pos):
        # If it's the human's turn and not in a removal phase, check if human is blocked.
        if self.turn == "human" and not self.removal_phase:
            if not get_possible_moves_player(self.board, "1"):
                messagebox.showinfo(
                    "Blocked", "You are blocked. AI will move to free up space.")
                self.ai_forced_move_no_capture()
                return

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
                if isMill(pos, self.board) and not self.blocked:
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
            if self.phase == "opening":
                self.opening_count -= 1
            self.update_board()
            self.turn = "ai"
            if self.opening_count != 0:
                self.ai_remove()
            else:
                self.phase = "movement"
                self.removal_phase = False
                self.root.after(500, self.ai_move)  # AI makes its move
        else:
            messagebox.showinfo("Invalid Selection",
                                "Select an AI piece to remove.")

    def handle_opening_phase(self):
        """Handles the logic for the opening phase."""
        # Determine the order of removal
        if self.first_mill == "human":
            print("Human formed the first mill")  # Debug statement
            messagebox.showinfo(
                "Opening Phase", "You formed a mill first! Remove one AI piece.")
            self.removal_phase = True
        elif self.first_mill == "ai":
            print("AI formed the first mill")  # Debug statement
            messagebox.showinfo(
                "Opening Phase", "AI formed a mill first! It will remove one of your pieces.")
            self.ai_remove()  # AI removes one human piece
        else:
            print("No mills were formed")  # Debug statement
            messagebox.showinfo(
                "Opening Phase", "No mills were formed. AI will remove one of your pieces first.")
            self.ai_remove()

    def remove_piece_opening(self, player):
        """Handles the removal of a piece by the specified player during the opening phase."""
        if player == "human":
            self.removal_phase = True  # Allow human to remove a piece
            messagebox.showinfo("Your Turn", "Click on an AI piece to remove.")
        elif player == "ai":
            # AI removes one human piece
            for pos in range(len(self.board)):
                if self.board[pos] == "1":  # Find the first human piece
                    self.board[pos] = "x"  # Remove it
                    self.ai_captures += 1  # Increment AI's capture count
                    self.update_board()
                    break
            self.removal_phase = False  # End the removal phase for the AI

    def ai_place(self):
        evaluation, move = minimax(
            self.board, self.depth,  self.alpha, self.beta, True, False)
        self.board[move] = '2'
        if isMill(move, self.board):
            if self.first_mill is None:  # Check if this is the first mill
                self.first_mill = "ai"  # Record that the AI formed the first mill
        self.placement_moves += 1
        self.update_board()
        if self.placement_moves < 24:
            self.turn = "human"
        else:
            self.phase = "opening"
            self.handle_opening_phase()
            self.removal_phase = True

    def ai_move(self):
        # if self.removal_phase:
        #     self.ai_remove()
        #     return

        evaluation, move = minimax(
            self.board, self.depth, self.alpha, self.beta, True, True)
        if move is None:
            messagebox.showinfo(
                "Blocked", "AI is blocked. Please make a move to free up space.")
            self.turn = "human"
            self.blocked = True
            return

        else:
            source, dest = move
            self.board[source] = 'x'
            self.board[dest] = '2'
            print(f"AI moved from {source} to {dest}")
            self.update_board()
            if isMill(dest, self.board):
                messagebox.showinfo(
                    "Mill Formed", "AI formed a mill! It will remove one of your pieces.")
                self.removal_phase = True
                self.root.after(500, self.ai_remove)
                return
        self.update_board()
        self.check_win_conditions()
        self.turn = "human"

    def ai_remove(self):
        # AI removal routine: remove one of the human's pieces.
        for pos, piece in enumerate(self.board):
            if piece == "1":
                self.board[pos] = "x"
                print(f"AI removed piece at {pos}")
                self.ai_captures += 1
                break
        self.removal_phase = False
        if self.phase == "opening":
            self.opening_count -= 1
        self.update_board()
        self.check_win_conditions()
        self.turn = "human"
        if self.phase == "opening" and self.opening_count == 0:
            self.phase = "movement"
        elif self.opening_count != 0:
            messagebox.showinfo(
                "Opening Phase", "Now it's your turn to remove one AI piece.")
            self.removal_phase = True

    def ai_forced_move_no_capture(self):
        """
        When the human is blocked, force the AI to move to free up space.
        During these moves, even if a mill is formed, no capture occurs.
        """
        moves = get_possible_moves_player(self.board, "2")

        for move in moves:
            src, dest = move
            adjacent = adjacentLocations(src)
            for j in random.choices(adjacent):
                if self.board[j] == '1':
                    self.board[src] = 'x'
                    self.board[dest] = '2'
                    print(f"AI block removal move from {src} to {dest}")
                    self.update_board()
                    return

        if not get_possible_moves_player(self.board, "2"):
            messagebox.showinfo(
                "Blocked", "AI is blocked too. No move can be made.")
            return
        evaluation, move = minimax(
            self.board, self.depth, self.alpha, self.beta, True, True)
        if move is None:
            messagebox.showinfo(
                "Blocked", "AI is blocked. No move can be made.")
            return
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
