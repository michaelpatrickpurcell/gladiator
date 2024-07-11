import random
import copy
import networkx as nx

import numpy as np
from scipy.special import comb

from itertools import combinations

import hashlib
import time

from termcolor import colored

n = 6
num_rows = comb(n,2,exact=True)
num_cols = comb(n,3,exact=True)
edge_indices = {frozenset(x):i for i,x in enumerate(combinations(np.arange(n), 2))}
triangle_indices = {frozenset(x):i for i,x in enumerate(combinations(np.arange(n), 3))}
active_states = np.zeros((num_rows, num_cols), dtype=bool)
for edge,i in edge_indices.items():
    for triangle,j in triangle_indices.items():
        if edge.issubset(triangle):
            active_states[i,j] = True


def compute_state_hash(state):
    h = hashlib.sha256(state.data)
    return h.digest()

class GameBoard(object):
    def __init__(self):
        self.state = np.zeros((num_rows, num_cols), dtype=int)

    def update_board(self, player_number, row_number):
        mask = active_states[row_number]
        self.state[row_number, mask] = player_number

    def check_win_condition(self, player_number):
        win_flag = False
        column_sums = np.sum(self.state, axis=0)
        if np.any(column_sums == 3*player_number):
            win_flag=True
        return win_flag

    def check_loss_condition(self, player_number):
        loss_flag = False
        column_sums = np.sum(self.state, axis=0)
        if np.any(column_sums == 3*player_number):
            loss_flag=True
        return loss_flag


    def get_valid_moves(self):
        row_sums = np.sum(self.state, axis=1)
        valid_moves = list(np.where(row_sums == 0)[0])
        return valid_moves
    
    def __str__(self):
        row_strings = []
        for i in range(num_rows):
            row_list = []
            for j in range(num_cols):
                if active_states[i,j]:
                    if self.state[i][j] == 0:
                        row_list.append('#' % self.state[i,j])
                    elif self.state[i][j] == 1:
                        row_list.append(colored('X' % self.state[i,j], 'red'))
                    elif self.state[i][j] == -1:
                        row_list.append(colored('O' % self.state[i,j], 'green'))
                    # row_list.append('%2i' % self.state[i,j])
                else:
                    if np.any(active_states[:i, j]) and np.any(active_states[(i+1):,j]):
                        mid_column_flag = True
                    else:
                        mid_column_flag = False
                    if np.any(active_states[i,:j]) and np.any(active_states[i,(j+1):]):
                        mid_row_flag = True
                    else:
                        mid_row_flag = False
                    # if mid_column_flag and mid_row_flag:
                    #     row_list.append(colored('+', 'white', attrs=['dark']))
                    if mid_column_flag:# and (not mid_row_flag):
                        row_list.append(colored('|', 'white', attrs=['dark']))
                    # elif mid_row_flag and (not mid_column_flag):
                    #     row_list.append(colored('-', 'white', attrs=['dark']))
                    else:
                        row_list.append(colored('.', 'white', attrs=['dark']))
            row_string = ' '.join(row_list)
            row_strings.append('%2i:  ' % i + row_string)
        
        x_sums = np.sum(self.state == 1, axis=0)
        x_list = []
        for j in range(num_cols):
            x_list.append('%i' % x_sums[j])
        x_string = colored('\n X:  ', 'red') + ' '.join(x_list)

        o_sums = np.sum(self.state == -1, axis=0)
        o_list = []
        for j in range(num_cols):
            o_list.append('%i' % o_sums[j])
        o_string = colored('\n O:  ', 'green') + ' '.join(o_list)

        return('\n'.join(row_strings) + '\n' + x_string + o_string + '\n')

class Opponent(object):
    def __init__(self, player_number=-1):
        start_time = time.time()
        self.player_number = player_number
        self.g = nx.Graph()
        print("Please wait while I teach myself to play Sim-%i." % n)
        print("This may take a few minutes.")
        self.initialize_evaluation_graph()
        stop_time = time.time()
        print("Elapsed time: %f" % (stop_time - start_time))
        print("I'm ready to play. You go first.\n")

    def initialize_evaluation_graph(self):
        self.g = nx.DiGraph()
        dummy_game_board = GameBoard()
        state_hash = compute_state_hash(dummy_game_board.state)
        self.g.add_node(state_hash, state=dummy_game_board.state, current_player_number=1)
        self.add_eg_children(state_hash, current_player_number=1)
        print(len(self.g.nodes))

    def add_eg_children_prelude(self, node):
        # node_data = dict(self.g.nodes.items())
        current_board = GameBoard()
        # current_board.state = node_data[node]['state']
        current_board.state = self.g.nodes[node]['state']
        current_state_hash = compute_state_hash(current_board.state)
        return current_board, current_state_hash

    def prepare_next_board(self, current_board, current_player_number, move):
            # next_board = copy.deepcopy(current_board)
            # next_board.update_board(current_player_number, move)
            # next_state_hash = compute_state_hash(next_board.state)
            # next_board = current_board
            # next_board.update_board(current_player_number, move)
            # next_state_hash = compute_state_hash(next_board.state)
            next_board = GameBoard()
            next_board.state = np.copy(current_board.state)
            next_board.update_board(current_player_number, move)
            next_state_hash = compute_state_hash(next_board.state)
            return next_board, next_state_hash

    def add_edge_to_existing_node(self, current_state_hash, next_state_hash, move, child_rewards):
        self.g.add_edge(current_state_hash, next_state_hash, move=move)
        # temp = dict(self.g.nodes.items())
        reward = self.g.nodes[next_state_hash]['reward']
        child_rewards.append(reward)

    def add_new_node(self, current_state_hash, next_board, next_state_hash, next_player_number, move):
        self.g.add_node(next_state_hash, state=next_board.state, current_player_number=next_player_number)
        self.g.add_edge(current_state_hash, next_state_hash, move=move)

    def add_eg_children(self, node, current_player_number, alpha=-np.inf, beta=np.inf):
        current_board, current_state_hash = self.add_eg_children_prelude(node)

        valid_moves = current_board.get_valid_moves()
        child_rewards = []
        for move in valid_moves:
            next_player_number = current_player_number * -1
            next_board, next_state_hash = self.prepare_next_board(current_board, current_player_number, move)

            if next_state_hash in self.g:
                self.add_edge_to_existing_node(current_state_hash, next_state_hash, move, child_rewards)
                continue

            self.add_new_node(current_state_hash, next_board, next_state_hash, next_player_number, move)

            if next_board.check_win_condition(1):
                reward = -self.player_number
                nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
            elif next_board.check_win_condition(-1):
                reward = self.player_number
                nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
            elif len(next_board.get_valid_moves()) == 0:
                reward = 0
                nx.set_node_attributes(self.g, {next_state_hash: {'reward': reward}})
            else:
                # if len(child_rewards) == 0:
                #     new_alpha = -np.inf
                #     new_beta = np.inf
                # else:
                #     new_alpha = max(child_rewards)
                #     new_beta = min(child_rewards)
                reward = self.add_eg_children(next_state_hash, next_player_number)#, alpha=new_alpha, beta=new_beta)

            child_rewards.append(reward)

            # if self.player_number == next_player_number:
            #     if reward < alpha:
            #         break
            # if self.player_number != next_player_number:
            #     if reward > beta:
            #         break

        if self.player_number == current_player_number:
            current_reward = 1.0 * max(child_rewards)
        else:
            current_reward = 1.0 * min(child_rewards)

        nx.set_node_attributes(self.g, {current_state_hash: {'reward': current_reward}})
        
        return current_reward

    def make_random_move(self, game_board):
        valid_moves = game_board.get_valid_moves()
        row_number = random.choice(valid_moves)
        game_board.update_board(self.player_number, row_number)

    def make_good_random_move(self, game_board):
        current_state_hash = compute_state_hash(game_board.state)
        # rewards = nx.get_node_attributes(self.g, 'reward')
        # moves = nx.get_edge_attributes(self.g, 'move')
        next_states = list(self.g.successors(current_state_hash))
        max_reward = max([self.g.nodes[x]['reward'] for x in next_states])
        good_next_states = [x for x in next_states if self.g.nodes[x]['reward'] == max_reward]
        chosen_next_state = random.choice(good_next_states)
        # location = moves[(current_state_hash, chosen_next_state)]
        location = self.g.edges[(current_state_hash, chosen_next_state)]['move']
        game_board.update_board(self.player_number, location)

    
if __name__ == "__main__":
    game_board = GameBoard()
    opponent = Opponent(player_number=1)

    winner = 2
    current_player = 1
    while winner == 2:
        if all(game_board.state[active_states] != 0):
            winner = 0
            continue

        print(game_board)
        # rewards = nx.get_node_attributes(opponent.g, 'reward')
        hash = compute_state_hash(game_board.state)
        # print(rewards[hash])
        print(opponent.g.nodes[hash]['reward'])
        if opponent.player_number == current_player:
            opponent.make_good_random_move(game_board)
        else:
            valid_move_flag = False
            valid_moves = game_board.get_valid_moves()
            while not valid_move_flag:
                print('The valid moves are: ', valid_moves)
                row_number = int(input('Enter the row for your move: '))
                if row_number in valid_moves:
                    valid_move_flag = True
                    game_board.update_board(current_player, row_number)
                else:
                    print("Invalid move, please try again.\n")
                    print(game_board)
        loss_flag = game_board.check_loss_condition(current_player)
        if loss_flag:
            winner = -1 * current_player
        current_player *= -1

    print(game_board)
    if winner == 1:
        print('The winner is: ' + colored('X', 'red'))
    elif winner == -1:
        print('The winner is: ' + colored('O', 'green'))
    else:
        print('The game is a draw.')