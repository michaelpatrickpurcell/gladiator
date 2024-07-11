import random
import copy
import networkx as nx

def compute_state_hash(state):
    temp = sum(state, [])
    hash = sum([x * 3**i for i,x in enumerate(temp[::-1])])
    return hash

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
    def get_valid_moves(self):
        valid_moves = []
        for i in range(self.n):
            for j in range(self.n):
                if self.state[i][j] == 0:
                    valid_moves.append((i,j))
        return valid_moves
    def __str__(self):
        return '\n'.join([' '.join(['%i' % x for x in self.state[row]]) for row in range(self.n)]) + '\n'
    
class Opponent(object):
    def __init__(self, player_number=2, n=3):
        self.n = n
        self.player_number = player_number
        self.g = nx.Graph()
        print("Please wait for a minute while I teach myself to play Tic Tac Toe.")
        self.initialize_evaluation_graph()
        print("I'm ready to play. You go first.\n")

    def initialize_evaluation_graph(self):
        self.g = nx.DiGraph()
        self.g.add_node(0, state=GameBoard().state, value=0, current_player_number=1)
        self.add_eg_children(0, current_player_number=1)

    def add_eg_children(self, node, current_player_number):
        node_data = dict(self.g.nodes.items())
        current_board = GameBoard()
        current_board.state = node_data[node]['state']
        current_state_hash = compute_state_hash(current_board.state)
        valid_moves = current_board.get_valid_moves()
        child_rewards = []
        for move in valid_moves:
            next_player_number = (current_player_number % 2) + 1
            next_board = copy.deepcopy(current_board)
            next_board.update_board(current_player_number, move)
            next_state_hash = compute_state_hash(next_board.state)
            if next_state_hash in self.g:
                self.g.add_edge(current_state_hash, next_state_hash, move=move)
                temp = dict(self.g.nodes.items())
                reward = temp[next_state_hash]['reward']
                child_rewards.append(reward)
                continue
            # print('current_state_hash: %i' % compute_state_hash(current_board.state))
            # print(current_board.state)
            # print('next_state_hash: %i' % next_state_hash)
            # print(next_board.state)
            self.g.add_node(next_state_hash, state=next_board.state, current_player_number = next_player_number)
            self.g.add_edge(current_state_hash, next_state_hash, move=move)
            if next_board.check_win_condition(1):
                # print('Player 1 wins')
                # print()
                if self.player_number == 1:
                    reward = 1
                    nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
                else:
                    reward = -1
                    nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
            elif next_board.check_win_condition(2):
                # print('Player 2 wins')
                # print()
                if self.player_number == 2:
                    reward = 1
                    nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
                else:
                    reward = -1
                    nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
            elif len(next_board.get_valid_moves()) == 0:
                # print('Draw')
                # print()
                reward = 0
                nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
            else:
                reward = self.add_eg_children(next_state_hash, next_player_number)
            child_rewards.append(reward)
        # print()
        if current_player_number == self.player_number:
            current_reward = max(child_rewards)
        else:
            current_reward = min(child_rewards)
        nx.set_node_attributes(self.g, {current_state_hash: {'reward': current_reward}})
        return current_reward

    def make_random_move(self, game_board):
        valid_moves = game_board.get_valid_moves()
        location = random.choice(valid_moves)
        game_board.update_board(self.player_number, location)

    def make_good_random_move(self, game_board):
        current_state_hash = compute_state_hash(game_board.state)
        rewards = nx.get_node_attributes(self.g, 'reward')
        moves = nx.get_edge_attributes(self.g, 'move')
        next_states = list(self.g.successors(current_state_hash))
        max_reward = max([rewards[x] for x in next_states])
        good_next_states = [x for x in next_states if rewards[x] == max_reward]
        chosen_next_state = random.choice(good_next_states)
        location = moves[(current_state_hash, chosen_next_state)]
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
            opponent.make_good_random_move(game_board)
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






