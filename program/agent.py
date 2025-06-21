import numpy as np
import pickle
import os
from random import randint, random
from constants import ACTION_MAP, NUM_ACTIONS
from player import Player

class RLAgent:
    # manages the q learning algorithm: q table and training
    def __init__(self, learning_rate, discount_factor, epsilon_start, epsilon_end, epsilon_decay, step_penalty):
        self.q_table = {}
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.step_penalty = step_penalty
        print(f"Agent Initialized with: LR={self.lr}, Gamma={self.gamma}, EpsilonDecay={self.epsilon_decay}")

    def _get_state_key(self, row, col):
        # this may seem redundant, but only made to make purpose clear in code
        # otherwise, it's just using the coordinates for no clear reason
        return (row, col) 

    def _initialize_q_table_for_state(self, state_key):
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(NUM_ACTIONS)

    def choose_action(self, state_key, exploit_only=False):
        # Chooses an action using an explore or exploit
        self._initialize_q_table_for_state(state_key)  
        if not exploit_only and random() < self.epsilon:
            return randint(0, NUM_ACTIONS - 1)  # explore: choose a random action
        else:
            return np.argmax(self.q_table[state_key])  # Exploit: choose the best known action

    def get_reward(self, old_pos, new_pos, move_reason, exit_pos):
        # Calculates the reward for a move
        if move_reason in ("wall", "boundary"): return -10.0
        if new_pos == exit_pos: return 100.0

        # more closer = more reward
        dist_old = abs(old_pos[0] - exit_pos[0]) + abs(old_pos[1] - exit_pos[1])
        dist_new = abs(new_pos[0] - exit_pos[0]) + abs(new_pos[1] - exit_pos[1])

        # +0.1 if goes toward -0.1 if going away
        distance_reward = (dist_old - dist_new) * 0.1

        return self.step_penalty + distance_reward

    def update_q_table(self, state_key, action, reward, next_state_key):
        # updates the Q-table
        self._initialize_q_table_for_state(next_state_key)

        old_q_value = self.q_table[state_key][action]
        max_future_q = np.max(self.q_table[next_state_key])

        # q learning  formula (google Bellman Equation if you forget what it means)
        new_q_value = old_q_value + self.lr * (reward + self.gamma * max_future_q - old_q_value)
        self.q_table[state_key][action] = new_q_value

    def train(self, maze, num_episodes):
        # trains the agent on a maze by just repeating episodes
        # let the reward mechanism handle it
        print(f"Starting training for {num_episodes} episodes...")
        self.epsilon = self.epsilon_start

        player = Player(maze.start_pos, maze.rows, maze.cols)
        max_steps_per_episode = maze.rows * maze.cols

        for episode in range(num_episodes):
            player.reset()
            state_key = self._get_state_key(player.row, player.col)
            total_reward = 0

            for step in range(max_steps_per_episode):
                action = self.choose_action(state_key)
                row_delta, col_delta, _ = ACTION_MAP[action]

                old_pos = (player.row, player.col)
                moved, move_reason = player.move(row_delta, col_delta, maze.layout)
                new_pos = (player.row, player.col)
                next_state_key = self._get_state_key(new_pos[0], new_pos[1])

                reward = self.get_reward(old_pos, new_pos, move_reason, maze.exit_pos)
                total_reward += reward
                
                self.update_q_table(state_key, action, reward, next_state_key)
                state_key = next_state_key

                if new_pos == maze.exit_pos:
                    break

            if self.epsilon > self.epsilon_end:
                self.epsilon *= self.epsilon_decay

            if (episode + 1) % (num_episodes // 20 or 1) == 0:
                print(f"  ...Episode: {episode+1:>6}/{num_episodes}, Steps: {step+1:<4}, Reward: {total_reward:6.1f}, Epsilon: {self.epsilon:.4f}")

        print("Training finished.")

    def save_q_table(self, filepath):
        # saves the q-table to a file using pickle
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self.q_table, f)
            print(f"Q-table saved to {filepath}")
        except IOError as e:
            print(f"Error saving Q-table to {filepath}: {e}")

    def load_q_table(self, filepath):
        # Loads a qtable from a file
        if not os.path.exists(filepath):
            print("No cached Q-table found. A new one will be created during training.")
            return False
        try:
            with open(filepath, 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Q-table successfully loaded from {filepath}")
            return True
        except (pickle.UnpicklingError, EOFError, IOError) as e:
            print(f"Error loading Q-table from {filepath}: {e}. Will train a new one.")
            return False
