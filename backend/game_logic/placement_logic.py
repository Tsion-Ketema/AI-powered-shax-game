from backend.game_logic.utils import *
from backend.game_logic.opening_logic import perform_ai_opening
from backend.ai_logic.ai_minimax import minimax
from backend.ai_logic.ai_mcts  import monte_carlo_tree_search



from backend.game_logic import opening_logic
def perform_ai_placement(game):
    move = None
    current_player = game.turn
    ai_type = game.ai_config[current_player]

    if ai_type == "mwor" or "mwr":
        evaluation, move = minimax(
            game.board, game.depth, game.alpha, game.beta,
            current_player, True, False
        )
    elif ai_type == "mcts":
        move = monte_carlo_tree_search(game.board, current_player, game.phase)
    elif ai_type == "human":
        print("Waiting for human to place...") 
        return  

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
        game.handle_opening_phase()
