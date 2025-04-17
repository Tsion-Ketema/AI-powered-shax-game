from backend.game_logic.utils import *
import random

def apply_place(board, move, player):
    new_board = board[:]
    new_board[move] = player
    return new_board


def apply_move(board, pos1, pos2, player):
    new_board = board[:]
    new_board[pos1] = 'x'
    new_board[pos2] = player
    return new_board


def opponent_can_form_mill(board_state):
    """
    Check if the opponent (player '1') can form a mill on the given board state.
    """
    for pos in range(len(board_state)):
        if board_state[pos] == 'x':  # empty spot
            board_state[pos] = '1'   # simulate placing a human piece
            if isMill(pos, board_state):
                board_state[pos] = 'x'  # revert
                return True
            board_state[pos] = 'x'  # revert
    return False

def evaluate(board, player):
    opponent = "2" if player == "1" else "1"
    CAPTURE_BONUS = 100
    BLOCK_BONUS = 100
    THREAT_PENALTY = 50       # Penalty for opponent's threats
    AI_THREAT_BONUS = 30      # Bonus for AI's own threats
    STRATEGIC_POSITION_BONUS = 20
    MOBILITY_BONUS = 5        # Bonus for each possible move
    DOUBLE_THREAT_BONUS = 40  # Bonus for creating double threats

    score = 0

    # 1. Mills and Threats
    for combo in mills:
        ai_count = sum(1 for pos in combo if board[pos] == player)
        opp_count = sum(1 for pos in combo if board[pos] == opponent)

        # Completed mills
        if ai_count == 3:
            score += CAPTURE_BONUS
        elif opp_count == 3:
            score -= BLOCK_BONUS

        # Threats (2/3 in a mill with an open spot)
        has_open_spot = any(board[pos] == 'x' for pos in combo)
        if ai_count == 2 and has_open_spot:
            score += AI_THREAT_BONUS  # AI can complete a mill next move
        if opp_count == 2 and has_open_spot:
            score -= THREAT_PENALTY   # Opponent can complete a mill next move

    # 2. Double Threats
    for combo1 in mills:
        for combo2 in mills:
            if combo1 != combo2:
                shared_positions = set(combo1) & set(combo2)
                if len(shared_positions) == 1:  # One shared position
                    shared_pos = list(shared_positions)[0]
                    if board[shared_pos] == player:  # AI controls shared position
                        score += DOUBLE_THREAT_BONUS

    # 3. Mobility
    ai_moves = len(get_possible_moves_player(board, player))
    opp_moves = len(get_possible_moves_player(board, opponent))
    score += (ai_moves - opp_moves) * MOBILITY_BONUS

    # 5. Piece Advantage
    ai_pieces = board.count(player)
    opp_pieces = board.count(opponent)
    score += (ai_pieces - opp_pieces) * 10

    return score


def minimax(board, depth, alpha, beta, player, is_maximizing, is_movement_phase):
    # Base case: Evaluate the board if depth is 0 or no moves are possible
    opponent = "2" if player == "1" else "1"
    possible_moves = get_possible_moves(board)
    if depth == 0 or not possible_moves:
        noise = random.uniform(-0.01, 0.01)
        return evaluate(board, player) + noise, None

    if is_maximizing:
        # Maximizing player (AI)
        if is_movement_phase:
            max_eval = float('-inf')
            best_move = None
            available_moves = get_possible_moves_player(board, player)
            random.shuffle(available_moves)
            if available_moves:
                best_move = available_moves[0]
            for source, dest in available_moves:
                # Apply the move
                new_board = apply_move(board, source, dest, player)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, opponent, False, is_movement_phase)
                # Update the best move
                if eval > max_eval:
                    max_eval = eval
                    best_move = (source, dest)
                # Alpha-beta pruning
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            max_eval = float('-inf')
            best_move = None
            moves = get_possible_moves(board)
            random.shuffle(moves)
            for move in moves:
                # Apply the placement
                new_board = apply_place(board, move, player)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, opponent, False, is_movement_phase)
                # Update the best move
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                # Alpha-beta pruning
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
    else:
        # Minimizing player (Human)
        if is_movement_phase:
            min_eval = float('inf')
            best_move = None
            available_moves = get_possible_moves_player(board, opponent)
            random.shuffle(available_moves)
            for source, dest in available_moves:
                # Apply the move
                new_board = apply_move(board, source, dest, opponent)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, player, True, is_movement_phase)
                # Update the best move
                if eval < min_eval:
                    min_eval = eval
                    best_move = (source, dest)
                # Alpha-beta pruning
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            moves = get_possible_moves(board)
            random.shuffle(moves)
            for move in moves:
                # Apply the placement
                new_board = apply_place(board, move, opponent)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, player, True, is_movement_phase)
                # Update the best move
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                # Alpha-beta pruning
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
