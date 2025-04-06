import json
import os
from itertools import combinations, permutations

mills = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],
    [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23],
    [0, 9, 21], [3, 10, 18], [6, 11, 15], [1, 4, 7],
    [16, 19, 22], [8, 12, 17], [5, 13, 20], [2, 14, 23]
]

output_path = "game_logs"
os.makedirs(output_path, exist_ok=True)


def encode(board):
    return [0 if x == 'x' else int(x) for x in board]


def save_samples(samples, filename):
    with open(os.path.join(output_path, filename), "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")


# =========================
# JARE SAMPLES (3 in a row)
# =========================
def generate_jare_samples(player="2"):
    samples = []
    reward = 10
    for mill in mills:
        for i in range(3):
            a, b = [mill[j] for j in range(3) if j != i]
            target = mill[i]
            board = ['x'] * 24
            board[a] = player
            board[b] = player
            state = encode(board)
            board[target] = player
            next_state = encode(board)

            samples.append({
                "state": state,
                "player": player,
                "action": target,
                "reward": reward,
                "next_state": next_state,
                "done": False,
                "phase": "placement"
            })
    return samples


# ==============================
# LABA-QAAD: double threat setup
# ==============================
def generate_laba_qaad_samples(player="2"):
    samples = []
    reward = 8
    mill_pairs = combinations(mills, 2)
    for m1, m2 in mill_pairs:
        common = set(m1) & set(m2)
        if not common:
            shared_board = ['x'] * 24
            for m in [m1, m2]:
                # place 2 from each
                for i in range(2):
                    shared_board[m[i]] = player
            state = encode(shared_board)
            samples.append({
                "state": state,
                "player": player,
                "action": None,
                "reward": reward,
                "next_state": state,
                "done": False,
                "phase": "placement"
            })
    return samples


# ==================================
# AFAREY: 4 in a defensive formation
# ==================================
def generate_afarey_samples(player="2"):
    samples = []
    reward = 6
    defensive_blocks = [
        [0, 1, 9, 10], [3, 4, 10, 11], [12, 13, 19, 20], [15, 16, 19, 22],
        [6, 7, 11, 12], [18, 19, 10, 13]
    ]
    for block in defensive_blocks:
        board = ['x'] * 24
        for pos in block:
            board[pos] = player
        state = encode(board)
        samples.append({
            "state": state,
            "player": player,
            "action": None,
            "reward": reward,
            "next_state": state,
            "done": False,
            "phase": "placement"
        })
    return samples


# ====================================
# IRMAAN: triangle-style control zones
# ====================================
def generate_irmaan_samples(player="2"):
    samples = []
    reward = 7
    triangles = [
        [1, 4, 7], [3, 4, 5], [10, 13, 19], [16, 19, 22],
        [12, 13, 14], [6, 11, 15], [8, 12, 17]
    ]
    for tri in triangles:
        board = ['x'] * 24
        for pos in tri:
            board[pos] = player
        state = encode(board)
        samples.append({
            "state": state,
            "player": player,
            "action": None,
            "reward": reward,
            "next_state": state,
            "done": False,
            "phase": "placement"
        })
    return samples


# ========================================
# BLOCKING JARE: prevent opponent's mill
# ========================================
def generate_mill_blocking_samples():
    samples = []
    reward = 5
    for mill in mills:
        for i in range(3):
            a, b = [mill[j] for j in range(3) if j != i]
            target = mill[i]
            board = ['x'] * 24
            board[a] = '2'  # opponent (trying to form a mill)
            board[b] = '2'
            # player should block by placing at target
            state = encode(board)
            board[target] = '1'
            next_state = encode(board)
            samples.append({
                "state": state,
                "player": "1",
                "action": target,
                "reward": reward,
                "next_state": next_state,
                "done": False,
                "phase": "placement"
            })
    return samples


if __name__ == "__main__":
    jare = generate_jare_samples()
    laba_qaad = generate_laba_qaad_samples()
    afarey = generate_afarey_samples()
    irmaan = generate_irmaan_samples()
    blocks = generate_mill_blocking_samples()

    save_samples(jare, "jare_examples.jsonl")
    save_samples(laba_qaad, "laba_qaad_examples.jsonl")
    save_samples(afarey, "afarey_examples.jsonl")
    save_samples(irmaan, "irmaan_examples.jsonl")
    save_samples(blocks, "block_mill_examples.jsonl")

    print("✅ Strategic training samples generated successfully.")
