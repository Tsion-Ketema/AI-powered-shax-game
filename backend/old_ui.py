import json
import os
from ai_minimax import get_possible_moves_player, minimax
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
         self.turn = "ai1"  # Start with AI
         self.placement_moves = 0
         self.first_mill = None
         self.removal_phase = False
         self.mills_formed = {"ai": 0, "ai2": 0}
         self.opening_count = 2  # Two removals per player in the opening phase
         self.alpha = float('-inf')
         self.beta = float('inf')
         self.depth = 4
         self.prev_board = self.board[:]
         self.game_id = random.randint(1000, 9999)
         self.game_log = []

 
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
         self.turn = "ai2"
         self.phase = "placement"
         self.root.after(500, self.ai_place)
 
     def ai_place(self):
         self.prev_board = self.board[:]
         reward = 0
         if self.turn == "ai":
             evaluation, move = minimax(self.board, self.depth, self.alpha, self.beta, "1", True, False)
             self.board[move] = '1'  # AI places a piece
             if isMill(move, self.board):
                    if self.first_mill is None:
                        print(f"first mill formed by {self.turn}")
                        self.first_mill="ai"
                        reward = 10
             self.record_move("1",move, reward, False)

         elif self.turn == "ai2":
             evaluation, move = minimax(self.board, self.depth, self.alpha, self.beta, "2", False, False)
             self.board[move] = '2'  # AI2 places a piece
             if isMill(move, self.board):
                    if self.first_mill is None:
                        print(f"first mill formed by {self.turn}")
                        self.first_mill="ai2"
                        reward = 10
             self.record_move("2",move, reward, False)
 
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
         Automate the removal of pieces during the opening phase.
         Each player removes two pieces before transitioning to the movement phase.
         """
         self.prev_board = self.board[:]
         reward = 3
         if self.turn == "ai":
            eval, move = minimax(self.board, self.depth, self.alpha, self.beta, "2", True, "removal")
            print(f"Evaluation of picece removal at {move}: score {eval}")
            self.board[move]='x'
            self.ai_captures+=1
            self.record_move("1",move, reward, False)

         elif self.turn == "ai2":
            eval, move = minimax(self.board, self.depth, self.alpha, self.beta, "1", True, "removal")
            print(f"Evaluation of picece removal at {move}: score {eval}")
            self.board[move]='x'
            self.ai2_captures+=1
            self.record_move("2",move, reward, False)

         self.update_board()
 
         if self.phase=="opening":
             self.opening_count -= 1
 
         # Check if both players have completed their removals
         if self.opening_count == 0 and self.phase=="opening":
             self.phase = "movement"
             self.turn = "ai2" if self.turn == "ai" else "ai"
             self.root.after(500, self.ai_move)
             return
         elif self.opening_count != 0 and self.phase=="opening":
             # Alternate turns for removals
             self.turn = "ai2" if self.turn == "ai" else "ai"
             self.root.after(500, self.ai_remove)
             return
         self.check_win_conditions()
         self.turn = "ai2" if self.turn == "ai" else "ai"
         self.root.after(500, self.ai_move)
 
     def ai_move(self):
         self.prev_board = self.board[:]
         reward = 1
         if self.turn == "ai":
             moves = get_possible_moves_player(self.board, "1")
             if not moves:
                 self.turn = "ai2"
                 self.root.after(500, self.ai_forced_move_no_capture)
                 return
             _, move = minimax(self.board, self.depth, self.alpha, self.beta,"1", True, self.phase)
             if move is None:
                 self.turn = "ai2"
                 self.root.after(500, self.ai_forced_move_no_capture)
                 return
             source, dest = move
             self.board[source] = 'x'
             self.board[dest] = '1'
             self.update_board()
             print(f" AI 1 moved from {source} to {dest}")

         elif self.turn == "ai2":
             moves = get_possible_moves_player(self.board, "2")
             if not moves:
                 self.turn = "ai"
                 self.root.after(500, self.ai_forced_move_no_capture)
                 return
             evaluation, move = minimax(self.board, self.depth, self.alpha, self.beta, "2",True, self.phase)
             if move is None:
                 self.turn = "ai"
                 self.root.after(500, self.ai_forced_move_no_capture)
                 return
             source, dest = move
             self.board[source] = 'x'
             self.board[dest] = '2'
             self.update_board()
             print(f" AI 2 moved from {source} to {dest}")
 
         if isMill(dest, self.board):
             print(f"{self.turn} formed a mill.")
             self.removal_phase = True
             player = "2" if self.turn=="ai2" else "1"
             self.record_move(player,move, 10, False)
             self.root.after(500, self.ai_remove)
             return
 
         self.check_win_conditions()
         player = "2" if self.turn=="ai2" else "1"
         self.record_move(player,move, reward, False)
         self.turn = "ai2" if self.turn == "ai" else "ai"
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
             self.save_game_log()
             messagebox.showinfo("Game Over", "AI2 wins!")
             self.root.quit()
         elif ai2_pieces < 3:
             self.save_game_log()
             messagebox.showinfo("Game Over", "AI wins!")
             self.root.quit()
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
 
 # Run the game
if __name__ == "__main__":
     root = tk.Tk()
     game = MorrisGame(root)
     root.mainloop()