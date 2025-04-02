from ai_minimax import *
from utils import *
from tkinter import messagebox
import tkinter as tk
import random
import time

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

        self.game_history = []  # To store game states for training
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
        self.last_move = None
        self.repeated_moves_count = 0
        self.last_five_moves = []

        self.ai_captures = 0
        self.ai2_captures = 0

        # Add randomness factor to evaluation
        self.ai_randomness = 0.1  # 10% random component for AI
        self.ai2_randomness = 0.15  # 15% random component for AI2

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
        
        # Save the current board state for training
        self.game_history.append(self.board[:])

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
        
        # Add some randomness to starting moves
        if random.random() < 0.5:
            self.depth = random.choice([3, 4, 5])
        
        self.root.after(500, self.ai_place)

    def ai_place(self):
        if self.turn == "ai":
            possible_positions = get_possible_moves(self.board)
            
            # Small chance to make a random move for variety
            if random.random() < 0.1:  # 10% chance for random move
                move = random.choice(possible_positions)
            else:
                # Use minimax with a small random factor
                eval_scores = []
                for pos in possible_positions[:min(5, len(possible_positions))]:  # Consider top positions
                    new_board = self.board[:]
                    new_board[pos] = '1'
                    eval_score = evaluate_with_randomness(new_board, self.ai_randomness)
                    eval_scores.append((eval_score, pos))
                
                eval_scores.sort(reverse=True)  # Sort by best score
                # Pick from top 3 if available
                if len(eval_scores) >= 3:
                    _, move = random.choice(eval_scores[:3])
                else:
                    _, move = eval_scores[0] if eval_scores else (0, possible_positions[0])
                
            self.board[move] = '1'
            print(f"AI placed a piece at {move}")
            
            # Check if mill was formed
            if isMill(move, self.board):
                for m in mills:
                    if move in m and all(self.board[p] == '1' for p in m):
                        print(f"AI formed a mill with positions {m}")
                        self.mills_formed["ai"] += 1
                        self.removal_phase = True
                        self.turn = "ai"  # Stay AI's turn for removal
                        self.root.after(500, self.ai_remove)
                        return
        elif self.turn == "ai2":
            possible_positions = get_possible_moves(self.board)
            
            # Small chance to make a random move for variety
            if random.random() < 0.15:  # 15% chance for random move
                move = random.choice(possible_positions)
            else:
                # Use minimax with a small random factor
                eval_scores = []
                for pos in possible_positions[:min(5, len(possible_positions))]:
                    new_board = self.board[:]
                    new_board[pos] = '2'
                    eval_score = evaluate_with_randomness(new_board, self.ai2_randomness)
                    eval_scores.append((eval_score, pos))
                
                eval_scores.sort(reverse=True)
                # Pick from top 3 if available
                if len(eval_scores) >= 3:
                    _, move = random.choice(eval_scores[:3])
                else:
                    _, move = eval_scores[0] if eval_scores else (0, possible_positions[0])
                
            self.board[move] = '2'
            print(f"AI2 placed a piece at {move}")
            
            # Check if mill was formed
            if isMill(move, self.board):
                for m in mills:
                    if move in m and all(self.board[p] == '2' for p in m):
                        print(f"AI2 formed a mill with positions {m}")
                        self.mills_formed["ai2"] += 1
                        self.removal_phase = True
                        self.turn = "ai2"  # Stay AI2's turn for removal
                        self.root.after(500, self.ai_remove)
                        return

        self.placement_moves += 1
        self.update_board()

        if self.placement_moves < 18:  # Changed from 24 to 18 (9 pieces each)
            self.turn = "ai2" if self.turn == "ai" else "ai"
            self.root.after(500, self.ai_place)
        else:
            self.phase = "movement"
            self.turn = "ai"
            self.root.after(500, self.ai_move)

    def ai_remove(self):
        current_player = "1" if self.turn == "ai" else "2"
        opponent = "2" if current_player == "1" else "1"
        
        # Find pieces that can be removed (not in mills)
        removable_pieces = []
        for pos, piece in enumerate(self.board):
            if piece == opponent:
                if not isMill(pos, self.board):
                    removable_pieces.append(pos)
        
        # If no pieces outside mills, then any piece can be removed
        if not removable_pieces:
            removable_pieces = [pos for pos, piece in enumerate(self.board) if piece == opponent]
        
        if removable_pieces:
            # Strategy: remove pieces that are part of potential mills or in strategic positions
            best_pos = None
            best_score = -float('inf')
            
            for pos in removable_pieces:
                score = 0
                
                # Check if the position is strategic
                if pos in [1, 4, 7, 16, 19, 22]:  # Center positions
                    score += 30
                
                # Check if removing this piece prevents a mill
                for m in mills:
                    if pos in m:
                        mill_pieces = sum(1 for p in m if self.board[p] == opponent)
                        if mill_pieces == 2:  # Removing this prevents a mill
                            score += 50
                
                if score > best_score:
                    best_score = score
                    best_pos = pos
            
            # If no strategic position found, choose randomly
            if best_pos is None and removable_pieces:
                best_pos = random.choice(removable_pieces)
            
            if best_pos is not None:
                self.board[best_pos] = "x"
                print(f"{self.turn} removed opponent's piece at position {best_pos}")
                if self.turn == "ai":
                    self.ai_captures += 1
                else:
                    self.ai2_captures += 1
        
        self.update_board()
        self.removal_phase = False
        self.turn = "ai2" if self.turn == "ai" else "ai"
        self.root.after(500, self.ai_move if self.phase == "movement" else self.ai_place)

    def ai_move(self):
        print(f"AI Move: Turn: {self.turn}, Phase: {self.phase}")

        self.move_count += 1
        if self.move_count > self.max_turns:
            messagebox.showinfo("Game Over", "Game ended due to maximum move count.")
            self.save_game_history()
            self.root.quit()
            return

        player = "1" if self.turn == "ai" else "2"
        moves = get_possible_moves_player(self.board, player)

        if not moves:
            print(f"{self.turn} has no moves. Game over!")
            winner = "AI2" if self.turn == "ai" else "AI"
            messagebox.showinfo("Game Over", f"{winner} wins because opponent has no moves!")
            self.save_game_history()
            self.root.quit()
            return

        # Check for repeated moves
        if len(self.last_five_moves) >= 10:  # 5 moves from each player
            # Check if the last 10 moves (5 per player) are being repeated
            if self.last_five_moves[-10:] == self.last_five_moves[-20:-10]:
                print("Detected move repetition. Adding randomness.")
                # Introduce more randomness to break the cycle
                if random.random() < 0.4:  # 40% chance to make a random move
                    move = random.choice(moves)
                    src, dst = move
                    self.board[src] = "x"
                    self.board[dst] = player
                    self.last_five_moves.append(move)
                    self.update_board()
                    
                    # Check for mill after random move
                    if isMill(dst, self.board):
                        print(f"{self.turn} formed a mill at position {dst}")
                        self.removal_phase = True
                        self.root.after(500, self.ai_remove)
                        return
                    
                    self.check_win_conditions()
                    self.turn = "ai2" if self.turn == "ai" else "ai"
                    self.root.after(500, self.ai_move)
                    return
        
        # Add some randomness to the move decision
        randomness = self.ai_randomness if player == "1" else self.ai2_randomness
        
        # Choose a move from the top 3 best moves
        best_moves = []
        for src, dst in moves:
            new_board = self.board[:]
            new_board[src] = "x"
            new_board[dst] = player
            
            # Add small random component to evaluation
            eval_value = evaluate_board(new_board, player) + (random.random() * randomness * 100)
            best_moves.append((eval_value, (src, dst)))
        
        best_moves.sort(reverse=(player == "2"))  # Sort based on player
        
        # Choose from top 3 moves if available
        if len(best_moves) >= 3:
            _, move = random.choice(best_moves[:3])
        else:
            _, move = best_moves[0]
        
        src, dst = move
        print(f"{self.turn} moved from {src} to {dst}")
        self.board[src] = "x"
        self.board[dst] = player
        
        # Record the move to detect repetitions
        self.last_five_moves.append(move)
        if len(self.last_five_moves) > 20:  # Keep only last 20 moves
            self.last_five_moves.pop(0)
            
        self.update_board()

        if isMill(dst, self.board):
            print(f"{self.turn} formed a mill at position {dst}")
            for m in mills:
                if dst in m and all(self.board[p] == player for p in m):
                    print(f"{self.turn} formed a mill with positions {m}")
                    break
            self.removal_phase = True
            self.root.after(500, self.ai_remove)
            return

        self.check_win_conditions()
        self.turn = "ai2" if self.turn == "ai" else "ai"
        self.root.after(500, self.ai_move)

    def check_win_conditions(self):
        p1 = numOfPieces(self.board, "1")
        p2 = numOfPieces(self.board, "2")
        
        # Win conditions
        if p1 < 3 and self.phase == "movement":
            messagebox.showinfo("Game Over", "AI2 wins! AI has fewer than 3 pieces.")
            self.save_game_history()
            self.root.quit()
        elif p2 < 3 and self.phase == "movement":
            messagebox.showinfo("Game Over", "AI wins! AI2 has fewer than 3 pieces.")
            self.save_game_history()
            self.root.quit()
            
        # Check if a player has no valid moves
        if self.phase == "movement":
            ai_moves = get_possible_moves_player(self.board, "1")
            ai2_moves = get_possible_moves_player(self.board, "2")
            
            if not ai_moves and self.turn == "ai":
                messagebox.showinfo("Game Over", "AI2 wins! AI has no valid moves.")
                self.save_game_history()
                self.root.quit()
            elif not ai2_moves and self.turn == "ai2":
                messagebox.showinfo("Game Over", "AI wins! AI2 has no valid moves.")
                self.save_game_history()
                self.root.quit()
    
    def save_game_history(self):
        """Save the game history to a file for later training"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        with open(f"game_history_{timestamp}.txt", "w") as f:
            for i, board_state in enumerate(self.game_history):
                f.write(f"Move {i}: {','.join(board_state)}\n")
        print(f"Game history saved to game_history_{timestamp}.txt")


def evaluate_with_randomness(board, randomness_factor=0.1):
    """Add a small random component to the evaluation to create variety"""
    base_score = evaluate_board(board, "2")  # Evaluate from AI2's perspective
    random_component = random.random() * randomness_factor * 100  # Random value up to 10% of typical eval
    return base_score + random_component


def evaluate_board(board, player):
    """More comprehensive evaluation function"""
    CAPTURE_BONUS = 200
    MILL_BONUS = 150
    POTENTIAL_MILL_BONUS = 75
    BLOCK_BONUS = 100
    MOBILITY_BONUS = 30
    CENTER_CONTROL_BONUS = 40
    PIECE_ADVANTAGE_BONUS = 20
    
    opponent = "1" if player == "2" else "2"
    score = 0
    
    # Piece advantage
    player_pieces = board.count(player)
    opponent_pieces = board.count(opponent)
    score += (player_pieces - opponent_pieces) * PIECE_ADVANTAGE_BONUS
    
    # Mills and potential mills
    for combo in mills:
        player_count = sum(1 for pos in combo if board[pos] == player)
        opponent_count = sum(1 for pos in combo if board[pos] == opponent)
        empty_count = sum(1 for pos in combo if board[pos] == "x")
        
        # Complete mills
        if player_count == 3:
            score += MILL_BONUS
        elif opponent_count == 3:
            score -= MILL_BONUS
        
        # Potential mills (2 pieces in line with empty spot)
        if player_count == 2 and empty_count == 1:
            score += POTENTIAL_MILL_BONUS
        if opponent_count == 2 and empty_count == 1:
            score -= POTENTIAL_MILL_BONUS * 1.2  # Higher priority to block opponent mills
    
    # Strategic positions (center and corners)
    strategic_positions = [4, 10, 13, 19]  # Center positions
    for pos in strategic_positions:
        if board[pos] == player:
            score += CENTER_CONTROL_BONUS
        elif board[pos] == opponent:
            score -= CENTER_CONTROL_BONUS * 0.8
    
    # Mobility (number of possible moves)
    player_moves = len(get_possible_moves_player(board, player))
    opponent_moves = len(get_possible_moves_player(board, opponent))
    score += (player_moves - opponent_moves) * MOBILITY_BONUS
    
    return score


if __name__ == "__main__":
    root = tk.Tk()
    game = MorrisGame(root)
    root.mainloop()