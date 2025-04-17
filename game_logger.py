import os
import matplotlib.pyplot as plt
from datetime import datetime


def normalize_match_type(match_type):
    parts = [p.strip().upper() for p in match_type.split("vs")]
    parts.sort()
    return "_vs_".join(parts)



class GameLogger:
    def __init__(self, match_type):
        self.original_match_type = match_type
        self.folder_name = normalize_match_type(match_type)
        self.results = []
        self.start_time = None
        self.end_time = None

    def log_result(self, game_number, winner, start_time, end_time, ai_config):
        duration = (end_time - start_time).total_seconds()
        player1_type = ai_config.get("1", "Player 1")
        player2_type = ai_config.get("2", "Player 2")

        if self.start_time is None:
            self.start_time = start_time
        self.end_time = end_time

        self.results.append((game_number, player1_type, player2_type, winner, duration))

        self.save_individual_plot(game_number, player1_type, player2_type, winner, duration)

    def save_individual_plot(self, game_number, p1_type, p2_type, winner, duration):
        folder_path = os.path.join("plots", self.folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Plot single game result
        plt.figure(figsize=(6, 4))
        plt.bar([p1_type, p2_type], [1 if winner == "Player 1" else 0, 1 if winner == "Player 2" else 0],
                color=["blue", "orange"])
        plt.title(f"Game {game_number}: {p1_type} vs {p2_type}\nWinner: {winner} | Duration: {duration:.1f}s")
        plt.ylabel("Win")

        filename = f"game_{game_number}.png"
        filepath = os.path.join(folder_path, filename)
        plt.savefig(filepath)
        plt.close()
        print(f"[Logger] Saved: {filepath}")