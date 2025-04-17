from backend.game_logic.utils import *
from backend.game_logic.opening_logic import perform_ai_opening
from backend.ai_logic.ai_minimax import minimax
from backend.ai_logic.ai_mcts import monte_carlo_tree_search
from backend.game_logic.removal_logic import handle_human_removal

def perform_ai_placement(game):
    current_player = game.turn
    ai_type = game.ai_config[current_player]

    if ai_type in ("mwor", "mwr"):
        use_rules = ai_type == "mwr"
        is_movement_phase = game.phase == "movement"
        evaluation, move = minimax(
            game.board, game.depth, game.alpha, game.beta,
            current_player, True, is_movement_phase
        )
    elif ai_type == "mcts":
        move = monte_carlo_tree_search(game.board, current_player, game.phase)

    game.board[move] = current_player

    if isMill(move, game.board):
        if game.first_mill is None:
            game.first_mill = current_player

    game.placement_moves += 1
    game.update_board()

    if game.placement_moves < 24:
        game.turn = "1" if current_player == "2" else "2"
        if game.ai_config[game.turn] != "human":
            game.root.after(500, game.ai_place)
    else:
        game.phase = "opening"
        game.removal_phase = True
        game.ai_opening()


def handle_human_placement(game, pos):
    current_player = game.turn

    if game.board[pos] != "x":
        print("Invalid move! Position already occupied.")
        return

    game.board[pos] = current_player

    if isMill(pos, game.board) and game.first_mill is None:
        game.first_mill = current_player

    game.placement_moves += 1
    game.update_board()

    if game.placement_moves < 24:
        game.turn = "1" if current_player == "2" else "2"
        if game.ai_config[game.turn] != "human":
            game.root.after(500, game.ai_place)

    else:
        game.phase = "opening"
        game.removal_phase = True
        game.turn = game.human_player  # Ensure human gets their turn to remove
        if game.ai_config[game.turn] == "human":
            game.canvas.bind("<Button-1>", game.handle_click)  # ✅ Allow human to click
        print("Waiting for human to remove a piece (or 2nd one)...")

