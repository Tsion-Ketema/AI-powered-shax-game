import json
import random
import os
import tkinter as tk
from tkinter import messagebox
from utils import adjacentLocations, isMill, numOfPieces
from ai_minimax import get_possible_moves_player, minimax
from ai_mcts import monte_carlo_tree_search
from nn_player_self import choose_move_from_nn

# ========================
# AI Configuration
# ========================
AI_TYPE = {
    "ai": "mcts",     # options: 'minimax' or 'mcts'
    "ai2": "nn"
}

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
        self.root.title("Shax Game (Flexible AI)")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="sandy brown")
        self.canvas.pack()

        self.status_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack()

        self.draw_board_lines()
        self.draw_positions()

        self.board = ["x"] * 24
        self.phase = "placement"
        self.turn = "ai"
        self.placement_moves = 0
        self.first_mill = None
        self.opening_count = 2
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.depth = 4
        self.prev_board = self.board[:]
        self.game_id = random.randint(1000, 9999)
        self.game_log = []
        self.ai_captures = 0
        self.ai2_captures = 0

        self.start_game()

    def run_ai(self, board, depth, alpha, beta, player_symbol, is_maximizing, phase):
        ai_id = "ai" if player_symbol == "1" else "ai2"
        strategy = AI_TYPE[ai_id]
        print(f"[{phase.upper()} PHASE] Player {player_symbol} ({ai_id.upper()}) is using {strategy.upper()} algorithm.")

        if strategy == "minimax":
            return minimax(board, depth, alpha, beta, player_symbol, is_maximizing, phase)
        elif strategy == "mcts":
            move = monte_carlo_tree_search(
                board,
                player_symbol,
                "removal" if phase == "opening" else phase,
                iterations=10000
            )
            if move is None:
                return 0, None
            return 0, move
        elif strategy == 'nn':
            move = choose_move_from_nn(board,phase,player_symbol)
            return 0, move
        else:
            raise ValueError(f"Unsupported AI strategy: {strategy}")

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
        self.root.after(500, self.ai_place)

    def ai_place(self):
        self.prev_board = self.board[:]
        reward = 0
        symbol = "1" if self.turn == "ai" else "2"
        evaluation, move = self.run_ai(self.board, self.depth, self.alpha, self.beta, symbol, True, "placement")
        if move is None:
            print(f"[WARNING] {self.turn.upper()} couldn't place a piece.")
            return
        self.board[move] = symbol
        if isMill(move, self.board) and self.first_mill is None:
            self.first_mill = self.turn
            reward = 10
        self.record_move(symbol, move, reward, False)
        self.placement_moves += 1
        self.update_board()

        if self.placement_moves < 24:
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_place)
        else:
            self.phase = "opening"
            self.handle_opening_phase()

    def handle_opening_phase(self):
        self.turn = self.first_mill if self.first_mill else "ai2"
        self.root.after(500, self.ai_remove)

    def ai_remove(self):
        self.prev_board = self.board[:]
        reward = 3
        symbol = "1" if self.turn == "ai" else "2"
        opponent = "2" if symbol == "1" else "1"
        evaluation, move = self.run_ai(self.board, self.depth, self.alpha, self.beta, symbol, True, "removal")
        if move is None:
            print(f"[WARNING] {self.turn.upper()} could not find a piece to remove.")
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_move)
            return
        self.board[move] = 'x'
        if self.turn == "ai":
            self.ai_captures += 1
        else:
            self.ai2_captures += 1
        self.record_move(symbol, move, reward, False)
        self.update_board()

        if self.phase == "opening":
            self.opening_count -= 1
            if self.opening_count == 0:
                self.phase = "movement"
                self.turn = "ai2" if self.turn == "ai" else "ai"
                self.root.after(500, self.ai_move)
                return
            else:
                self.turn = "ai2" if self.turn == "ai" else "ai"
                self.root.after(500, self.ai_remove)
                return

        self.turn = "ai2" if self.turn == "ai" else "ai"
        self.root.after(500, self.ai_move)

    def ai_move(self):
        self.prev_board = self.board[:]
        reward = 1
        symbol = "1" if self.turn == "ai" else "2"
        moves = get_possible_moves_player(self.board, symbol)
        if not moves:
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_forced_move_no_capture)
            return
        evaluation, move = self.run_ai(self.board, self.depth, self.alpha, self.beta, symbol, True, "movement")
        if move is None:
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_forced_move_no_capture)
            return
        source, dest = move
        self.board[source] = 'x'
        self.board[dest] = symbol
        self.update_board()
        print(f"{self.turn.upper()} moved from {source} to {dest}")

        if isMill(dest, self.board):
            print(f"{self.turn} formed a mill.")
            self.record_move(symbol, move, 10, False)
            self.removal_phase = True
            self.root.after(500, self.ai_remove)
            return

        self.record_move(symbol, move, reward, False)
        self.check_win_conditions()
        self.turn = "ai2" if self.turn == "ai" else "ai"
        self.root.after(500, self.ai_move)

    def ai_forced_move_no_capture(self):
        symbol = "1" if self.turn == "ai" else "2"
        moves = get_possible_moves_player(self.board, symbol)
        if not moves:
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_move)
            return
        source, dest = random.choice(moves)
        self.board[source] = 'x'
        self.board[dest] = symbol
        self.update_board()
        self.record_move(symbol, (source, dest), 0, False)
        self.check_win_conditions()
        self.turn = "ai2" if self.turn == "ai" else "ai"
        self.root.after(500, self.ai_move)

    def check_win_conditions(self):
        ai_pieces = numOfPieces(self.board, "1")
        ai2_pieces = numOfPieces(self.board, "2")
        if ai_pieces < 3:
            self.game_log[-1]["reward"] += 10
            self.game_log[-1]["done"] =True
            self.save_game_log()
            print("Game Over", "AI2 wins!")
            self.root.quit()
        elif ai2_pieces < 3:
            self.game_log[-1]["reward"] += 10
            self.game_log[-1]["done"] =True
            self.save_game_log()
            print("Game Over", "AI wins!")
            self.root.quit()

    def record_move(self, player, action, reward, done):
        self.game_log.append({
            "state": [0 if x == 'x' else int(x) for x in self.prev_board],
            "player": player,
            "action": action,
            "reward": reward,
            "next_state": [0 if x == 'x' else int(x) for x in self.board],
            "done": done,
            "phase": "removal" if self.phase=="opening" else self.phase,
        })

    def save_game_log(self):
        os.makedirs("recorded_ai_games", exist_ok=True)
        with open(f"recorded_ai_games/game_{self.game_id}.jsonl", "w") as f:
            for entry in self.game_log:
                f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    NUM_GAMES = 10  # change to any number you want

    for i in range(NUM_GAMES):
        print(f"\n🔁 Starting Game {i+1}/{NUM_GAMES}")
        root = tk.Tk()
        game = MorrisGame(root)
        root.mainloop()
        root.destroy()