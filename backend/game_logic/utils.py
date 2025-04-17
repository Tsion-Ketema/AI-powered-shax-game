from datetime import datetime

mills = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14],
    [15, 16, 17], [18, 19, 20], [21, 22, 23], [0, 9, 21], [3, 10, 18],
    [6, 11, 15], [1, 4, 7], [16, 19, 22], [8, 12, 17], [5, 13, 20], [2, 14, 23]
]

adjacent = {
    0: [1, 9], 1: [0, 2, 4], 2: [1, 14], 3: [4, 10], 4: [1, 3, 5, 7],
    5: [4, 13], 6: [7, 11], 7: [4, 6, 8], 8: [7, 12], 9: [0, 10, 21],
    10: [3, 9, 11, 18], 11: [6, 10, 15], 12: [8, 13, 17], 13: [5, 12, 14, 20],
    14: [2, 13, 23], 15: [11, 16], 16: [15, 17, 19], 17: [12, 16], 18: [10, 19],
    19: [16, 18, 20, 22], 20: [13, 19], 21: [9, 22], 22: [19, 21, 23], 23: [14, 22]
}


def get_possible_moves(board):
    return [i for i in range(len(board)) if board[i] == 'x']

def get_possible_moves_player(board, player):
    possible_moves = []
    for i in range(len(board)):
        if board[i] == player:
            adjacent = adjacentLocations(i)
            for j in adjacent:
                if board[j] == 'x':
                    possible_moves.append((i, j))
    return possible_moves

def adjacentLocations(position):
    return adjacent[position]

def check_next_mill(position, board, player):
    for mill in mills:
        if position in mill:
            if all(board[i] == player for i in mill):
                return True
    return False

def isMill(position, board):
    p = board[position]
    return p != 'x' and check_next_mill(position, board, p)

def numOfPieces(board, player):
    return board.count(player)

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

