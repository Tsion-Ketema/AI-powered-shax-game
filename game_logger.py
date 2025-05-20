import os
import json
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

        result_entry = {
            "game_number": game_number,
            "player1_type": player1_type,
            "player2_type": player2_type,
            "winner": winner,
            "duration": str(duration),
            "match_name": self.original_match_type
        }

        self.results.append(result_entry)

        # Save to JSON log file dynamically
        logs_path = os.path.join("logs")
        os.makedirs(logs_path, exist_ok=True)
        log_file_path = os.path.join(logs_path, f"{self.folder_name}.json")

        # Append to JSON file if exists, or create new
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.append(result_entry)

        with open(log_file_path, "w") as f:
            json.dump(existing_data, f, indent=2)

    def save_individual_plot(self, game_number, p1_type, p2_type, winner, duration):
        folder_path = os.path.join("plots", self.folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Determine the next available game index
        existing_files = [f for f in os.listdir(
            folder_path) if f.startswith("game_") and f.endswith(".png")]
        next_index = len(existing_files) + 1
        filename = f"game_{next_index}.png"

        # Plotting a bar for the winner
        plt.figure(figsize=(6, 4))
        plt.bar([p1_type, p2_type],
                [1 if winner == "Player 1" else 0,
                    1 if winner == "Player 2" else 0],
                color=["blue", "orange"])
        plt.title(
            f"Game {next_index}: {p1_type} vs {p2_type}\nWinner: {winner} | Duration: {duration}")
        plt.ylabel("Win")

        filepath = os.path.join(folder_path, filename)
        plt.savefig(filepath)
        plt.close()
        print(f"[Logger] Saved: {filepath}")

    def plot_game_analysis(self):
        folder_path = os.path.join("plots", self.folder_name)
        os.makedirs(folder_path, exist_ok=True)

        if not self.results:
            print("No game results to analyze.")
            return

        # Extract data
        game_numbers = [entry["game_number"] for entry in self.results]
        winners = [entry["winner"] for entry in self.results]
        durations = [
            datetime.strptime(entry["duration"], "%H:%M:%S.%f").second +
            datetime.strptime(entry["duration"], "%H:%M:%S.%f").minute * 60 +
            datetime.strptime(entry["duration"], "%H:%M:%S.%f").hour * 3600
            for entry in self.results
        ]

        # Count wins
        win_counts = {}
        for winner in winners:
            win_counts[winner] = win_counts.get(winner, 0) + 1

        # Plot win counts
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.bar(win_counts.keys(), win_counts.values(),
                color=["skyblue", "salmon"])
        plt.title("Number of Wins per Player")
        plt.xlabel("Winner")
        plt.ylabel("Wins")
        plt.grid(axis="y")

        # Plot game durations
        plt.subplot(1, 2, 2)
        plt.plot(game_numbers, durations, marker="o", color="green")
        plt.title("Game Duration Over Time")
        plt.xlabel("Game Number")
        plt.ylabel("Duration (seconds)")
        plt.grid(True)

        plt.tight_layout()

        # Save combined plot
        plot_path = os.path.join(
            folder_path, f"{self.folder_name}_summary.png")
        plt.savefig(plot_path)
        plt.close()
        print(f"[Logger] Summary plot saved at: {plot_path}")
