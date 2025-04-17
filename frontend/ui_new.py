import tkinter as tk

from backend.game_logic.placement_logic import perform_ai_placement
from backend.game_logic.opening_logic import perform_ai_opening
from backend.game_logic.removal_logic import perform_ai_removal
from backend.game_logic.movement_logic import perform_ai_movement
from backend.game_logic.utils import *

pos_coords = {
    0: (40, 40), 1: (280, 40), 2: (520, 40), 3: (120, 120), 4: (280, 120),
    5: (440, 120), 6: (200, 200), 7: (280, 200), 8: (360, 200), 9: (40, 280),
    10: (120, 280), 11: (200, 280), 12: (360, 280), 13: (440, 280), 14: (520, 280),
    15: (200, 360), 16: (280, 360), 17: (360, 360), 18: (120, 440), 19: (280, 440),
    20: (440, 440), 21: (40, 520), 22: (280, 520), 23: (520, 520)
}

class ShaxGame:
    def __init__(self, root, ai_config, logger, game_number):
        self.root = root
        self.root.title("Shax game by AI crackers")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="sandy brown")
        self.canvas.pack()
        self.status_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack()


        self.logger = logger
        self.game_number = game_number
        self.ai_config = ai_config

        self._init_game_state()

        self.draw_board_lines()
        self.draw_positions()

        self.ai_player = "1" if self.ai_config["1"] != "human" else "2"
        self.human_player = "2" if self.ai_player == "1" else "1"

        if self.ai_config[self.turn] == "human":
            self.canvas.bind("<Button-1>", self.handle_click)
        else:
            self.root.after(500, self.ai_place)

        self.update_board()
        self.game_start_time = datetime.now()
        print(f"[Game Start] Game started at {self.game_start_time.strftime('%H:%M:%S')}")

    def _init_game_state(self):
        self.board = ["x"] * 24
        self.phase = "placement"
        self.turn = "1"
        self.placement_moves = 0
        self.selected = None
        self.first_mill = None
        self.removal_phase = False
        self.mills_formed = {"human": 0, "ai": 0}
        self.opening_count = 2
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.depth = 4
        self.blocked = False
        self.player_one_captures = 0
        self.player_two_captures = 0
        # in ui_new.py
        self.pos_coords = pos_coords  # set as instance attribute once

    def draw_board_lines(self):
        self.canvas.create_rectangle(40, 40, 520, 520, width=2)
        self.canvas.create_rectangle(120, 120, 440, 440, width=2)
        self.canvas.create_rectangle(200, 200, 360, 360, width=2)
        self.canvas.create_line(280, 40, 280, 200, width=2)
        self.canvas.create_line(520, 280, 360, 280, width=2)
        self.canvas.create_line(280, 520, 280, 360, width=2)
        self.canvas.create_line(40, 280, 200, 280, width=2)

    def draw_positions(self):
        radius = 12
        for pos, (x, y) in pos_coords.items():
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill="white", outline="black", width=2)

    def update_board(self):
        self.canvas.delete("piece")
        radius = 12
        for pos, (x, y) in pos_coords.items():
            piece = self.board[pos]
            color = "green" if piece == "1" else "yellow" if piece == "2" else "white"
            self.canvas.create_text(x, y - 25, text=str(pos), fill="black")
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill=color, outline="black", width=2, tag="piece")
        self.update_status()
        self.root.update()

    def update_status(self):
        p1 = numOfPieces(self.board, "1")
        p2 = numOfPieces(self.board, "2")
        self.status_label.config(text=f"Turn: player {self.turn}  |  Player 1 Pieces: {p1}  |  Player 2 Pieces: {p2}  "
                                      f"|  P1 Captures: {self.player_one_captures}  |  P2 Captures: {self.player_two_captures}  | Phase: {self.phase}")

    def handle_click(self, event):
        for pos, (x, y) in pos_coords.items():
            if (event.x - x) ** 2 + (event.y - y) ** 2 <= 15 ** 2:
                if self.phase == "placement":
                    from backend.game_logic.placement_logic import handle_human_placement
                    handle_human_placement(self, pos)
                elif self.removal_phase:
                    from backend.game_logic.removal_logic import handle_human_removal
                    handle_human_removal(self, pos)
                elif self.phase == "movement":
                    from backend.game_logic.movement_logic import handle_human_movement
                    handle_human_movement(self, pos)
                return

    def check_win_conditions(self):
        p1, p2 = numOfPieces(self.board, "1"), numOfPieces(self.board, "2")
        if p1 < 3 or p2 < 3:
            winner = "Player 2" if p1 < 3 else "Player 1"
            loser = "Player 1" if p1 < 3 else "Player 2"
            duration = datetime.now() - self.game_start_time
            print(f"[Game End] {winner} won against {loser}")
            print(f"[Game Duration] Total duration: {duration}")
            self.logger.log_result(
                game_number=self.game_number,
                winner=winner,
                start_time=self.game_start_time,
                end_time=datetime.now(),
                ai_config=self.ai_config
            )
            self.root.quit()

    def ai_place(self):
        perform_ai_placement(self)

    def ai_opening(self):
        perform_ai_opening(self)

    def ai_move(self):
        perform_ai_movement(self)

    def ai_remove(self):
        perform_ai_removal(self)
