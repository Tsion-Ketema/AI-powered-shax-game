from datetime import datetime
from statistics import mean
import matplotlib.pyplot as plt
import os


class GameLogger:
    def __init__(self, match_type):
        self.match_type = match_type
        self.results = []

    def log_result(self, game_number, winner, start_time, end_time, ai_config):
        duration = (end_time - start_time).total_seconds()
        player1_type = ai_config.get("1", "Player 1")
        player2_type = ai_config.get("2", "Player 2")
        self.results.append(
            (game_number, player1_type, player2_type, winner, duration))

    def summarize_and_plot(self):
        total_games = len(self.results)
        if total_games == 0:
            return

        p1_wins = sum(1 for _, _, _, winner,
                      _ in self.results if winner == "Player 1")
        p2_wins = total_games - p1_wins

        print(f"\nMatch Summary: {self.match_type}")
        print(f"Total Games: {total_games}")
        print(f"Player 1 Wins: {p1_wins}")
        print(f"Player 2 Wins: {p2_wins}")

        # Plotting
        plt.figure(figsize=(6, 4))
        plt.bar(["Player 1", "Player 2"], [
                p1_wins, p2_wins], color=["blue", "orange"])
        plt.title(f"Win Count - {self.match_type}")
        plt.ylabel("Wins")

        # Auto-incrementing filename
        base_filename = f"{self.match_type.replace(' ', '_').replace('/', '_vs_')}_wins"
        filename = f"{base_filename}.png"
        counter = 2
        while os.path.exists(filename):
            filename = f"{base_filename}_{counter}.png"
            counter += 1

        plt.savefig(filename)
        plt.close()

        print(f"Plot saved as: {filename}")
