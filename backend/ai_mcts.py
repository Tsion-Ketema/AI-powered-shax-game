import random
import math
from .utils import mills, adjacentLocations, encode_board
import torch
import torch.nn as nn
import os

# === Neural Network Definitions ===
class ShaxNet(nn.Module):
    def __init__(self, output_size):
        super().__init__()
        self.fc1 = nn.Linear(24, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc_policy = nn.Linear(128, output_size)
        self.fc_value = nn.Linear(128, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        policy_logits = self.fc_policy(x)
        value = torch.tanh(self.fc_value(x))
        return policy_logits, value
    
# === Load Models ===
placement_model = ShaxNet(24)
movement_model = ShaxNet(24 * 24)
removal_model = ShaxNet(24)

# Dynamically locate model paths based on this file's location
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # One level up from /backend
placement_path = os.path.join(base_dir, 'placement_model.pth')
movement_path = os.path.join(base_dir, 'movement_model.pth')
removal_path = os.path.join(base_dir, 'removal_model.pth')

# Load models safely
placement_model.load_state_dict(torch.load(placement_path, map_location=torch.device('cpu')))
movement_model.load_state_dict(torch.load(movement_path, map_location=torch.device('cpu')))
removal_model.load_state_dict(torch.load(removal_path, map_location=torch.device('cpu')))

placement_model.eval()
movement_model.eval()
removal_model.eval()

class Node:
    def __init__(self, board, player, phase, move=None, parent=None):
        self.board = board.copy()
        self.player = player
        self.phase = phase  # Track phase as part of node state
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0

    def is_fully_expanded(self):
        if self.phase == 'movement':
            possible_moves = get_possible_moves_player(self.board, self.player)
        elif self.phase == 'removal':
            possible_moves = get_positions(self.board, self.player)
        else:
            possible_moves = get_possible_moves(self.board)
        return len(self.children) == len(possible_moves)

    def expand(self):
        if self.phase == 'movement':
            possible_moves = get_possible_moves_player(self.board, self.player)
        elif self.phase == 'removal':
            opponent = '1' if self.player == '2' else '2'
            possible_moves = get_positions(self.board, opponent)
            print(f"[DEBUG] Possible Moves for Removal Phase: {possible_moves}")
            model = removal_model
        else:
            possible_moves = get_possible_moves(self.board)
        if not possible_moves:
            return []
        # Load model and policy prediction
        board_tensor = encode_board(self.board)
        # model = movement_model if self.phase == "movement" else placement_model
        if self.phase == "movement":
            model = movement_model
        elif self.phase == "removal":
            model = removal_model
        else:
            model = placement_model
        with torch.no_grad():
            logits, _ = model(board_tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0).numpy()
        # Reorder moves based on predicted probabilities
        if self.phase == "movement":
            move_scores = {move: probs[move[0] * 24 + move[1]] for move in possible_moves}
        elif self.phase == "removal":
            move_scores = {move: probs[move] for move in possible_moves}
        else:
            move_scores = {move: probs[move] for move in possible_moves}
        sorted_moves = sorted(possible_moves, key=lambda m: -move_scores[m])
        for move in sorted_moves:
            if self.phase == "movement":
                new_board = apply_move(self.board, move[0], move[1], self.player)
            elif self.phase == "removal":
                new_board = apply_removal(self.board, move)
            else:
                new_board = apply_place(self.board, move, self.player)
            next_player = '1' if self.player == '2' else '2'
            child_node = Node(new_board, next_player, self.phase, move=move, parent=self)
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
    board_tensor = encode_board(node.board)
    if node.phase == "movement":
        model = movement_model
    elif node.phase == "removal":
        model = removal_model
    else:
        model = placement_model
    with torch.no_grad():
        _, value = model(board_tensor)
    return value.item()


def monte_carlo_tree_search(initial_board, player, phase, iterations=1000):
    root = Node(initial_board, player, phase)
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
         print("[DEBUG] No children generated for root node during removal phase.")
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

def apply_removal(board, move):
    print(f"[DEBUG] Applying Removal at Position: {move}")
    new_board = board[:]
    new_board[move] = 'x'
    return new_board



# def get_positions(board, player):
#     return [i for i in range(len(board)) if board[i] == player]


def get_positions(board, player):
    positions = [i for i in range(len(board)) if board[i] == player]
    print(f"[DEBUG] Positions for Player {player}: {positions}")
    print(f"[DEBUG] Board State: {board}")
    return positions


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