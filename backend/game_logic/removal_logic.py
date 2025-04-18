from tkinter import messagebox
from backend.ai_logic.ai_mcts import monte_carlo_tree_search
from backend.game_logic.utils import *

def perform_ai_removal(game):
    player = game.turn
    opponent = "2" if player == "1" else "1"
    ai_type = game.ai_config[player]

    def remove_piece(pos, reason):
        game.board[pos] = "x"
        if player == "1":
            game.player_one_captures += 1
        else:
            game.player_two_captures += 1
        game.update_board()
        game.check_win_conditions()
        print(f"{pos} removed by {reason}")
        game.removal_phase = False

        if game.phase == "opening":
            game.opening_count -= 1
            if game.opening_count == 0:
                game.phase = "movement"
            else:
                game.removal_phase = True
                game.turn = opponent

        # After removal, decide who plays next
        if game.ai_config[game.turn] == "human":
            game.canvas.bind("<Button-1>", game.handle_click)
        else:
            game.root.after(500, game.ai_move if game.phase == "movement" else game.ai_remove)

    # MCTS AI logic
    if ai_type == "mcts":
        move = monte_carlo_tree_search(game.board, player, "removal" if game.removal_phase else game.phase)
        remove_piece(move, "MCTS removal")
        return

    # Minimax without rules
    if ai_type == "mwor":
        for pos, piece in enumerate(game.board):
            if piece == opponent:
                remove_piece(pos, "fallback removal")
                return

    # Minimax with rules
    if ai_type == "mwr":
        positions = [i for i, p in enumerate(game.board) if p == opponent]

        if game.phase == "opening":
            for pos in positions:
                if any(pos in mill and all(game.board[p] in [player, "x"] for p in mill) and
                       any(game.board[adj] == player for adj in adjacentLocations(pos)) for mill in mills):
                    remove_piece(pos, "opening mill block")
                    return

            for pos in positions:
                if any(pos in mill and sum(game.board[p] == opponent for p in mill) == 2 and
                       sum(game.board[p] == "x" for p in mill) == 1 for mill in mills):
                    remove_piece(pos, "disrupt mill")
                    return

            remove_piece(positions[0], "fallback opening")
            return

        elif game.phase == "movement":
            for mill in mills:
                hp = [p for p in mill if game.board[p] == opponent]
                ep = [p for p in mill if game.board[p] == "x"]
                if len(hp) == 2 and len(ep) == 1:
                    for adj in adjacentLocations(ep[0]):
                        if game.board[adj] == opponent:
                            remove_piece(adj, "back-and-forth prevention")
                            return

            remove_piece(positions[0], "fallback movement")


def handle_human_removal(game, pos):
    print("Waiting for human to remove a piece...")

    if game.ai_config[game.turn] != "human":
        print("[ERROR] Not human's removal turn.")
        return

    if game.board[pos] != game.ai_player:
        messagebox.showinfo("Invalid Selection", "Select an AI piece to remove.")
        return

    game.board[pos] = "x"
    game.player_one_captures += 1
    print(f"[Human Capture] Player {game.human_player} removed AI piece at {pos}")  # ✅ Debug line

    if game.phase == "opening":
        game.opening_count -= 1

    game.update_board()

    if game.phase == "opening" and game.opening_count == 0:
        game.phase = "movement"
        game.removal_phase = False
        game.turn = game.ai_player
        game.root.after(500, game.ai_move)
    else:
        game.removal_phase = True
        game.turn = game.ai_player
        if game.ai_config[game.turn] == "human":
            print("Waiting for human to remove a piece.")
            game.canvas.bind("<Button-1>", game.handle_click)
        else:
            game.root.after(500, game.ai_remove)
