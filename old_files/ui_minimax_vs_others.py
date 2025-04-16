from ai_minimax import *
from utils import *
from tkinter import messagebox
import tkinter as tk
import random
from ai_mcts import *
from datetime import datetime
from game_logger import GameLogger


pos_coords = {
    0: (40, 40), 1: (280, 40), 2: (520, 40), 3: (120, 120), 4: (280, 120),
    5: (440, 120), 6: (200, 200), 7: (280, 200), 8: (360, 200), 9: (40, 280),
    10: (120, 280), 11: (200, 280), 12: (360, 280), 13: (440, 280), 14: (520, 280),
    15: (200, 360), 16: (280, 360), 17: (360, 360), 18: (120, 440), 19: (280, 440),
    20: (440, 440), 21: (40, 520), 22: (280, 520), 23: (520, 520)
}

ai_config = {
    "1": "mcts",
    "2": "minimax"
}


class ShaxGame:
    def __init__(self, root, ai_config, logger, game_number):
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
        self.turn = "2"
        self.selected = None
        self.placement_moves = 0
        self.first_mill = None
        self.removal_phase = False
        self.mills_formed = {"human": 0, "ai": 0}
        self.opening_count = 2
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.depth = 5
        self.blocked = False

        # Capture tracking
        self.player_one_captures = 0
        self.player_two_captures = 0

        self.root.after(500, self.ai_place)
        self.update_board()
        self.game_start_time = datetime.now()
        
        self.root = root
        self.ai_config = ai_config  # injected from main
        self.logger = logger
        self.game_number = game_number


        print(
            f"[Game Start] Game started at {self.game_start_time.strftime('%H:%M:%S')}")

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
        player_one_pieces = numOfPieces(self.board, "1")
        player_two_pieces = numOfPieces(self.board, "2")

        status_text = (
            f"Turn: player {self.turn}  |  Player 1 Pieces: {player_one_pieces}  |  Player 2 Pieces: {player_two_pieces}  "
            f"|  Player 1 Captures: {self.player_one_captures}  |  Player 2 Captures: {self.player_two_captures}  | Phase: {self.phase}"
        )
        self.status_label.config(text=status_text)

    def handle_opening_phase(self):
        """Handles the logic for the opening phase."""
        # Determine the order of removal
        if self.first_mill == "1":
            print(
                "Opening Phase Player 1 formed the first mill Player 1 remove player 2's piece first")
            self.removal_phase = True
            self.turn = "1"
            self.ai_remove()
        elif self.first_mill == "2":
            print(
                "Opening Phase Player 2 formed a mill first! It will remove one of opponent pieces.")
            self.removal_phase = True
            self.turn = "2"
            self.ai_remove()  # AI removes one human piece
        else:
            print(
                "Opening Phase", "No mills were formed. Player 2 will remove player 1's piece first.")
            self.turn = "2"
            self.removal_phase = True
            self.ai_remove()

    def ai_place(self):
        move = None
        if ai_config[self.turn] == "minimax":
            evaluation, move = minimax(
                self.board, self.depth,  self.alpha, self.beta, self.turn, True, False)
        elif ai_config[self.turn] == "mcts":
            move = monte_carlo_tree_search(self.board, self.turn, self.phase)

        self.board[move] = self.turn
        # print(
        # f"Player {self.turn} placed piece {self.placement_moves+1} at position {move}")
        if isMill(move, self.board):
            if self.first_mill is None:
                self.first_mill = self.turn
        self.placement_moves += 1
        self.update_board()
        if self.placement_moves < 24:
            self.turn = "1" if self.turn == "2" else "2"
            self.ai_place()
        else:
            self.phase = "opening"
            self.handle_opening_phase()
            self.removal_phase = True

    def ai_move(self):
        opponent = "2" if self.turn == "1" else "1"

        moves = get_possible_moves_player(self.board, self.turn)
        if not moves:
            # print(
            #     f"Player {self.turn} is blocked. Player {opponent} will make a move to free up space.")
            self.turn = opponent
            self.blocked = True
            self.ai_forced_move_no_capture()
            return

        if ai_config[self.turn] == "mcts":
            move = monte_carlo_tree_search(self.board, self.turn, self.phase)
            source, dest = move
            self.board[source] = 'x'
            self.board[dest] = self.turn
            print(
                f"Player {self.turn} moved from {source} to {dest} with mcts")
            self.update_board()
            self.check_win_conditions()
            self.turn = opponent
            self.root.after(500, self.ai_move)
        elif ai_config[self.turn] == "minimax":
            # Step 1: Try forming a mill
            for src, dest in moves:
                self.board[src] = "x"
                self.board[dest] = self.turn
                if isMill(dest, self.board):
                    # print(
                    #     f"Player {self.turn} moved from {src} to {dest} to form a mill.")
                    self.update_board()
                    # print(
                    #     f"Player {self.turn} formed a mill! It will remove one of opponent piece.")
                    self.removal_phase = True
                    self.root.after(500, self.ai_remove)
                    return
                self.board[src] = self.turn
                self.board[dest] = "x"
            # Step 2: Try to move the ai piece to block potential back-and-forth mill reformation by the human.
            for src, dest in moves:
                self.board[src] = "x"
                self.board[dest] = self.turn
                backforth_threat = False
                for mill in mills:
                    if any(self.board[p] == opponent for p in mill) and dest in mill:
                        opponent_positions = [
                            p for p in mill if self.board[p] == opponent]
                        empty_positions = [
                            p for p in mill if self.board[p] == "x"]
                        if len(opponent_positions) == 2 and len(empty_positions) == 1:
                            backforth_threat = True
                            break
                self.board[src] = self.turn
                self.board[dest] = "x"
                if backforth_threat:
                    # print(
                    #     f"Player {self.turn} moved from {src} to {dest} to block opponent back-and-forth mill.")
                    self.board[src] = "x"
                    self.board[dest] = self.turn
                    if isMill(dest, self.board):
                        # print(
                        #     f"Player {self.turn} moved from {src} to {dest} to form a mill while blocking potential back-and-forth mill.")
                        self.update_board()
                        # print(
                        #     f"Player {self.turn} formed a mill! It will remove one of opponent pieces.")
                        self.removal_phase = True
                        self.root.after(500, self.ai_remove)
                        return
                    self.update_board()
                    self.turn = opponent
                    self.root.after(500, self.ai_move)
                    return
            # Step 5: Try to recreate a mill by moving back and forth for iself (the last best thing it can do for iself (almot bay tegaday staff)
            for src, dest in moves:
                if self.board[src] == self.turn and self.board[dest] == "x":
                    for mill in mills:
                        if src in mill and all(self.board[p] == self.turn for p in mill):
                            # Safe to vacate unless it forms a mill
                            if any(self.board[adj] == opponent for adj in adjacentLocations(src)) and all(self.board[adj] != "x" for adj in adjacentLocations(src)):
                                continue  # Not safe unless it forms a mill
                            else:
                                empty_space = []
                                safe_target = []
                                for i in adjacentLocations(src):
                                    if self.board[i] == "x":
                                        empty_space.append(i)
                                for pos in empty_space:
                                    if any(self.board[adj] == opponent for adj in adjacentLocations(pos)):
                                        continue
                                    else:
                                        safe_target.append(pos)
                                if not safe_target:
                                    self.board[src] = "x"
                                    self.board[dest] = self.turn
                                    print(
                                        f"Player {self.turn} moved from {src} to {dest} to create back and forth mill. no safe target")
                                else:
                                    self.board[src] = "x"
                                    self.board[safe_target[0]] = self.turn
                                if isMill(dest, self.board):
                                    print(
                                        f"Player {self.turn} moved from {src} to {dest} to create back and forth mill. safe target")
                                    self.update_board()
                                    print(
                                        f"Player {self.turn} formed a mill! It will remove one of opponent piece.")
                                    self.removal_phase = True
                                    self.root.after(500, self.ai_remove)
                                self.update_board()
                                self.check_win_conditions()
                                self.turn = opponent
                                self.root.after(500, self.ai_move)

                                return

            # Step 4: Try moving the AI Piece to the postion of blocking double opportunity threat made by the opponet.
            for src, dest in moves:
                self.board[src] = "x"
                self.board[dest] = self.turn
                blocked = False
                for pos, piece in enumerate(self.board):
                    if piece == opponent:
                        threat_count = 0
                        for mill in mills:
                            if pos in mill and all(self.board[p] in [opponent, "x"] for p in mill):
                                threat_count += 1
                        if threat_count >= 2:
                            if dest == pos:
                                blocked = True
                                break
                self.board[src] = self.turn
                self.board[dest] = "x"
                if blocked:
                    print(
                        f"Player {self.turn} moved from {src} to {dest} to block a double opportunity threat.")
                    self.board[src] = "x"
                    self.board[dest] = self.turn
                    if isMill(dest, self.board):
                        print(
                            f"Player {self.turn} moved from {src} to {dest} to form a mill while blocking double opportunity threat.")
                        self.update_board()
                        print(
                            f"Player {self.turn} formed a mill! It will remove one of opponent pieces.")
                        self.removal_phase = True
                        self.root.after(500, self.ai_remove)
                        return
                    self.update_board()
                    self.turn = opponent
                    self.root.after(500, self.ai_move)
                    return

            # Step 6: Use minimax (last but not least)
            evaluation, move = minimax(
                self.board, self.depth, self.alpha, self.beta, self.turn, True, True)
            source, dest = move
            self.board[source] = 'x'
            self.board[dest] = self.turn
            print(
                f"Player {self.turn} moved from {source} to {dest} with minimax")

            self.update_board()
            self.check_win_conditions()
            self.turn = opponent
            self.root.after(500, self.ai_move)

    def ai_remove(self):
        """
        AI removal routine: intelligently remove one of the human's pieces.
        Handles both the opening and movement phases with prioritized logic.
        """
        opponent = "2" if self.turn == "1" else "1"

        def remove_piece(pos, reason):
            """Helper function to remove a human piece and update the game state."""
            self.board[pos] = "x"
            if self.turn == "1":
                self.player_one_captures += 1
            else:
                self.player_two_captures += 1
            # print(
                # f"Player {self.turn} removed opponent piece at {pos} ({reason})")
            self.update_board()
            self.check_win_conditions()  # Ensure win condition is checked immediately
            self.removal_phase = False

            if self.phase == "opening":
                self.opening_count -= 1
                if self.opening_count == 0:
                    self.phase = "movement"
                    self.turn = opponent
                    self.root.after(500, self.ai_move)
                    print(
                        f"Opening phase complete. Movement phase begins. Player {opponent}'s turn.")
                else:
                    print(
                        f"Opening Phase Now it's Player {opponent}'s turn to remove one {self.turn}'s piece.")
                    self.removal_phase = True
                    self.turn = opponent
                    self.root.after(500, self.ai_remove)
            else:
                self.turn = opponent
                self.root.after(500, self.ai_move)
            self.update_board()

        if ai_config[self.turn] == "mcts":
            phase_for_mcts = "removal" if self.removal_phase else self.phase
            print(
                f"[DEBUG] self.phase={self.phase}, self.removal_phase={self.removal_phase}")

            move = monte_carlo_tree_search(
                self.board, self.turn, phase_for_mcts)

            print(f"[MCTS] Phase: {self.phase}, Move returned: {move}")

            remove_piece(move, "Mcts removal move")

        elif ai_config[self.turn] == "minimax":

            # ***************Opening phase removal logic*****************
            # Step 1: Opening phase logic - prioritize guaranteed AI mills
            if self.phase == "opening":
                for pos, piece in enumerate(self.board):
                    if piece == opponent:
                        for mill in mills:
                            if pos in mill and all(self.board[p] in [self.turn, "x"] for p in mill):
                                if any(self.board[adj] == self.turn for adj in adjacentLocations(pos)):
                                    self.board[pos] = "x"
                                    for adj in adjacentLocations(pos):
                                        if self.board[adj] == self.turn:
                                            self.board[adj] = "x"
                                            if isMill(adj, self.board):
                                                self.board[adj] = self.turn
                                                remove_piece(
                                                    pos, "guaranteed mill opportunity")
                                                if self.phase == "opening":
                                                    self.opening_count -= 1
                                                if self.phase == "opening" and self.opening_count == 0:
                                                    self.phase = "movement"
                                                return
                                            self.board[adj] = self.turn
                                    self.board[pos] = opponent

                # Step 2: Opening phase logic - disrupt human mills
                for pos, piece in enumerate(self.board):
                    if piece == opponent:
                        for mill in mills:
                            if pos in mill:
                                human_count = sum(
                                    1 for p in mill if self.board[p] == opponent)
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
                    if piece == self.turn:
                        for adj_pos in adjacentLocations(pos):
                            if self.board[adj_pos] == self.turn:
                                for mill in mills:
                                    if pos in mill and adj_pos in mill:
                                        blocking_pos = [
                                            p for p in mill if p != pos and p != adj_pos][0]
                                        if self.board[blocking_pos] == opponent:
                                            # Check that this removal doesn't give human an immediate mill
                                            self.board[blocking_pos] = "x"
                                            opponent_can_form_mill = any(
                                                isMill(p, self.board) for p in range(len(self.board)) if self.board[p] == opponent
                                            )

                                            # Check if AI can form a mill after the removal
                                            ai_can_form_mill = any(
                                                isMill(p, self.board) for p in range(len(self.board)) if self.board[p] == self.turn
                                            )

                                            # Check if the AI's mill is safe from immediate disruption
                                            mill_safe = all(
                                                self.board[adj] != opponent for adj in adjacentLocations(blocking_pos) if self.board[adj] == self.turn
                                            )

                                            # Restore the human piece
                                            self.board[blocking_pos] = opponent

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
                    if piece == opponent:
                        remove_piece(pos, "fallback")
                        return  # Stop further execution once a piece is removed

            # ***************Movement phase removal logic*****************

            if self.phase == "movement":
                removed = False

                # Step 1: First Detect back-and-forth mill recreation
                for mill in mills:
                    human_positions = [
                        p for p in mill if self.board[p] == opponent]
                    empty_positions = [p for p in mill if self.board[p] == "x"]

                    # Check if the mill has exactly 2 human pieces and 1 empty position
                    if len(human_positions) == 2 and len(empty_positions) == 1:
                        # The empty position in the mill
                        empty_pos = empty_positions[0]

                        # Check for human pieces adjacent to the empty position
                        for adj in adjacentLocations(empty_pos):
                            # Human piece adjacent to the empty position
                            if self.board[adj] == opponent:
                                remove_piece(
                                    adj, "prevent back-and-forth mill recreation april-10-update")
                                removed = True
                                return

                # Step 2: Check for other double opportunity pieces dynamically
                if not removed:
                    for pos, piece in enumerate(self.board):
                        if piece == opponent:
                            for mill in mills:
                                if pos in mill and all(self.board[p] in [opponent, "x"] for p in mill):
                                    if any(self.board[adj] == "x" for adj in adjacentLocations(pos)):
                                        remove_piece(
                                            pos, "double opportunity prevention")
                                        removed = True
                                        return

                # Step 4: Fallback - remove the first available human piece
                if not removed:
                    for pos, piece in enumerate(self.board):
                        if piece == opponent:
                            remove_piece(pos, "final fallback")
                            removed = True
                            return

                 # Safety net: log and recover if somehow no piece was removed
                if not removed:
                    print(
                        f"Player {self.turn} failed to remove a player {opponent}'s piece during movement phase. Forcing cleanup.")
                    self.removal_phase = False
                    self.turn = opponent
                    self.update_board()

    def ai_forced_move_no_capture(self):
        """
        When the human is blocked, force the AI to move to free up space.
        Tries to avoid enabling opponent mills.
        Falls back to a random move if no safe move is found.
        """
        moves = get_possible_moves_player(self.board, self.turn)
        if moves:
            src, dest = random.choice(moves)
            self.board[src] = 'x'
            self.board[dest] = self.turn
            print(
                f"Player {self.turn} fallback random move from {src} to {dest}")
            self.update_board()

        if not get_possible_moves_player(self.board, self.turn):
            print(f"Player {self.turn} is blocked too. No move can be made.")
            return

        evaluation, move = minimax(
            self.board, self.depth, self.alpha, self.beta, self.turn, True, True)

        if move is None:
            print(f"Player {self.turn} AI is blocked. No move can be made.")
            return

        self.update_board()
        self.check_win_conditions()
        self.turn = "2" if self.turn == "1" else "1"
        self.root.after(500, self.ai_move)

    def check_win_conditions(self):
        player_one_pieces = numOfPieces(self.board, "1")
        player_two_pieces = numOfPieces(self.board, "2")

        if player_one_pieces < 3 or player_two_pieces < 3:
            winner = "Player 2" if player_one_pieces < 3 else "Player 1"
            loser = "Player 1" if player_one_pieces < 3 else "Player 2"
            game_end_time = datetime.now()
            duration = game_end_time - self.game_start_time

            print(f"[Game End] {winner} won against {loser}")
            print(f"[Game Duration] Total duration: {duration}")

            # Log result using logger
            self.logger.log_result(
                game_number=self.game_number,
                winner=winner,
                start_time=self.game_start_time,
                end_time=game_end_time,
                ai_config=ai_config  # <--- perfect, since it holds current player type info
            )

            self.root.quit()


if __name__ == "__main__":

    logger = GameLogger("Minimax with Rules vs MCTS")
    for i in range(5):

        print(f"Game {i+1}/10 started")

        root = tk.Tk()
        game = ShaxGame(root)

        game.logger = logger  # Attach logger to the game
        game.game_number = i + 1
        root.mainloop()
        root.destroy()

    logger.summarize_and_plot()
