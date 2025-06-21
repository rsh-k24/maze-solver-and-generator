import pygame
import sys
import argparse
from random import randint

from constants import *
from maze import Maze
from agent import RLAgent
from game import Game

def get_user_config():
    print("--- Configuration Setup ---")

    def get_int_input(prompt, default):
        while True:
            try:
                val = input(f"{prompt} (default: {default}): ")
                return int(val) if val else default
            except ValueError:
                print("Invalid input. Please enter a whole number. \n")

    def get_float_input(prompt, default):
        while True:
            try:
                val = input(f"{prompt} (default: {default}): ")
                return float(val) if val else default
            except ValueError:
                print("Invalid input. Please enter a number. \n")

    rows = get_int_input("Enter maze row number (approximate, +-4)", 21)
    cols = get_int_input("Enter maze column number (approximate, +-6)", 31)

    # Scaling factor
    base_area = 20 * 20
    area = rows * cols
    scale = area / base_area

    # Scaled defaults
    default_episodes = int(20000 * scale ** 1.2)
    default_step_penalty = max(-0.1 / scale ** 0.3, -0.01)
    default_lr = max(0.5 / scale ** 0.2, 0.05)
    default_gamma = min(0.99 + min(scale ** 0.05 * 0.01, 0.009), 0.999)
    default_epsilon_decay = 0.9998 ** (1 / scale ** 0.5)
    default_num_mazes = 5

    config = {
        'rows': rows,
        'cols': cols,
        'episodes': get_int_input("How many training episodes?", default_episodes),
        'step_penalty': get_float_input("Penalty for steps?", default_step_penalty),
        'lr': get_float_input("Learning Rate (e.g., 0.5)", default_lr),
        'gamma': get_float_input("Discount Factor (e.g., 0.99)", default_gamma),
        'epsilon_decay': get_float_input("Epsilon Decay (e.g., 0.9998)", default_epsilon_decay),
        'num_mazes': get_int_input("Number of mazes to solve?", default_num_mazes),
        'no_cache': False  # not user configurable
    }

    return config


def get_cli_config():
    parser = argparse.ArgumentParser(description="A Reinforcement Learning Maze Solver.")
    parser.add_argument("--rows", type=int, default=21, help="Number of rows in the maze.")
    parser.add_argument("--cols", type=int, default=31, help="Number of columns in the maze.")
    parser.add_argument("--episodes", type=int, default=20000, help="Number of training episodes per maze.")
    parser.add_argument("--step_penalty", type=float, default=-0.1, help="Penalty for each step taken.")
    parser.add_argument("--lr", type=float, default=0.5, help="Learning Rate for the agent.")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount Factor for future rewards.")
    parser.add_argument("--epsilon_decay", type=float, default=0.9998, help="Decay rate for exploration.")
    parser.add_argument("--num_mazes", type=int, default=5, help="Number of mazes to solve in a session.")
    parser.add_argument("--no_cache", action="store_true", help="Force retraining; do not use a cached Q-table.")
    args = parser.parse_args()
    return vars(args) # returns as dictionary

if __name__ == "__main__":
    # use cli or use input?
    if len(sys.argv) > 1:
        config = get_cli_config()
        print("-> Configuration loaded from command-line arguments.")
    else:
        config = get_user_config()
        print("\n-> Configuration set by user.")

    print("\n--- Session Parameters ---")
    for key, value in config.items():
        print(f"  {key.replace('_', ' ').title():<16}: {value}")
    print("--------------------------\n")

    stats = {'success': 0, 'failed': 0, 'total': 0}

    for i in range(config['num_mazes']):
        print(f"\n--- Maze {i+1}/{config['num_mazes']} ---")
        stats['total'] += 1
        
        # random maze size for variety
        current_rows = config['rows'] + randint(-2, 2) * 2
        current_cols = config['cols'] + randint(-3, 3) * 2
        
        maze = Maze(rows=max(7, current_rows), cols=max(7, current_cols))

        agent = RLAgent(
            learning_rate=config['lr'],
            discount_factor=config['gamma'],
            epsilon_start=1.0,
            epsilon_end=0.01,
            epsilon_decay=config['epsilon_decay'],
            step_penalty=config['step_penalty']
        )
        
        q_table_filename = f"q_table_{maze.rows}x{maze.cols}.pkl"
        
        if not config['no_cache'] and agent.load_q_table(q_table_filename):
            pass # Q-table loaded, no training needed
        else:
            agent.train(maze, num_episodes=config['episodes'])
            agent.save_q_table(q_table_filename)

        # this loop handles retries
        while True:
            game = Game(maze, agent)
            result = game.run() # this loop runs until a key press (N, R, Q) or game over

            if result in ["success", "failed_timeout"]:
                # wait for user to press N, R, or Q after game ends
                while True:
                    user_action = None
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: 
                            user_action = "quit"
                            break
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                user_action = "quit"
                                break
                            if event.key == pygame.K_n:
                                user_action = "next_maze"
                                break
                            if event.key == pygame.K_r:
                                user_action = "retry"
                                break

                    if user_action: 
                        break
                    pygame.time.wait(50)
                
                if user_action == "retry": 
                    continue
                # For next_maze or quit, handle stats and break the retry loop
                if result == "success": 
                    stats['success'] += 1
                else: 
                    stats['failed'] += 1
                result = user_action
                break

            elif result == "retry":
                print("-> Retrying the same maze...")
                continue # re run the game loop on the same maze
            else:
                break

        if result == "quit":
            print("-> User chose to quit the session.")
            break
            
    print("\n--- Session Summary ---")
    print(f"Mazes Attempted: {stats['total']}")
    print(f"Successful Solves: {stats['success']}")
    print(f"Failed Solves: {stats['failed']}")
    print("Exiting.")
    
    pygame.quit()
    sys.exit()
