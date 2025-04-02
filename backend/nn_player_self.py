import torch
import torch.nn as nn
from .utils import encode_board

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



# Load Trained Models
placement_model = ShaxNet(24)
placement_model.load_state_dict(torch.load("placement_model.pth", map_location=torch.device('cpu')))
placement_model.eval()

movement_model = ShaxNet(24 * 24)
movement_model.load_state_dict(torch.load("movement_model.pth", map_location=torch.device('cpu')))
movement_model.eval()


from backend.utils import encode_board, adjacentLocations

def choose_move_from_nn(board,player, is_movement_phase=True):
    input_tensor = encode_board(board)

    if is_movement_phase:
        logits, _ = movement_model(input_tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        sorted_indices = torch.argsort(probs, descending=True).tolist()

        for index in sorted_indices:
            src = index // 24
            dst = index % 24

            if board[src] == player:      # Must own the piece
                continue
            if board[dst] != 'x':      # Destination must be empty
                continue
            if dst not in adjacentLocations(src):  # ❗ No jumping
                continue

            return (src, dst)

        return None  # No valid move found

    else:
        logits, _ = placement_model(input_tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        sorted_indices = torch.argsort(probs, descending=True).tolist()

        for move in sorted_indices:
            if board[move] == 'x':  # Find first empty spot
                return move

        return None  # No valid move


