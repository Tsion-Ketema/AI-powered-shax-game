from utils import *
from utils import adjacentLocations
import random


def get_possible_moves(board):
    moves = [i for i in range(len(board)) if board[i] == 'x']
    random.shuffle(moves)
    return moves


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
    random.shuffle(possible_moves)
    return possible_moves


def apply_place(board, move, player):
    new_board = board[:]
    new_board[move] = player
    return new_board

def apply_removal(board, move):
    new_board = board[:]
    new_board[move] = 'x'
    return new_board


def apply_move(board, pos1, pos2, player):
    new_board = board[:]
    new_board[pos1] = 'x'
    new_board[pos2] = player
    return new_board


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


def evaluate(board):
    CAPTURE_BONUS = 200
    BLOCK_BONUS = 100
    THREAT_PENALTY = 50       # Penalty for opponent's threats
    AI_THREAT_BONUS = 30      # Bonus for AI's own threats
    STRATEGIC_POSITION_BONUS = 20

    score = 0

    # Check mills and threats
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

    # Strategic positions (central spots, part of multiple mills)
    # Example for a standard Morris board
    strategic_positions = [4, 10, 13, 19]
    for pos in strategic_positions:
        if board[pos] == '2':
            score += STRATEGIC_POSITION_BONUS
        elif board[pos] == '1':
            score -= STRATEGIC_POSITION_BONUS

    # Piece advantage
    ai_pieces = board.count('2')
    opp_pieces = board.count('1')
    score += (ai_pieces - opp_pieces) * 10

    return score


def minimax(board, depth, alpha, beta, player, is_maximizing, phase):
    opponent = "2" if player == "1" else "1"
    possible_moves = get_possible_moves(board)
    if phase!="removal":
        if depth == 0 or not possible_moves:
            return evaluate(board), None
    

    if is_maximizing:
        if phase=="movement":
            max_eval = float('-inf')
            available_moves = get_possible_moves_player(board, player)
            best_move = None
            if available_moves:
                best_move = available_moves[0]
            for source, dest in available_moves:
                new_board = apply_move(board, source, dest, player)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, False, opponent, phase)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (source, dest)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        elif phase =="removal":
            max_eval = float('-inf')
            removal_pos = get_positions(board,player)
            best_move = removal_pos[0]
            print(f"initial move {best_move}")
            for move in removal_pos:
                new_board = apply_removal(board, move)
                eval = evaluate(new_board)
                print(f"current move {move} current eval {eval}")
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            max_eval = float('-inf')
            best_move = None
            for move in get_possible_moves(board):
                new_board = apply_place(board, move, player)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, False, opponent ,phase)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
    else:
        if phase=="movement":
            min_eval = float('inf')
            best_move = None
            for source, dest in get_possible_moves_player(board, opponent):
                new_board = apply_move(board, source, dest, opponent)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, True,player, phase)
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
                new_board = apply_place(board, move, opponent)
                eval, _ = minimax(new_board, depth-1, alpha,
                                  beta, True, player,phase)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
