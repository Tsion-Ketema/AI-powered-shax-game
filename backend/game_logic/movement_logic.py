from backend.ai_logic.ai_minimax import minimax
from backend.ai_logic.ai_mcts import monte_carlo_tree_search
from backend.game_logic.utils import *
from tkinter import messagebox
import random


def perform_ai_movement(game):

    current_player = game.turn
    opponent = "2" if current_player == "1" else "1"
    ai_type = game.ai_config[current_player]

    moves = get_possible_moves_player(game.board, current_player)
    if not moves:
        game.turn = opponent
        game.blocked = True
        game.ai_forced_move_no_capture()
        return

    if ai_type == "mcts":
        source, dest = monte_carlo_tree_search(game.board, current_player, game.phase)
        game.board[source] = 'x'
        game.board[dest] = current_player
        game.update_board()

        if isMill(dest, game.board):
            game.removal_phase = True
            print(f"{current_player} formed a mill")
            game.turn = current_player  # AI gets to remove
            game.root.after(500, game.ai_remove)
        else:
            print(f"{current_player} moves from {source} to {dest}")
            game.check_win_conditions()
            game.turn = opponent
            game.root.after(500, game.ai_move)
        return

    elif ai_type == "human":
        print("Waiting for human to move...")
        return

    elif ai_type == "mwor":
        evaluation, move = minimax(game.board, game.depth, game.alpha, game.beta, current_player, True, True)
        if move:
            source, dest = move
            game.board[source] = 'x'
            game.board[dest] = current_player
            game.update_board()

            if isMill(dest, game.board):
                print(f"{current_player} formed a mill")
                game.removal_phase = True
                game.turn = current_player  # AI gets to remove
                game.root.after(500, game.ai_remove)
            else:
                game.check_win_conditions()
                game.turn = opponent
                print(f"{current_player} makes a move from {source} to {dest}")
                game.root.after(500, game.ai_move)
        return

    def try_form_mill(game, moves, player, opponent):
        for src, dest in moves:
            game.board[src] = "x"
            game.board[dest] = player
            if isMill(dest, game.board):
                game.update_board()
                game.removal_phase = True
                game.root.after(500, game.ai_remove)
                return True
            game.board[src] = player
            game.board[dest] = "x"
        return False

    def block_backforth_threat(game, moves, player, opponent):
        for src, dest in moves:
            game.board[src] = "x"
            game.board[dest] = player
            for mill in mills:
                if any(game.board[p] == opponent for p in mill) and dest in mill:
                    opponent_positions = [p for p in mill if game.board[p] == opponent]
                    empty_positions = [p for p in mill if game.board[p] == "x"]
                    if len(opponent_positions) == 2 and len(empty_positions) == 1:
                        game.board[src] = "x"
                        game.board[dest] = player
                        if isMill(dest, game.board):
                            game.update_board()
                            game.removal_phase = True
                            game.root.after(500, game.ai_remove)
                            return True
                        game.update_board()
                        game.turn = opponent
                        game.root.after(500, game.ai_move)
                        return True
            game.board[src] = player
            game.board[dest] = "x"
        return False

    def disrupt_opponent_double_threat(game, moves, player, opponent):
        for src, dest in moves:
            game.board[src] = "x"
            game.board[dest] = player
            blocked = False
            for pos, piece in enumerate(game.board):
                if piece == opponent:
                    threat_count = 0
                    for mill in mills:
                        if pos in mill and all(game.board[p] in [opponent, "x"] for p in mill):
                            threat_count += 1
                    if threat_count >= 2 and dest == pos:
                        blocked = True
                        break
            game.board[src] = player
            game.board[dest] = "x"
            if blocked:
                game.board[src] = "x"
                game.board[dest] = player
                game.update_board()
                game.turn = opponent
                game.root.after(500, game.ai_move)
                return True
        return False

    def fallback_minimax_move(game, moves, player, opponent):
        evaluation, move = minimax(game.board, game.depth, game.alpha, game.beta, player, True, True)
        if move:
            source, dest = move
            game.board[source] = 'x'
            game.board[dest] = player
            game.update_board()
            game.check_win_conditions()
            game.turn = opponent
            game.root.after(500, game.ai_move)
            return True
        return False

    if ai_type == "mwr":
        for strategy in [
            try_form_mill,
            block_backforth_threat,
            disrupt_opponent_double_threat
        ]:
            if strategy(game, moves, current_player, opponent):
                return

        # Fallback to minimax with rules
        fallback_minimax_move(game, moves, current_player, opponent)


def handle_human_movement(game, pos):
    if game.ai_config[game.turn] != "human" or game.removal_phase:
        return

    player = game.human_player

    if not get_possible_moves_player(game.board, player):
        messagebox.showinfo("Blocked", "You are blocked. AI will move.")
        game.blocked = True
        game.root.after(500, lambda: game.ai_move())
        return

    if game.selected is None:
        if game.board[pos] == player:
            game.selected = pos
            x, y = game.pos_coords[pos]
            game.canvas.create_oval(x - 12, y - 12, x + 12, y + 12, outline="red", width=3, tag="highlight")
        else:
            messagebox.showinfo("Invalid Selection", "Select one of your own pieces.")
    else:
        if game.board[pos] != "x" or pos not in adjacentLocations(game.selected):
            messagebox.showinfo("Invalid Move", "Invalid destination.")
        else:
            game.board[game.selected] = "x"
            game.board[pos] = player
            print(f"Human moved from {game.selected} to {pos}")
            game.update_board()
            if isMill(pos, game.board):
                messagebox.showinfo("Mill Formed", "You formed a mill! Remove one of AI's pieces.")
                game.removal_phase = True
            else:
                game.check_win_conditions()
                game.turn = game.ai_player
                game.root.after(500, lambda: game.ai_move())

        game.canvas.delete("highlight")
        game.selected = None


