import torch
import torch.nn as nn
from train_nn import ShaxNet
from utils import encode_board, adjacentLocations


# Load Trained Models
placement_model = ShaxNet(24)
placement_model.load_state_dict(torch.load("placement_model.pth", map_location=torch.device('cpu')))
placement_model.eval()

movement_model = ShaxNet(24 * 24)
movement_model.load_state_dict(torch.load("movement_model.pth", map_location=torch.device('cpu')))
movement_model.eval()

removal_model = ShaxNet(24)
removal_model.load_state_dict(torch.load("removal_model.pth", map_location=torch.device('cpu')))
removal_model.eval()



def choose_move_from_nn(board, phase, player):
    input_tensor = encode_board(board)
    opponent = "1" if player == "2" else "2"

    if phase == "movement":
        logits, _ = movement_model(input_tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        sorted_indices = torch.argsort(probs, descending=True).tolist()

        for index in sorted_indices:
            src = index // 24
            dst = index % 24

            if board[src] != player:        # Own piece
                continue
            if board[dst] != 'x':           # Destination must be empty
                continue
            if dst not in adjacentLocations(src):  # No jumping
                continue

            return (src, dst)
        return None

    elif phase == "removal":
        logits, _ = removal_model(input_tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        sorted_indices = torch.argsort(probs, descending=True).tolist()

        for move in sorted_indices:
            if board[move] == opponent:
                return move
        return None

    else:  # placement phase
        logits, _ = placement_model(input_tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        sorted_indices = torch.argsort(probs, descending=True).tolist()

        for move in sorted_indices:
            if board[move] == 'x':
                return move
        return None


