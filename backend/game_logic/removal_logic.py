from tkinter import messagebox
from backend.ai_logic.ai_mcts  import monte_carlo_tree_search
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
        game.removal_phase = False

        if game.phase == "opening":
            game.opening_count -= 1
            if game.opening_count == 0:
                game.phase = "movement"
                game.removal_phase = False
                game.turn = opponent
                game.root.after(500, game.ai_move)
            else:
                game.removal_phase = True
                game.turn = opponent
                if game.ai_config[game.turn] != "human":
                    game.root.after(500, game.ai_remove)
                else:
                    print("Waiting for human to remove a piece(first one)...")
                    game.canvas.bind("<Button-1>", game.handle_click)
        else:
            game.turn = opponent
            game.root.after(500, game.ai_move)
            game.canvas.bind("<Button-1>", game.handle_click)

    if ai_type == "mcts":
        move = monte_carlo_tree_search(game.board, player, "removal" if game.removal_phase else game.phase)
        remove_piece(move, "MCTS removal")
        return

    # Opening phase logic for minimax (MWOR or MWR)
    if game.phase == "opening":
        for pos, piece in enumerate(game.board):
            if piece == opponent:
                for mill in mills:
                    if pos in mill and all(game.board[p] in [player, "x"] for p in mill):
                        if any(game.board[adj] == player for adj in adjacentLocations(pos)):
                            remove_piece(pos, "opening mill block")
                            return
        for pos, piece in enumerate(game.board):
            if piece == opponent:
                for mill in mills:
                    if pos in mill:
                        human_count = sum(1 for p in mill if game.board[p] == opponent)
                        empty_count = sum(1 for p in mill if game.board[p] == "x")
                        if human_count == 2 and empty_count == 1:
                            remove_piece(pos, "disrupt mill")
                            return
        for pos, piece in enumerate(game.board):
            if piece == opponent:
                remove_piece(pos, "fallback opening")
                return

    # Movement phase logic for minimax (MWOR or MWR)
    if game.phase == "movement":
        for mill in mills:
            human_positions = [p for p in mill if game.board[p] == opponent]
            empty_positions = [p for p in mill if game.board[p] == "x"]
            if len(human_positions) == 2 and len(empty_positions) == 1:
                for adj in adjacentLocations(empty_positions[0]):
                    if game.board[adj] == opponent:
                        remove_piece(adj, "back-and-forth prevention")
                        return
        for pos, piece in enumerate(game.board):
            if piece == opponent:
                remove_piece(pos, "fallback movement")
                return

#
def handle_human_removal(game, pos):
    print("Waiting for human to remove a piece...")

    if game.ai_config[game.turn] != "human":
        print("[ERROR] Not human's removal turn.")
        return

    if game.board[pos] == game.ai_player:
        game.board[pos] = "x"
        game.player_one_captures += 1
        print(f"Human removed AI piece at {pos}")

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
            if game.ai_config[game.turn] != "human":
                game.root.after(500, game.ai_remove)
            else:
                print("Waiting for human to remove a piece.")
                game.canvas.bind("<Button-1>", game.handle_click)
    else:
        messagebox.showinfo("Invalid Selection", "Select an AI piece to remove.")
