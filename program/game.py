import pygame
from constants import *
from player import Player
from maze import Maze

class Game:
    # Manages the pygame window
    def __init__(self, maze, agent):
        pygame.init()
        info = pygame.display.Info()
        max_width = info.current_w
        max_height = info.current_h - 100  # leave room for taskbar, etc.

        # dynamically adjust TILE_SIZE if maze too big
        max_tile_width = max_width // maze.cols
        max_tile_height = (max_height - INFO_PANEL_HEIGHT) // maze.rows
        self.tile_size = min(max_tile_width, max_tile_height, TILE_SIZE)  # don't exceed original TILE_SIZE

        self.screen_width = maze.cols * self.tile_size
        self.screen_height = maze.rows * self.tile_size + INFO_PANEL_HEIGHT

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

        self.maze = maze
        self.agent = agent
        self.player = Player(maze.start_pos, maze.rows, maze.cols)

        self.screen_width = maze.cols * TILE_SIZE
        self.screen_height = maze.rows * TILE_SIZE + INFO_PANEL_HEIGHT
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Reinforcement Learning Maze Solver")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_large = pygame.font.SysFont("Arial", 22, bold=True)

    def _draw_maze(self):
        # draws the maze on the screen
        for r, row_str in enumerate(self.maze.layout):
            for c, char in enumerate(row_str):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if char == 'W':
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    pygame.draw.rect(self.screen, COLOR_WALL_BORDER, rect, 1)
                elif char in ' P':
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)
                elif char == 'E':
                    pygame.draw.rect(self.screen, COLOR_EXIT_BORDER, rect)
                    inner_rect = rect.inflate(-TILE_SIZE // 4, -TILE_SIZE // 4)
                    pygame.draw.rect(self.screen, COLOR_EXIT, inner_rect)

    def _display_text(self, text, pos, font, color=COLOR_INFO_TEXT):
        # helper to render text
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, pos)

    def _draw_info_panel(self, agent_steps, status_text, status_color):
        # Draws the bottom panel with game information
        panel_rect = pygame.Rect(0, self.maze.rows * TILE_SIZE, self.screen_width, INFO_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_INFO_BG, panel_rect)

        # optimal vs agent Steps
        optimal_text = f"Optimal Steps: {self.maze.shortest_path_length}"
        agent_text = f"Agent Steps: {agent_steps}"
        self._display_text(optimal_text, (20, panel_rect.y + 10), self.font_small)
        self._display_text(agent_text, (20, panel_rect.y + 35), self.font_small)

        self._display_text(status_text, (self.screen_width // 2.5, panel_rect.y + 20), self.font_large, status_color)
        
        controls_text = "N: Next Maze | R: Retry | Q: Quit"
        text_w = self.font_small.render(controls_text, True, COLOR_INFO_TEXT).get_width()
        self._display_text(controls_text, (self.screen_width - text_w - 20, panel_rect.y + 25), self.font_small)

    def run(self):
        # The main loop for running the agent's solution
        self.player.reset()
        agent_steps = 0
        game_over = False
        status_text = "Solving..."
        status_color = COLOR_INFO_TEXT

        max_run_steps = self.maze.rows * self.maze.cols * 2 # generous step limit because it very easily gets stuck

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: return "quit"
                    if event.key == pygame.K_n: return "next_maze"
                    if event.key == pygame.K_r: return "retry"

            if not game_over:
                current_state_key = self.agent._get_state_key(self.player.row, self.player.col)
                
                # agent makes a move (always exploit best knowledge)
                action = self.agent.choose_action(current_state_key, exploit_only=True)
                
                row_delta, col_delta, _ = ACTION_MAP[action]
                self.player.move(row_delta, col_delta, self.maze.layout)
                agent_steps += 1

                # check for win/fail conditions
                if (self.player.row, self.player.col) == self.maze.exit_pos:
                    game_over = True
                    eff = (self.maze.shortest_path_length / agent_steps * 100) if agent_steps > 0 else 0
                    status_text = f"Success! ({eff:.1f}%)"
                    status_color = COLOR_SUCCESS if eff >= 80 else COLOR_WARNING
                    self.screen.fill(COLOR_BACKGROUND)
                    self._draw_maze()
                    self.player.draw(self.screen)
                    self._draw_info_panel(agent_steps, status_text, status_color)
                    pygame.display.flip()

                    return "success"
                elif agent_steps >= max_run_steps:
                    game_over = True
                    status_text = "Failed: Timed Out"
                    status_color = COLOR_FAIL
                    return "failed_timeout"
            
            self.screen.fill(COLOR_BACKGROUND)
            self._draw_maze()
            self.player.draw(self.screen)
            self._draw_info_panel(agent_steps, status_text, status_color)
            pygame.display.flip()
            
            self.clock.tick(20) # can control agent animation speed
