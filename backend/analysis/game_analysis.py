import os
import json
import pandas as pd
import matplotlib.pyplot as plt

class GameResultsAnalyzer:
    def __init__(self, log_folder='logs'):
        self.log_folder = log_folder
        self.results = []
        self.summary_df = pd.DataFrame()

    def _load_results(self):
        self.results = []
        if not os.path.exists(self.log_folder):
            print(f"Log folder '{self.log_folder}' not found.")
            return

        for file in os.listdir(self.log_folder):
            if file.endswith('.json'):
                file_path = os.path.join(self.log_folder, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        self.results.extend(data)
                except Exception as e:
                    print(f"Skipping {file} due to error: {e}")

    def analyze_and_plot_results(self):
        if not self.results:
            print("No results to summarize.")
            return pd.DataFrame()

        df = pd.DataFrame(self.results)
        df['duration_sec'] = pd.to_timedelta(df['duration']).dt.total_seconds()

        summary = {}
        configs = df['match_name'].unique()

        rows = 8
        cols = 4

        fig, axs = plt.subplots(rows, cols, figsize=(20, 20))
        axs = axs.flatten()

        plot_index = 0
        for config in configs:
            sub_df = df[df['match_name'] == config]
            p1_wins = (sub_df['winner'] == 'Player 1').sum()
            p2_wins = (sub_df['winner'] == 'Player 2').sum()
            avg_duration = sub_df['duration_sec'].mean()

            summary[config] = {
                'P1 Wins': p1_wins,
                'P2 Wins': p2_wins,
                'Avg Duration (s)': round(avg_duration, 2),
                'Games': len(sub_df)
            }

            if plot_index < len(axs):
                axs[plot_index].bar(['P1', 'P2'], [p1_wins, p2_wins], color=['blue', 'orange'])
                axs[plot_index].set_title(f'{config} - Wins')
                axs[plot_index].set_ylabel('Wins')
                plot_index += 1

            if plot_index < len(axs):
                axs[plot_index].plot(range(1, len(sub_df)+1), sub_df['duration_sec'], marker='o', color='green')
                axs[plot_index].set_title(f'{config} - Duration')
                axs[plot_index].set_xlabel('Game #')
                axs[plot_index].set_ylabel('Duration (s)')
                plot_index += 1

        for i in range(plot_index, len(axs)):
            fig.delaxes(axs[i])

        plt.tight_layout()
        plt.show()

        self.summary_df = pd.DataFrame.from_dict(summary, orient='index')
        return self.summary_df