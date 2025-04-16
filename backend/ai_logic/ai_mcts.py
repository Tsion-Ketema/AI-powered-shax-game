import random
import math
from backend.game_logic.utils import *


class Node:
    def __init__(self, board, player, phase, move=None, parent=None):
        self.board = board.copy()
        self.player = player
        self.phase = phase  # 'placement', 'movement', or 'removal'
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0

    def is_fully_expanded(self):
        if self.phase == 'movement':
            possible_moves = get_possible_moves_player(self.board, self.player)
        elif self.phase == 'removal':
            opponent = '2' if self.player == '1' else '1'
            possible_moves = [i for i in range(
                24) if self.board[i] == opponent]
        else:  # placement
            possible_moves = get_possible_moves(self.board)

        # return len(self.children) == len(possible_moves)
        existing_moves = set(child.move for child in self.children)
        return all(move in existing_moves for move in possible_moves)

    def expand(self):
        if self.phase == 'movement':
            possible_moves = get_possible_moves_player(self.board, self.player)
        elif self.phase == 'removal':
            opponent = '2' if self.player == '1' else '1'
            possible_moves = [i for i in range(
                24) if self.board[i] == opponent]
        else:  # placement
            possible_moves = get_possible_moves(self.board)

        for move in possible_moves:
            if self.phase == 'movement':
                new_board = apply_move(
                    self.board, move[0], move[1], self.player)
            elif self.phase == 'removal':
                new_board = self.board[:]
                new_board[move] = 'x'
            else:  # placement
                new_board = apply_place(self.board, move, self.player)

            next_player = '1' if self.player == '2' else '2'
            # Phase doesn't change during expansion
            child_node = Node(new_board, next_player,
                              self.phase, move=move, parent=self)
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
            exploration = exploration_weight * \
                math.sqrt(math.log(self.visits) / child.visits)
            uct = exploitation + exploration
            if uct > best_score:
                best_score = uct
                best_children = [child]
            elif uct == best_score:
                best_children.append(child)
        return random.choice(best_children) if best_children else None


def simulate(node):
    board = node.board.copy()
    current_player = node.player
    phase = node.phase
    max_depth = 30
    depth = 0

    while depth < max_depth:
        if phase == 'movement':
            moves = get_possible_moves_player(board, current_player)
            if not moves:
                break
            move = random.choice(moves)
            board = apply_move(board, move[0], move[1], current_player)

        elif phase == 'placement':
            moves = get_possible_moves(board)
            if not moves:
                break
            move = random.choice(moves)
            board = apply_place(board, move, current_player)

        elif phase == 'removal':
            opponent = '2' if current_player == '1' else '1'
            moves = [i for i in range(24) if board[i] == opponent]
            if not moves:
                break
            move = random.choice(moves)
            board[move] = 'x'

        current_player = '1' if current_player == '2' else '2'
        depth += 1

    return evaluate(board, current_player)


def monte_carlo_tree_search(initial_board, player, phase, iterations=1000):
    root = Node(initial_board, player, phase)
    for _ in range(iterations):
        node = root
        while node.is_fully_expanded() and node.children:
            node = node.best_child(exploration_weight=1.4)
        if not node.is_fully_expanded():
            node.expand()
            if node.children:
                node = random.choice(node.children)
        simulation_result = simulate(node)
        while node is not None:
            if node.player == player:
                node.total_reward += simulation_result
            else:
                node.total_reward -= simulation_result
            node.visits += 1
            node = node.parent

    if not root.children:
        return None

    best_child = max(root.children, key=lambda c: c.visits)

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


def select_capture_position(board, player):
    # Prioritize removing opponent's mills or strategic positions
    opponent = "2" if player == "1" else "1"
    opponent_pieces = [i for i in range(len(board)) if board[i] == opponent]
    best_pos = None
    best_score = -float('inf')

    for pos in opponent_pieces:
        # Check if the piece is part of an existing mill
        in_mill = any(
            all(board[p] == opponent for p in combo)
            for combo in mills if pos in combo
        )

        score = 0
        if in_mill:
            score += 100

        if score > best_score:
            best_score = score
            best_pos = pos

    return best_pos if best_pos else random.choice(opponent_pieces)


def evaluate(board, player):
    opponent = "2" if player == "1" else "1"
    CAPTURE_BONUS = 100
    THREAT_PENALTY = 50       # Penalty for opponent's threats
    AI_THREAT_BONUS = 30      # Bonus for AI's own threats
    STRATEGIC_POSITION_BONUS = 20

    score = 0

    # Check mills and threats
    for combo in mills:
        ai_count = sum(1 for pos in combo if board[pos] == player)
        opp_count = sum(1 for pos in combo if board[pos] == opponent)

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
    # Example for a standard Morris board
    strategic_positions = [4, 10, 13, 19]
    for pos in strategic_positions:
        if board[pos] == player:
            score += STRATEGIC_POSITION_BONUS
        elif board[pos] == opponent:
            score -= STRATEGIC_POSITION_BONUS

    # Piece advantage
    ai_pieces = board.count(player)
    opp_pieces = board.count(opponent)
    score += (ai_pieces - opp_pieces) * 10

    return score
