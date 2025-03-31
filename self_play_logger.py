import json
import os
from backend.ai import monte_carlo_tree_search, apply_place, apply_move, get_possible_moves_player, get_possible_moves
from backend.nn_player import choose_move_from_nn
from backend.utils import adjacentLocations, isMill, numOfPieces, encode_board

LOG_DIR = "game_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def play_game(game_id=0, iterations=2000):
    board = ['x'] * 24
    phase = 'placement'
    player = '1'
    placement_moves = 0
    game_data = []

    while True:
        state = [0 if x == 'x' else int(x) for x in board]
        is_movement_phase = (phase == 'movement')

        if phase == 'placement':
            move = monte_carlo_tree_search(board, player, False, iterations)
            if move is None:
                break
            board = apply_place(board, move, player)
            reward = 2 if isMill(move, board) else 0
            placement_moves += 1
            if placement_moves >= 24:
                phase = 'movement'
        else:
            moves = get_possible_moves_player(board, player)
            if not moves:
                reward = -1
                done = True
                game_data.append({
                    "state": state,
                    "player": player,
                    "action": None,
                    "reward": reward,
                    "next_state": [0 if x == 'x' else int(x) for x in board],
                    "done": done,
                    "phase": phase
                })
                break
            move = choose_move_from_nn(board, is_movement_phase=True)

            if move is None:
                break  # No legal move
            src, dst = move

            # Ensure it's a valid adjacent move
            if dst not in adjacentLocations(src):
                continue  # ❌ Skip jumping moves

            board = apply_move(board, src, dst, player)
            reward += 3 if isMill(dst, board) else 0

        next_state = [0 if x == 'x' else int(x) for x in board]
        done = numOfPieces(board, '1') < 3 or numOfPieces(board, '2') < 3

        game_data.append({
            "state": state,
            "player": player,
            "action": move,
            "reward": reward,
            "next_state": next_state,
            "done": done,
            "phase": phase
        })

        if done:
            break

        player = '2' if player == '1' else '1'

    with open(os.path.join(LOG_DIR, f"game_{game_id}.jsonl"), "w") as f:
        for step in game_data:
            f.write(json.dumps(step) + "\n")

    print(f"Hybrid Game {game_id} finished with {len(game_data)} steps.")
