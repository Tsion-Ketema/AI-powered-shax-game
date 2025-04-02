import json
import random
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from backend.utils import (
    adjacentLocations, isMill, numOfPieces
)
from backend.ai import  get_possible_moves_player
from backend.nn_player_self import choose_move_from_nn


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
        self.root.title("Shax game AI vs AI")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="sandy brown")
        self.canvas.pack()

        # Add Status Labels
        self.status_label = tk.Label(
            root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack()

        # Add game counter
        self.game_counter_label = tk.Label(
            root, text="Game: 1/20", font=("Arial", 12), fg="red")
        self.game_counter_label.pack()

        self.draw_board_lines()
        self.draw_positions()
        
        # Game statistics
        self.games_played = 0
        self.max_games = 1
        self.player1_wins = 0  # First AI (plays as "1")
        self.player2_wins = 0  # Second AI (plays as "2")
        
        self.start_new_game()
        
        # Start the first game automatically
        self.root.after(1000, self.play_game_step)
    def start_new_game(self):
        self.board = ["x"] * 24
        self.phase = "placement"
        self.turn = "1"
        self.selected = None
        self.placement_moves = 0
        self.first_mill = None
        self.removal_phase = False
        self.mills_formed = {"1": 0, "2": 0}
        self.opening_count = 2
        self.blocked = False
        self.iteration = 15000

        # Capture tracking
        self.player1_captures = 0
        self.player2_captures = 0

        # Game recording
        self.game_log = []
        self.game_id = random.randint(1000, 9999)
        
        self.prev_board = self.board[:]
        
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
        player1_pieces = numOfPieces(self.board, "1")
        player2_pieces = numOfPieces(self.board, "2")
        turn_text = "AI 1" if self.turn == "1" else "AI 2"

        status_text = (
            f"Turn: {turn_text}  |  AI 1 Pieces: {player1_pieces}  |  AI 2 Pieces: {player2_pieces}  "
            f"|  AI 1 Captures: {self.player1_captures}  |  AI 2 Captures: {self.player2_captures}  | Phase: {self.phase}"
        )
        self.status_label.config(text=status_text)
        
        # Update game counter
        self.game_counter_label.config(text=f"Game: {self.games_played + 1}/{self.max_games} | AI 1 Wins: {self.player1_wins} | AI 2 Wins: {self.player2_wins}")

    def play_game_step(self):
        """Main game loop that progresses the AI vs AI game"""
        # Don't proceed if we've reached max games
        if self.games_played >= self.max_games:
            print(f"All {self.max_games} games completed!")
            print(f"Final score - AI 1: {self.player1_wins}, AI 2: {self.player2_wins}")
            return
            
        # Process the current game state based on phase and turn
        if self.phase == "placement":
            if self.turn == "1":
                self.ai_place("1")
            else:
                self.ai_place("2")
        elif self.phase == "opening":
            if self.removal_phase:
                if self.turn == "1":
                    self.ai_remove("1")
                else:
                    self.ai_remove("2")
            else:
                self.handle_opening_phase()
        elif self.phase == "movement":
            if self.removal_phase:
                if self.turn == "1":
                    self.ai_remove("1")
                else:
                    self.ai_remove("2")
            else:
                # Check for blocked condition
                if self.turn == "1":
                    # Check if player1 is blocked
                    if not get_possible_moves_player(self.board, "1"):
                        print("AI 1 is blocked. AI 2 will move to free up space.")
                        self.ai_forced_move_no_capture("2")
                    else:
                        self.ai_move("1")
                else:
                    # Check if player2 is blocked
                    if not get_possible_moves_player(self.board, "2"):
                        print("AI 2 is blocked. AI 1 will move to free up space.")
                        self.ai_forced_move_no_capture("1")
                    else:
                        self.ai_move("2")
                        
        # Add a small delay to make the gameplay visible
        self.root.after(500, self.play_game_step)

    def handle_opening_phase(self):
        """Handles the logic for the opening phase."""
        # Determine the order of removal
        if self.first_mill == "1":
            print("AI 1 formed the first mill")
            self.turn = "1"
            self.removal_phase = True
        elif self.first_mill == "2":
            print("AI 2 formed the first mill")
            self.turn = "2"
            self.removal_phase = True
        else:
            print("No mills were formed. Starting with AI 1 removal.")
            self.turn = "1"
            self.removal_phase = True

    def ai_place(self, player):
        """AI placement phase for either player"""
        reward = 1
        self.prev_board = self.board[:]
        
        move = choose_move_from_nn(self.board, player,is_movement_phase=False)
        self.board[move] = player
        print(f"AI {player} placed a piece at {move}")
        if isMill(move, self.board):
            if self.first_mill is None:
                self.first_mill = "1" if player == "1" else "2"
                reward = 10
                print(f"AI {player} formed a mill during placement")
        
        self.record_move(player, move, reward, False)
        self.placement_moves += 1
        self.update_board()
        
        if self.placement_moves < 24:
            # Switch turns
            self.turn = "2" if self.turn == "1" else "1"
        else:
            # All pieces placed, move to opening phase
            self.phase = "opening"
            print("All pieces placed, moving to opening phase")

    def ai_move(self, player):
        """AI movement phase for either player"""
        reward = 0
        self.prev_board = self.board[:]
        
        move = choose_move_from_nn(self.board, player, is_movement_phase=True)
        if move is None:
            print(f"AI {player} is blocked. Other AI will move to free up space.")
            self.blocked = True
            self.turn = "2" if player == "1" else "1"
            return
        
        source, dest = move
        action = (source, dest)
        
        self.board[source] = 'x'
        self.board[dest] = player
        print(f"AI {player} moved from {source} to {dest}")
        
        if isMill(dest, self.board):
            print(f"AI {player} formed a mill! It will remove an opponent piece.")
            self.removal_phase = True
            reward = 10
            self.record_move(player, action, reward, False)
            self.update_board()
            self.turn = "2" if player == "1" else "1" 
            return
        
        self.record_move(player, action, reward, False)
        self.update_board()
        self.check_win_conditions()
        self.turn = "2" if player == "1" else "1"

    def ai_remove(self, player):
        """AI removes opponent's piece after forming a mill"""
        opponent = "2" if player == "1" else "1"
        reward = 3
        self.prev_board = self.board[:]
        
        # Find a valid piece to remove
        remove_pos = -1
        for pos, piece in enumerate(self.board):
            if piece == opponent:
                remove_pos = pos
                break
                
        if remove_pos >= 0:
            self.board[remove_pos] = "x"
            self.record_move(player, remove_pos, reward, False)
            print(f"AI {player} removed opponent's piece at {remove_pos}") 
            if player == "1":
                self.player1_captures += 1
            else:
                self.player2_captures += 1
                
            if self.phase == "opening":
                self.opening_count -= 1
         
        self.removal_phase = False
        self.update_board()
        self.check_win_conditions()
        
        # Switch turns
        self.turn = "2" if player == "1" else "1"
        
        # Check if opening phase is complete
        if self.phase == "opening" and self.opening_count == 0:
            self.phase = "movement"
            print("Opening phase complete, moving to movement phase")
        elif self.opening_count != 0:
            print("Opening phase continues, waiting for the other AI to remove a piece")
            self.removal_phase = True
            self.ai_remove("2" if player == "1" else "1")

    def ai_forced_move_no_capture(self, player):
        """When one AI is blocked, force the other AI to move to free up space"""
        moves = get_possible_moves_player(self.board, player)
        self.prev_board = self.board[:]
        
        for move in moves:
            src, dest = move
            opponent = "1" if player == "2" else "2"
            adjacent = adjacentLocations(src)
            
            # Try to find a move that frees up an opponent's piece
            for adj in adjacent:
                if self.board[adj] == opponent:
                    self.board[src] = 'x'
                    self.board[dest] = player
                    action = (src, dest)
                    self.record_move(player, action, 0, False)
                    print(f"AI {player} made a forced move from {src} to {dest} to free opponent")
                    self.update_board()
                    self.turn = "1" if player == "2" else "2"
                    return
        
        # If no specific move found to free opponent, just make any valid move
        if moves:
            src, dest = moves[0]
            self.board[src] = 'x'
            self.board[dest] = player
            action = (src, dest)
            self.record_move(player, action, 0, False)
            print(f"AI {player} made a random forced move from {src} to {dest}")
            self.update_board()
            self.turn = "1" if player == "2" else "2"
        else:
            print(f"AI {player} cannot make a move. Both AIs are blocked.")
            self.check_win_conditions()

    def check_win_conditions(self):
        """Check if either AI has won the game"""
        player1_pieces = numOfPieces(self.board, "1")
        player2_pieces = numOfPieces(self.board, "2")

        if player2_pieces < 3:
            print(f"Game {self.games_played + 1}: AI 1 wins!")
            if self.game_log:
                self.game_log[-1]["reward"] += 10
                self.game_log[-1]["done"] = True
            self.player1_wins += 1
            self.save_game_log()
            self.games_played += 1
            
            if self.games_played < self.max_games:
                self.start_new_game()
            return True
        elif player1_pieces < 3:
            print(f"Game {self.games_played + 1}: AI 2 wins!")
            if self.game_log:
                self.game_log[-1]["reward"] += 10
                self.game_log[-1]["done"] = True
            self.player2_wins += 1
            self.save_game_log()
            self.games_played += 1
            
            if self.games_played < self.max_games:
                self.start_new_game()
            return True
        
        return False

    def record_move(self, player, action, reward, done):
        self.game_log.append({
            "state": [0 if x == 'x' else int(x) for x in self.prev_board],
            "player": player,
            "action": action,
            "reward": reward,
            "next_state": [0 if x == 'x' else int(x) for x in self.board],
            "done": done,
            "phase": self.phase
        })

    def save_game_log(self):
        os.makedirs("recorded_ai_games", exist_ok=True)
        with open(f"recorded_ai_games/game_{self.game_id}.jsonl", "w") as f:
            for entry in self.game_log:
                f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    game = MorrisGame(root)
    root.mainloop()