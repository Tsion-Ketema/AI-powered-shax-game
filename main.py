import tkinter as tk
from frontend.ui_new import ShaxGame
from game_logger import GameLogger

def select_mode():
    print("Select game mode:")
    print("1: Minimax Without Rules vs MCTS")
    print("2: Minimax With Rules vs MCTS")
    print("3: Human vs Minimax With Rules")
    print("4: Minimax With Rules vs Minimax With Rules")
    choice = input("Enter 1-4: ")
    return choice

def get_game_config(mode):
    if mode == "1":
        return {"1": "mwor", "2": "mcts"}, "MWOR vs MCTS"
    elif mode == "2":
        return {"1": "mcts", "2": "mwr"}, "MWR vs MCTS"
    elif mode == "3":
        return {"1": "human", "2": "mwr"}, "MWR vs Human"
    elif mode == "4":
        return {"1": "mwr", "2": "mwor"}, "MWR vs MWOR"
    else:
        print("Invalid option.")
        exit()

def run_games(ai_config, logger, num_games=5):
    for i in range(num_games):
        print(f"\n=== Game {i + 1} / {num_games} started ===")
        root = tk.Tk()
        game = ShaxGame(root, ai_config=ai_config, logger=logger, game_number=i + 1)
        root.mainloop()
        root.destroy()
    game.logger.plot_game_analysis()

if __name__ == "__main__":
    mode = select_mode()
    ai_config, match_name = get_game_config(mode)
    logger = GameLogger(match_name)
    run_games(ai_config, logger)
