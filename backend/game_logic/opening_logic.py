from backend.game_logic.removal_logic import perform_ai_removal

# Handles the opening phase where the first removal takes place


def perform_ai_opening(self):
    # If Player 1 formed the first mill, they remove first
    if self.first_mill == "1":
        print("Opening Phase: Player 1 formed the first mill — Player 1 removes Player 2's piece first.")
        self.removal_phase = True
        self.turn = "1"
        self.ai_remove()

    # If Player 2 formed the first mill, they remove first
    elif self.first_mill == "2":
        print("Opening Phase: Player 2 formed a mill first — It will remove one of Player 1's pieces.")
        self.removal_phase = True
        self.turn = "2"
        self.ai_remove()  # AI removes one human piece

    # If no mills were formed during placement, Player 2 removes first by default
    else:
        print("Opening Phase: No mills were formed — Player 2 will remove Player 1's piece first.")
        self.turn = "2"
        self.removal_phase = True
        self.ai_remove()

# AI triggers the removal action (delegates to full logic)


def ai_remove(self):
    perform_ai_removal(self)
