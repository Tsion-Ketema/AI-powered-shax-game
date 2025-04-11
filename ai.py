from utils import *
from utils import adjacentLocations
import random


def get_possible_moves(board):
    return [i for i in range(len(board)) if board[i] == 'x']


def get_positions(board, player):
    return [i for i in range(len(board)) if board[i] == player]


def get_possible_moves_player(board, player):

    possible_moves = []
    for i in range(len(board)):
        if board[i] == player:
            adjacent = adjacentLocations(i)
            for j in adjacent:
                if board[j] == 'x':
                    possible_moves.append((i, j))
    return possible_moves


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


def select_capture_position(board):
    # Prioritize removing opponent's mills or strategic positions
    opponent_pieces = [i for i in range(len(board)) if board[i] == '1']
    best_pos = None
    best_score = -float('inf')

    for pos in opponent_pieces:
        # Check if the piece is part of an existing mill
        in_mill = any(
            all(board[p] == '1' for p in combo)
            for combo in mills if pos in combo
        )
        # Check if the position is strategic
        is_strategic = pos in [1, 3, 4, 5, 7, 16, 18, 19, 20, 22]  # Example

        score = 0
        if in_mill:
            score += 100
        if is_strategic:
            score += 50

        if score > best_score:
            best_score = score
            best_pos = pos

    return best_pos if best_pos else random.choice(opponent_pieces)

# Here i completely change the evaluation and the minimax working logic


def evaluate(board):
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
        ai_count = sum(1 for pos in combo if board[pos] == '2')
        opp_count = sum(1 for pos in combo if board[pos] == '1')

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
                    if board[shared_pos] == '2':  # AI controls shared position
                        score += DOUBLE_THREAT_BONUS

    # 3. Strategic Positions
    strategic_positions = [4, 10, 13, 19]  # Example strategic positions
    for pos in strategic_positions:
        if board[pos] == '2':
            score += STRATEGIC_POSITION_BONUS
        elif board[pos] == '1':
            score -= STRATEGIC_POSITION_BONUS

    # 4. Mobility
    ai_moves = len(get_possible_moves_player(board, '2'))
    opp_moves = len(get_possible_moves_player(board, '1'))
    score += (ai_moves - opp_moves) * MOBILITY_BONUS

    # 5. Piece Advantage
    ai_pieces = board.count('2')
    opp_pieces = board.count('1')
    score += (ai_pieces - opp_pieces) * 10

    return score


def minimax(board, depth, alpha, beta, is_maximizing, is_movement_phase):
    # Base case: Evaluate the board if depth is 0 or no moves are possible
    possible_moves = get_possible_moves(board)
    if depth == 0 or not possible_moves:
        return evaluate(board), None

    if is_maximizing:
        # Maximizing player (AI)
        if is_movement_phase:
            max_eval = float('-inf')
            best_move = None
            available_moves = get_possible_moves_player(board, '2')
            if available_moves:
                best_move = available_moves[0]
            for source, dest in available_moves:
                # Apply the move
                new_board = apply_move(board, source, dest, '2')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, False, is_movement_phase)
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
            for move in get_possible_moves(board):
                # Apply the placement
                new_board = apply_place(board, move, '2')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, False, is_movement_phase)
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
            for source, dest in get_possible_moves_player(board, '1'):
                # Apply the move
                new_board = apply_move(board, source, dest, '1')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, True, is_movement_phase)
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
            for move in get_possible_moves(board):
                # Apply the placement
                new_board = apply_place(board, move, '1')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, True, is_movement_phase)
                # Update the best move
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                # Alpha-beta pruning
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
