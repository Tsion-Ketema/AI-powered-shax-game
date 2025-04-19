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

    def log_result(self, game_number, winner, duration, ai_config):
        player1_type = ai_config.get("1", "Player 1")
        player2_type = ai_config.get("2", "Player 2")

        self.results.append((game_number, player1_type, player2_type, winner, duration))

       # self.save_individual_plot(game_number, player1_type, player2_type, winner, duration)

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

    def plot_game_analysis(self):
        folder_path = os.path.join("plots", self.folder_name)

        if not self.results:
            print("No game results to analyze.")
            return

        # Extract data
        game_numbers = [r[0] for r in self.results]
        player1_type = [r[1] for r in self.results]
        player2_type = [r[2] for r in self.results]
        winners = [r[3] for r in self.results]
        durations = [r[4].total_seconds() for r in self.results]  # duration in seconds
        print(durations)

        # Count wins
        win_counts = {}
        for winner in winners:
            if winner not in win_counts:
                win_counts[winner] = 0
            win_counts[winner] += 1

        # Plot win counts
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.bar(win_counts.keys(), win_counts.values())
        plt.title('Number of Wins per Player')
        plt.xlabel('Winner')
        plt.ylabel('Wins')
        plt.grid(axis='y')

        # Plot game durations
        plt.subplot(1, 2, 2)
        plt.plot(game_numbers, durations, marker='o')
        plt.title('Game Duration Over Time')
        plt.xlabel('Game Number')
        plt.ylabel('Duration (seconds)')
        plt.grid(True)

        plt.tight_layout()

        plt.savefig(folder_path)
        print(f"Plot saved")

