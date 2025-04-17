from backend.game_logic.removal_logic import perform_ai_removal

def perform_ai_opening(self):
            # Determine the order of removal
            if self.first_mill == "1":
                print(
                    "Opening Phase Player 1 formed the first mill Player 1 remove player 2's piece first")
                self.removal_phase = True
                self.turn = "1"
                self.ai_remove()
            elif self.first_mill == "2":
                print(
                    "Opening Phase Player 2 formed a mill first! It will remove one of opponent pieces.")
                self.removal_phase = True
                self.turn = "2"
                self.ai_remove()  # AI removes one human piece
            else:
                print(
                    "Opening Phase", "No mills were formed. Player 2 will remove player 1's piece first.")
                self.turn = "2"
                self.removal_phase = True
                self.ai_remove()

def ai_remove(self):
        perform_ai_removal(self)

        