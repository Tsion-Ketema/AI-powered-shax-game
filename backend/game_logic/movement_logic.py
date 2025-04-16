from backend.ai_logic.ai_minimax import minimax
from backend.ai_logic.ai_mcts  import monte_carlo_tree_search
from backend.game_logic.utils import *

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
        game.check_win_conditions()
        game.turn = opponent
        game.root.after(500, game.ai_move)
        return

    if ai_type == "human":
        print("Waiting for human to move...")
        return

    if ai_type == "mwor":
        evaluation, move = minimax(game.board, game.depth, game.alpha, game.beta, current_player, True, False)
        if move:
            source, dest = move
            game.board[source] = 'x'
            game.board[dest] = current_player
            game.update_board()
            game.check_win_conditions()
            game.turn = opponent
            game.root.after(500, game.ai_move)
        return

    elif ai_type == "mwr":
        for strategy in [
            try_form_mill,
            block_backforth_threat,
            disrupt_opponent_double_threat
        ]:
            if strategy(game, moves, current_player, opponent):
                return

        # Fallback to minimax with rules
        fallback_minimax_move(game, moves, current_player, opponent)

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
