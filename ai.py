from utils import *
from utils import adjacentLocations


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


def evaluate(board):
    CAPTURE_BONUS = 100
    THREAT_PENALTY = 50
    score = 0
    for combo in mills:
        ai_count = sum(1 for pos in combo if board[pos] == '2')
        opp_count = sum(1 for pos in combo if board[pos] == '1')

        if ai_count == 3:
            score += CAPTURE_BONUS
        elif opp_count == 3:
            score -= CAPTURE_BONUS
        elif opp_count == 2 and any(board[pos] == 'x' for pos in combo):
            score -= THREAT_PENALTY

    return score


def minimax(board, depth, alpha, beta, is_maximizing, is_movement_phase):
    possible_moves = get_possible_moves(board)
    if depth == 0 or not possible_moves:
        return evaluate(board), None

    if is_maximizing:
        if is_movement_phase:
            max_eval = float('-inf')
            available_moves = get_possible_moves_player(board, '2')
            best_move = None
            if available_moves:
                best_move = available_moves[0]
            for source, dest in available_moves:
                new_board = apply_move(board, source, dest, '2')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, False, is_movement_phase)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (source, dest)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            max_eval = float('-inf')
            best_move = None
            for move in get_possible_moves(board):
                new_board = apply_place(board, move, '2')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, False, is_movement_phase)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
    else:
        if is_movement_phase:
            min_eval = float('inf')
            best_move = None
            for source, dest in get_possible_moves_player(board, '1'):
                new_board = apply_move(board, source, dest, '1')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, True, is_movement_phase)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (source, dest)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in get_possible_moves(board):
                new_board = apply_place(board, move, '1')
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, True, is_movement_phase)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
