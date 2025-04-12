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


class ShaxGame:
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
        self.depth = 4
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
            self.canvas.create_text(x, y - 25, text=str(pos), fill="black")
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
                print(f"Human moved from {self.selected} to {pos}")
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
                    self.blocked = False
                    self.root.after(500, self.ai_move)
        else:
            return

    def handle_removal(self, pos):
        """Handles the removal of an opponent's piece when a mill is formed."""
        if self.board[pos] == "2":  # Check if the piece belongs to AI
            self.board[pos] = "x"
            self.human_captures += 1  # Increase human's capture count
            print(f"human removed AI piece at {pos}")
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
        is_placed = False

        # Step 1: Check if the human has a potential mill and block it
        for pos in range(len(self.board)):
            if self.board[pos] == "x":  # Check empty positions
                # Temporarily simulate human placing a piece
                self.board[pos] = "1"
                if isMill(pos, self.board):  # Check if this forms a mill for the human
                    # Block the mill by placing AI's piece
                    self.board[pos] = "2"
                    if isMill(pos, self.board):
                        if self.first_mill is None:  # Check if this is the first mill
                            self.first_mill = "ai"  # Record that the AI formed the first mill
                    print(f"AI placed at {pos} to block human mill formation.")
                    is_placed = True
                    break
                self.board[pos] = "x"  # Restore the board if no mill is formed

        # Step 2: Use minimax algorithm
        if not is_placed:
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
        is_moved = False
        moves = get_possible_moves_player(self.board, "2")

        if not moves:
            messagebox.showinfo(
                "Blocked", "AI is blocked. Please make a move to free up space.")
            self.turn = "human"
            self.blocked = True
            return

        # Step 1: Try forming a mill
        for src, dest in moves:
            self.board[src] = "x"
            self.board[dest] = "2"
            if isMill(dest, self.board):
                print(f"AI moved from {src} to {dest} to form a mill.")
                self.update_board()
                messagebox.showinfo(
                    "Mill Formed", "AI formed a mill! It will remove one of your pieces.")
                self.removal_phase = True
                self.root.after(500, self.ai_remove)
                return
            self.board[src] = "2"
            self.board[dest] = "x"

        # Step 2: Try to move the ai piece to block potential back-and-forth mill reformation by the human.
        for src, dest in moves:
            self.board[src] = "x"
            self.board[dest] = "2"
            backforth_threat = False
            for mill in mills:
                if any(self.board[p] == "1" for p in mill) and dest in mill:
                    human_positions = [p for p in mill if self.board[p] == "1"]
                    empty_positions = [p for p in mill if self.board[p] == "x"]
                    if len(human_positions) == 2 and len(empty_positions) == 1:
                        backforth_threat = True
                        break
            self.board[src] = "2"
            self.board[dest] = "x"
            if backforth_threat:
                print(
                    f"AI moved from {src} to {dest} to block human back-and-forth mill.")
                self.board[src] = "x"
                self.board[dest] = "2"
                self.update_board()
                self.turn = "human"
                return

        # Step 4: Try moving the AI Piece to the postion of blocking double opportunity threat made by the opponet.
        for src, dest in moves:
            self.board[src] = "x"
            self.board[dest] = "2"
            blocked = False
            for pos, piece in enumerate(self.board):
                if piece == "1":
                    threat_count = 0
                    for mill in mills:
                        if pos in mill and all(self.board[p] in ["1", "x"] for p in mill):
                            threat_count += 1
                    if threat_count >= 2:
                        if dest == pos:
                            blocked = True
                            break
            self.board[src] = "2"
            self.board[dest] = "x"
            if blocked:
                print(
                    f"AI moved from {src} to {dest} to block a double opportunity threat.")
                self.board[src] = "x"
                self.board[dest] = "2"
                self.update_board()
                self.turn = "human"
                return

        # Step 5: Try to recreate a mill by moving back and forth for iself (the last best thing it can do for iself (almot bay tegaday staff)
        for src, dest in moves:
            if self.board[src] == "2" and self.board[dest] == "x":
                for mill in mills:
                    if src in mill and all(self.board[p] == "2" for p in mill):
                        # Safe to vacate unless it forms a mill
                        if any(self.board[adj] == "1" for adj in adjacentLocations(src)) and not isMill(dest, self.board):
                            continue  # Not safe unless it forms a mill

                        # Try simulating back and forth
                        self.board[src] = "x"
                        self.board[dest] = "2"
                        if isMill(dest, self.board):
                            # Simulate moving back to src
                            self.board[dest] = "x"
                            self.board[src] = "2"
                            self.board[src] = "x"
                            self.board[dest] = "2"
                            if isMill(dest, self.board):
                                print(
                                    f"AI recreates a mill via {src} → {dest} → {src}")
                                self.update_board()
                                self.removal_phase = True
                                self.root.after(500, self.ai_remove)
                                return
                        # Reset the board
                        self.board[dest] = "x"
                        self.board[src] = "2"

        # Step 6: Use minimax (last but not least)
        evaluation, move = minimax(
            self.board, self.depth, self.alpha, self.beta, True, True)
        source, dest = move
        self.board[source] = 'x'
        self.board[dest] = '2'
        print(f"AI moved from {source} to {dest} with minimax")

        self.update_board()
        self.check_win_conditions()
        self.turn = "human"

    def ai_remove(self):
        """
        AI removal routine: intelligently remove one of the human's pieces.
        Handles both the opening and movement phases with prioritized logic.
        """
        def remove_piece(pos, reason):
            """Helper function to remove a human piece and update the game state."""
            self.board[pos] = "x"
            self.ai_captures += 1
            print(f"AI removed human piece at {pos} ({reason})")
            self.update_board()
            self.check_win_conditions()  # Ensure win condition is checked immediately
            self.removal_phase = False

            if self.phase == "opening":
                self.opening_count -= 1
                if self.opening_count == 0:
                    self.phase = "movement"
                    self.turn = "human"
                    print(
                        "Opening phase complete. Movement phase begins. Human's turn.")
                else:
                    messagebox.showinfo(
                        "Opening Phase", "Now it's your turn to remove one AI piece.")
                    self.removal_phase = True
            else:
                self.turn = "human"

            self.update_board()

        # ***************Opening phase removal logic*****************
        # Step 1: Opening phase logic - prioritize guaranteed AI mills
        if self.phase == "opening":
            for pos, piece in enumerate(self.board):
                if piece == "1":
                    for mill in mills:
                        if pos in mill and all(self.board[p] in ["2", "x"] for p in mill):
                            if any(self.board[adj] == "2" for adj in adjacentLocations(pos)):
                                self.board[pos] = "x"
                                for adj in adjacentLocations(pos):
                                    if self.board[adj] == "2":
                                        self.board[adj] = "x"
                                        if isMill(adj, self.board):
                                            self.board[adj] = "2"
                                            remove_piece(
                                                pos, "guaranteed mill opportunity")
                                            if self.phase == "opening":
                                                self.opening_count -= 1
                                            if self.phase == "opening" and self.opening_count == 0:
                                                self.phase = "movement"
                                            return
                                        self.board[adj] = "2"
                                self.board[pos] = "1"

            # Step 2: Opening phase logic - disrupt human mills
            for pos, piece in enumerate(self.board):
                if piece == "1":
                    for mill in mills:
                        if pos in mill:
                            human_count = sum(
                                1 for p in mill if self.board[p] == "1")
                            empty_count = sum(
                                1 for p in mill if self.board[p] == "x")
                            if human_count == 2 and empty_count == 1:
                                remove_piece(pos, "disrupt human mill")
                                if self.phase == "opening":
                                    self.opening_count -= 1
                                if self.phase == "opening" and self.opening_count == 0:
                                    self.phase = "movement"
                                return

            # Step 3: This strategy is removing the opponet piece that blocks the AI to form a mill.
            for pos, piece in enumerate(self.board):
                if piece == "2":
                    for adj_pos in adjacentLocations(pos):
                        if self.board[adj_pos] == "2":
                            for mill in mills:
                                if pos in mill and adj_pos in mill:
                                    blocking_pos = [
                                        p for p in mill if p != pos and p != adj_pos][0]
                                    if self.board[blocking_pos] == "1":
                                        # Check that this removal doesn't give human an immediate mill
                                        self.board[blocking_pos] = "x"
                                        opponent_can_form_mill = any(
                                            isMill(p, self.board) for p in range(len(self.board)) if self.board[p] == "1"
                                        )

                                        # Check if AI can form a mill after the removal
                                        ai_can_form_mill = any(
                                            isMill(p, self.board) for p in range(len(self.board)) if self.board[p] == "2"
                                        )

                                        # Check if the AI's mill is safe from immediate disruption
                                        mill_safe = all(
                                            self.board[adj] != "1" for adj in adjacentLocations(blocking_pos) if self.board[adj] == "2"
                                        )

                                        # Restore the human piece
                                        self.board[blocking_pos] = "1"

                                        # Remove the human piece if it does not benefit the opponent and ensures the AI's mill is safe
                                        if not opponent_can_form_mill:
                                            if ai_can_form_mill and mill_safe:
                                                remove_piece(
                                                    blocking_pos, "blocking AI mill and forming a safe mill"
                                                )
                                            else:
                                                remove_piece(
                                                    blocking_pos, "blocking AI mill without aiding opponent"
                                                )

                                            if self.phase == "opening":
                                                self.opening_count -= 1
                                            if self.phase == "opening" and self.opening_count == 0:
                                                self.phase = "movement"
                                            return
            # Step 4: Fallback - remove the first available human piece
            for pos, piece in enumerate(self.board):
                if piece == "1":
                    remove_piece(pos, "fallback")
                    return  # Stop further execution once a piece is removed

        # ***************Movement phase removal logic*****************

        if self.phase == "movement":
            removed = False

            # Step 1: First Detect back-and-forth mill recreation
            for mill in mills:
                human_positions = [p for p in mill if self.board[p] == "1"]
                empty_positions = [p for p in mill if self.board[p] == "x"]

                # Check if the mill has exactly 2 human pieces and 1 empty position
                if len(human_positions) == 2 and len(empty_positions) == 1:
                    # The empty position in the mill
                    empty_pos = empty_positions[0]

                    # Check for human pieces adjacent to the empty position
                    for adj in adjacentLocations(empty_pos):
                        # Human piece adjacent to the empty position
                        if self.board[adj] == "1":
                            remove_piece(
                                adj, "prevent back-and-forth mill recreation april-10-update")
                            removed = True
                            return

            # Step 2: Check for other double opportunity pieces dynamically
            if not removed:
                for pos, piece in enumerate(self.board):
                    if piece == "1":
                        for mill in mills:
                            if pos in mill and all(self.board[p] in ["1", "x"] for p in mill):
                                if any(self.board[adj] == "x" for adj in adjacentLocations(pos)):
                                    remove_piece(
                                        pos, "double opportunity prevention")
                                    removed = True
                                    return

            # Step 4: Fallback - remove the first available human piece
            if not removed:
                for pos, piece in enumerate(self.board):
                    if piece == "1":
                        remove_piece(pos, "final fallback")
                        removed = True
                        return

             # Safety net: log and recover if somehow no piece was removed
            if not removed:
                print(
                    "AI failed to remove a human piece during movement phase. Forcing cleanup.")
                self.removal_phase = False
                self.turn = "human"
                self.update_board()

    def ai_forced_move_no_capture(self):
        """
        When the human is blocked, force the AI to move to free up space.
        Tries to avoid enabling opponent mills.
        Falls back to a random move if no safe move is found.
        """
        moves = get_possible_moves_player(self.board, "2")
        # Add randomness when choosing among safe options
        random.shuffle(moves)

        # First try safe moves (that don’t allow opponent to form a mill)
        for src, dest in moves:
            simulated_board = self.board.copy()
            simulated_board[src] = 'x'
            simulated_board[dest] = '2'

            if not opponent_can_form_mill(simulated_board):
                self.board[src] = 'x'
                self.board[dest] = '2'
                print(f"AI safe forced move from {src} to {dest}")
                self.update_board()
                return

    # If no safe move, fall back to random one
        if moves:
            src, dest = random.choice(moves)
            self.board[src] = 'x'
            self.board[dest] = '2'
            print(f"AI fallback random move from {src} to {dest}")
            self.update_board()

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
