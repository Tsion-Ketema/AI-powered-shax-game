import os
import matplotlib.pyplot as plt
from datetime import datetime

def normalize_match_type(match_type):
    return match_type.strip().replace(" ", "_")


class GameLogger:
    def __init__(self, match_type):
        self.original_match_type = match_type
        self.folder_name = normalize_match_type(match_type)
        self.results = []
        self.game_start_time = datetime.now()
        self.end_time = None

    def log_result(self, game_number, winner, start_time, end_time, ai_config):
        duration = datetime.now() - self.game_start_time
        player1_type = ai_config.get("1", "Player 1")
        player2_type = ai_config.get("2", "Player 2")

        if self.game_start_time is None:
            self.start_time = start_time
        self.end_time = end_time

        self.results.append((game_number, player1_type, player2_type, winner, duration))

        self.save_individual_plot(game_number, player1_type, player2_type, winner, duration)

    def save_individual_plot(self, game_number, p1_type, p2_type, winner, duration):
        folder_path = os.path.join("plots", self.folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Determine the next available game number
        existing_files = [f for f in os.listdir(folder_path) if f.startswith("game_") and f.endswith(".png")]
        next_index = len(existing_files) + 1
        filename = f"game_{next_index}.png"

        # Plot
        plt.figure(figsize=(6, 4))
        plt.bar([p1_type, p2_type], [1 if winner == "Player 1" else 0, 1 if winner == "Player 2" else 0],
                color=["blue", "orange"])
        plt.title(f"Game {next_index}: {p1_type} vs {p2_type}\nWinner: {winner} | Duration: {duration}")
        plt.ylabel("Win")

        filepath = os.path.join(folder_path, filename)
        plt.savefig(filepath)
        plt.close()
        print(f"[Logger] Saved: {filepath}")
