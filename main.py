import tkinter as tk
from frontend.ui import ShaxGame
from game_logger import GameLogger

# Prompt the user to choose a game mode


def select_mode():
    print("Select game mode:")
    print("1: Minimax Without Rules vs MCTS")
    print("2: Minimax With Rules vs MCTS")
    print("3: Human vs Minimax With Rules")
    choice = input("Enter 1-3: ")
    return choice

# Map the selected mode to an AI configuration and a descriptive match name


def get_game_config(mode):
    if mode == "1":
        return {"1": "mwor", "2": "mcts"}, "MWOR vs MCTS"
    elif mode == "2":
        return {"1": "mwr", "2": "mcts"}, "MWR vs MCTS"
    elif mode == "3":
        return {"1": "human", "2": "mwr"}, "Human vs MWR"
    else:
        print("Invalid option.")
        exit()

# Run a series of games (default = 10) based on the chosen AI configuration


def run_games(ai_config, logger, num_games=10):
    for i in range(num_games):
        print(f"\n=== Game {i + 1} / {num_games} started ===")
        root = tk.Tk()  # Create a new game window
        game = ShaxGame(root, ai_config=ai_config,
                        logger=logger, game_number=i + 1)
        root.mainloop()  # Start the GUI event loop (waits for game to finish)
        root.destroy()   # Close the game window after the game ends
    game.logger.plot_game_analysis()  # Generate and save summary plots after all games


# Entry point of the program
if __name__ == "__main__":
    mode = select_mode()                        # Get user’s game mode selection
    # Get config and label for selected mode
    ai_config, match_name = get_game_config(mode)
    # Initialize logger with match name
    logger = GameLogger(match_name)
    run_games(ai_config, logger)                # Run the game series
