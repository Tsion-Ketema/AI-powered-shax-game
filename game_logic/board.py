class Board:
    def __init__(self):
        """
        Initializes the Shax board with 24 valid positions.
        """
        self.positions = {pos: None for pos in range(24)}

    def place_piece(self, position, player):
        """
        Places a piece on the board at the specified position if it's empty.
        :param position: The position index (0-23).
        :param player: 'Player 1' or 'Player 2'.
        :return: True if the piece was placed, False otherwise.
        """
        if position in self.positions and self.positions[position] is None:
            self.positions[position] = player
            return True
        return False
