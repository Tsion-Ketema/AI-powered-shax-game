from copy import deepcopy

# --- Game Rules ---
mills = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14],
    [15, 16, 17], [18, 19, 20], [21, 22, 23], [0, 9, 21], [3, 10, 18],
    [6, 11, 15], [1, 4, 7], [16, 19, 22], [8, 12, 17], [5, 13, 20], [2, 14, 23]
]

adjacent = {
    0: [1, 9], 1: [0, 2, 4], 2: [1, 14], 3: [4, 10], 4: [1, 3, 5, 7],
    5: [4, 13], 6: [7, 11], 7: [4, 6, 8], 8: [7, 12], 9: [0, 10, 21],
    10: [3, 9, 11, 18], 11: [6, 10, 15], 12: [8, 13, 17], 13: [5, 12, 14, 20],
    14: [2, 13, 23], 15: [11, 16], 16: [15, 17, 19], 17: [12, 16], 18: [10, 19],
    19: [16, 18, 20, 22], 20: [13, 19], 21: [9, 22], 22: [19, 21, 23], 23: [14, 22]
}

# --- Placement Phase Tracking ---
placement_mills = {"human": 0, "ai": 0}
first_mill = None  # Tracks who formed the first mill first (human/ai)

# --- Helper Functions ---


def adjacentLocations(position):
    return adjacent[position]


def check_next_mill(position, board, player):
    for mill in mills:
        if position in mill:
            if all(board[i] == player for i in mill):
                return True
    return False


def isMill(position, board):
    p = board[position]
    return p != 'x' and check_next_mill(position, board, p)


def numOfPieces(board, player):
    return board.count(player)


def remove_non_mill_piece(board, player):
    """Removes one opponent piece that is not in a mill."""
    opponent = "2" if player == "1" else "1"
    for pos in range(len(board)):
        if board[pos] == opponent and not isMill(pos, board):
            board[pos] = "x"
            return True  # Successfully removed
    return False  # No valid piece to remove


def determine_opening_order():
    """Determine the order of removal in the Opening Phase."""
    global first_mill, placement_mills
    if placement_mills["human"] > 0 and placement_mills["ai"] == 0:
        return ["human", "ai"]  # Human removes first
    elif placement_mills["ai"] > 0 and placement_mills["human"] == 0:
        return ["ai", "human"]  # AI removes first
    elif first_mill == "human":
        return ["human", "ai"]  # Human made first mill, removes first
    elif first_mill == "ai":
        return ["ai", "human"]  # AI made first mill, removes first
    return ["ai", "human"]  # Default case (if no mills, second player starts)


def removePiece(board, player):
    """Removes one opponent piece not in a mill."""
    opponent = "2" if player == "1" else "1"
    for pos in range(len(board)):
        if board[pos] == opponent and not isMill(pos, board):
            board[pos] = "x"
            return True  # Piece successfully removed
    return False  # No removable piece found

# --- Movement Handling ---


def possibleMoves_stage2(board, player):
    """Returns possible moves for the movement phase (adjacent moves)."""
    board_list = []
    for i in range(len(board)):
        if board[i] == player:
            for pos in adjacentLocations(i):
                if board[pos] == 'x':
                    board_copy = deepcopy(board)
                    board_copy[i] = 'x'
                    board_copy[pos] = player
                    if isMill(pos, board_copy):
                        removePiece(board_copy, player)
                    board_list.append(board_copy)
    return board_list


def possibleMoves_stage3(board, player):
    """Returns possible moves when a player has only 3 pieces left (flying rule)."""
    board_list = []
    for i in range(len(board)):
        if board[i] == player:
            for j in range(len(board)):
                if board[j] == 'x':
                    board_copy = deepcopy(board)
                    board_copy[i] = 'x'
                    board_copy[j] = player
                    if isMill(j, board_copy):
                        removePiece(board_copy, player)
                    board_list.append(board_copy)
    return board_list


def possibleMoves_stage2or3(board, player):
    """Chooses between stage 2 (adjacent moves) and stage 3 (flying) based on piece count."""
    return possibleMoves_stage3(board, player) if numOfPieces(board, player) == 3 else possibleMoves_stage2(board, player)

# --- AI Implementation with Minimax ---


class Evaluate:
    def __init__(self):
        self.evaluate = 0
        self.board = []


alpha = float('-inf')
beta = float('inf')
depth = 2
CAPTURE_BONUS = 100
THREAT_PENALTY = 50


def minimax(board, depth, alpha, beta, is_maximizing, is_movement_phase):
    """Minimax algorithm with alpha-beta pruning."""
    possible_moves = get_possible_moves(board)
    if depth == 0 or not possible_moves:
        return evaluate(board), None

    if is_maximizing:
        if is_movement_phase:
            max_eval = float('-inf')
            best_move = None
            for source, dest in get_possible_moves_player(board, '2'):
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
            min_eval = float('+inf')
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
            min_eval = float('+inf')
            best_move = None
            for move in possible_moves:
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


def get_possible_moves(board):
    """Returns possible placements for AI during placement phase."""
    return [i for i in range(len(board)) if board[i] == 'x']


def get_possible_moves_player(board, player):
    possible_moves = []
    for i in range(len(board)):
        if board[i] == player:  # Check if the current position belongs to the player
            adjacent = adjacentLocations(i)  # Get adjacent positions
            for j in adjacent:
                if board[j] == 'x':  # Check if the adjacent position is empty
                    # Append (source, destination) tuple
                    possible_moves.append((i, j))
    return possible_moves


def apply_place(board, move, player):
    """Applies a move for AI during placement phase."""
    new_board = board[:]
    new_board[move] = player
    return new_board


def apply_move(board, pos1, pos2, player):
    new_board = board[:]
    new_board[pos1] = 'x'
    new_board[pos2] = player
    return new_board


def evaluate(board):
    """Evaluates the board based on piece count and mill formations."""
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

    return score  # Only return the score, no extra None
