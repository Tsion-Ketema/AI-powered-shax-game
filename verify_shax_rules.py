
import os
import json
from backend.utils import adjacentLocations, isMill

def is_valid_shax_move(prev_board, next_board, player, action, phase, first_jare_formed):
    opponent = 2 if player == "1" else 1
    prev_board = list(map(int, prev_board))
    next_board = list(map(int, next_board))

    if phase == "placement":
        if not isinstance(action, int) or not (0 <= action < 24):
            return False, "Invalid placement index"
        if prev_board[action] != 0 or next_board[action] != int(player):
            return False, "Invalid placement"
        if sum(next_board) - sum(prev_board) != int(player):
            return False, "Unexpected board delta during placement"
        return True, ""

    elif phase == "removal":
        if not isinstance(action, int) or not (0 <= action < 24):
            return False, "Invalid removal index"
        if prev_board[action] != opponent:
            return False, "Removed piece was not opponent's"
        if next_board[action] != 0:
            return False, "Piece not removed correctly"
        return True, ""

    elif phase == "movement":
        if not isinstance(action, list) or len(action) != 2:
            return False, "Invalid movement format"
        src, dst = action
        if prev_board[src] != int(player) or prev_board[dst] != 0:
            return False, "Source or destination issue"
        if dst not in adjacentLocations(src):
            return False, "Illegal jump (no flying allowed in Shax)"
        if next_board[src] != 0 or next_board[dst] != int(player):
            return False, "Post-move board mismatch"
        return True, ""

    elif phase == "blocked_movement":
        # Treated like movement, but cannot form a jare and capture
        valid, reason = is_valid_shax_move(prev_board, next_board, player, action, "movement", first_jare_formed)
        if not valid:
            return False, reason
        if isinstance(action, list) and isMill(action[1], next_board):
            return False, "Capture should not occur during forced unblocking"
        return True, ""

    return False, "Unknown phase"

def verify_shax_games(log_dir="recorded_ai_games"):
    issues = []
    for filename in os.listdir(log_dir):
        if not filename.endswith(".jsonl"):
            continue
        with open(os.path.join(log_dir, filename)) as f:
            first_jare_formed = None
            for i, line in enumerate(f):
                entry = json.loads(line)
                phase = entry["phase"]
                if phase == "removal" and entry.get("first_mill", False) and i < 24:
                    issues.append({
                        "file": filename, "line": i, "phase": phase,
                        "player": entry["player"], "action": entry["action"],
                        "reason": "Removal not allowed during placement phase in Shax"
                    })
                    continue
                valid, reason = is_valid_shax_move(
                    entry["state"],
                    entry["next_state"],
                    entry["player"],
                    entry["action"],
                    phase,
                    first_jare_formed
                )
                if not valid:
                    issues.append({
                        "file": filename,
                        "line": i,
                        "phase": entry["phase"],
                        "player": entry["player"],
                        "action": entry["action"],
                        "reason": reason
                    })
    return issues

if __name__ == "__main__":
    issues = verify_shax_games()
    if not issues:
        print("✅ All moves follow Shax rules!")
    else:
        print(f"❌ Found {len(issues)} rule violations:")
        for issue in issues:
            print(issue)
