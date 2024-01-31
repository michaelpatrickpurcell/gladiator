import random

class GameBoard(object):
    def __init__(self, n=3):
        self.n = n
        self.state = [[0 for j in range(n)] for i in range(n)]
    def update_board(self, player_number, location):
        self.state[location[0]][location[1]] = player_number
    def check_win_condition(self, player_number):
        win_flag = False
        for row in range(self.n):
            if all([self.state[row][j] == player_number for j in range(self.n)]):
                win_flag = True
        for column in range(self.n):
            if all([self.state[i][column] == player_number for i in range(self.n)]):
                win_flag = True
        if all([self.state[i][i] == player_number for i in range(self.n)]):
            win_flag = True
        if all([self.state[i][self.n-1-i] == player_number for i in range(self.n)]):
            win_flag=True
        return win_flag
    def __str__(self):
        return '\n'.join([' '.join(['%i' % x for x in self.state[row]]) for row in range(self.n)]) + '\n'
    
class Opponent(object):
    def __init__(self, player_number=2, n=3):
        self.n = n
        self.player_number = player_number
    def make_random_move(self, game_board):
        valid_moves = []
        for i in range(self.n):
            for j in range(self.n):
                if game_board.state[i][j] == 0:
                    valid_moves.append((i,j))
        location = random.choice(valid_moves)
        game_board.update_board(self.player_number, location)
    
if __name__ == "__main__":
    game_board = GameBoard(n=3)
    opponent = Opponent(player_number=2, n=3)
    winner = 0
    current_player = 1
    while winner == 0:
        if all([game_board.state[i][j] != 0 for i in range(game_board.n) for j in range(game_board.n)]):
            winner = -1
            continue
        print(game_board)
        if opponent.player_number == current_player:
            opponent.make_random_move(game_board)
        else:
            valid_move = False
            while not valid_move:
                row = int(input('Enter the row for your move: '))
                column = int(input('Enter the column for your move: '))
                if game_board.state[row][column] == 0:
                    valid_move = True
                    game_board.update_board(current_player, (row, column))
                else:
                    print("Invalid move, please try again.\n")
                    print(game_board)
        win_flag = game_board.check_win_condition(current_player)
        if win_flag:
            winner = current_player
        if current_player == 1:
            current_player = 2
        elif current_player == 2:
            current_player = 1

    print(game_board)
    print('The winner is: %i' % winner)






