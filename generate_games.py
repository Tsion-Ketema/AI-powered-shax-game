from self_play_logger import play_game

def generate_multiple_games(n=10, iterations=5000, start=0):
    for i in range(start, start + n):
        play_game(game_id=i, iterations=iterations)

if __name__ == "__main__":
    generate_multiple_games(n=576)
