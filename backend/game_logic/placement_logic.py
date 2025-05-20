from backend.game_logic.utils import *
from backend.game_logic.opening_logic import perform_ai_opening
from backend.ai_logic.ai_minimax import minimax
from backend.ai_logic.ai_mcts import monte_carlo_tree_search
from backend.game_logic.removal_logic import handle_human_removal
from tkinter import messagebox

# Handles AI piece placement during the placement phase


def handle_ai_placement(game):
    current_player = game.turn
    ai_type = game.ai_config[current_player]

    # Safety check: prevent placing after all 24 pieces are used
    if game.placement_moves >= 24:
        print("Placement phase should be over, skipping.")
        return

    move = None

    # Choose move based on AI type
    if ai_type in ("mwor", "mwr"):
        _, move = minimax(
            game.board, game.depth, game.alpha, game.beta,
            current_player, True, is_movement_phase=False
        )
    elif ai_type == "mcts":
        move = monte_carlo_tree_search(game.board, current_player, game.phase)

    # Validate selected move
    if move is None or game.board[move] != "x":
        print(f"[ERROR] AI {ai_type} returned invalid move: {move}")
        return

    # Apply move to the board
    game.board[move] = current_player
    print(f"[AI Placement] Player {current_player} placed at {move}")

    # If this is the first mill formed, record it for opening phase
    if isMill(move, game.board) and game.first_mill is None:
        game.first_mill = current_player
        print(f"[Mill] Player {current_player} formed the first mill")

    # Update board and game state
    game.placement_moves += 1
    game.update_board()

    # If placement phase is not over, switch turns
    if game.placement_moves < 24:
        game.turn = "2" if current_player == "1" else "1"
        if game.ai_config[game.turn] == "human":
            game.canvas.bind("<Button-1>", game.handle_click)
        else:
            game.root.after(500, game.ai_place)
    else:
        # Transition to opening phase
        game.phase = "opening"
        game.removal_phase = True
        game.turn = game.first_mill or "1"

        if game.ai_config[game.turn] == "human":
            print("Waiting for human to remove a piece")
            game.canvas.bind("<Button-1>", game.handle_click)
        else:
            game.root.after(500, game.ai_remove)

# Handles human piece placement during the placement phase


def handle_human_placement(game, pos):
    # Check if it's human's turn
    if game.ai_config[game.turn] != "human":
        print("It's not the human's turn to place.")
        return
    current_player = game.turn

    # Validate if selected position is empty
    if game.board[pos] != "x":
        print("Invalid move! Position already occupied.")
        return

    # Place the piece
    game.board[pos] = current_player

    # Record first mill if applicable
    if isMill(pos, game.board) and game.first_mill is None:
        game.first_mill = current_player

    # Update board state
    game.placement_moves += 1
    game.update_board()

    # If placement not complete, switch turns
    if game.placement_moves < 24:
        game.turn = "1" if current_player == "2" else "2"
        if game.ai_config[game.turn] != "human":
            game.root.after(500, game.ai_place)
    else:
        # Transition to opening phase
        game.phase = "opening"
        game.removal_phase = True
        game.turn = game.first_mill if game.first_mill else (
            "2" if current_player == "1" else "1")

        if game.ai_config[game.turn] == "human":
            print("Waiting for human to remove a piece")
            game.canvas.bind("<Button-1>", game.handle_click)
        else:
            game.root.after(500, game.ai_remove)
