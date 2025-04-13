import random
import math
from utils import mills, adjacentLocations


class Node:
    def __init__(self, board, player, is_movement_phase, move=None, parent=None):
        self.board = board.copy()
        self.player = player
        self.is_movement_phase = is_movement_phase  # Track phase as part of node state
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0

    def is_fully_expanded(self):
        if self.is_movement_phase:
            possible_moves = get_possible_moves_player(self.board, self.player)
        else:
            possible_moves = get_possible_moves(self.board)
        return len(self.children) == len(possible_moves)

    def expand(self):
        if self.is_movement_phase:
            possible_moves = get_possible_moves_player(self.board, self.player)
        else:
            possible_moves = get_possible_moves(self.board)

        for move in possible_moves:
            if self.is_movement_phase:
                new_board = apply_move(self.board, move[0], move[1], self.player)
            else:
                new_board = apply_place(self.board, move, self.player)

            next_player = '1' if self.player == '2' else '2'
            # Phase transitions are handled externally - assume phase remains the same
            # unless your game has specific transition rules (not specified here)
            new_is_movement_phase = self.is_movement_phase  # Default: phase remains

            child_node = Node(new_board, next_player, new_is_movement_phase, move=move, parent=self)
            self.children.append(child_node)
        return self.children

    def best_child(self, exploration_weight=math.sqrt(2)):
        if not self.children:
            return None
        best_score = -float('inf')
        best_children = []
        for child in self.children:
            if child.visits == 0:
                return child
            exploitation = child.total_reward / child.visits
            exploration = exploration_weight * math.sqrt(math.log(self.visits) / child.visits)
            uct = exploitation + exploration
            if uct > best_score:
                best_score = uct
                best_children = [child]
            elif uct == best_score:
                best_children.append(child)
        return random.choice(best_children) if best_children else None


def simulate(node):
    current_board = node.board.copy()
    current_player = node.player
    is_movement_phase = node.is_movement_phase  # Use phase from node state
    max_depth = 100
    depth = 0

    while True:
        if depth >= max_depth:
            return evaluate(current_board)

        if is_movement_phase:
            possible_moves = get_possible_moves_player(current_board, current_player)
        else:
            possible_moves = get_possible_moves(current_board)

        if not possible_moves:
            return evaluate(current_board)

        if not node.is_movement_phase:
            # Prioritize strategic positions in placement phase
            strategic_moves = [move for move in possible_moves if move in [4, 10, 13, 19]]
            if strategic_moves:
                move = random.choice(strategic_moves)
            else:
                move = random.choice(possible_moves)
        else:
            move = random.choice(possible_moves)
        if is_movement_phase:
            new_board = apply_move(current_board, move[0], move[1], current_player)
        else:
            new_board = apply_place(current_board, move, current_player)
        current_board = new_board
        current_player = '1' if current_player == '2' else '2'
        # Phase remains the same during simulation (as per original rules)
        depth += 1


def monte_carlo_tree_search(initial_board, player, is_movement_phase, iterations=1000):
    root = Node(initial_board, player, is_movement_phase)
    for _ in range(iterations):
        node = root
        while node.is_fully_expanded() and node.children:
            node = node.best_child(exploration_weight=1.4)
        if not node.is_fully_expanded():
            node.expand()
            node = random.choice(node.children)
        simulation_result = simulate(node)
        while node is not None:
            if node.player == '2':
                node.total_reward += simulation_result
            else:
                node.total_reward -= simulation_result
            node.visits += 1
            node = node.parent
    if not root.children:
        return None
    best_child = max(root.children, key=lambda child: child.visits)
    return best_child.move


# Original functions remain unchanged
def get_possible_moves(board):
    return [i for i in range(len(board)) if board[i] == 'x']


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
        is_strategic = pos in [3, 4, 5, 6, 7, 8, 18, 19, 20]  # Example

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
    CAPTURE_BONUS = 100
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
            score -= CAPTURE_BONUS

        # Threats (2/3 in a mill with an open spot)
        has_open_spot = any(board[pos] == 'x' for pos in combo)
        if ai_count == 2 and has_open_spot:
            score += AI_THREAT_BONUS  # AI can complete a mill next move
        if opp_count == 2 and has_open_spot:
            score -= THREAT_PENALTY   # Opponent can complete a mill next move

    # Strategic positions (central spots, part of multiple mills)
    strategic_positions = [4, 10, 13, 19]  # Example for a standard Morris board
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