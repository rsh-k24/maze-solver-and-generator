same 3 drill for this
import pygame
from constants import TILE_SIZE, COLOR_PLAYER

class Player:
    def __init__(self, start_pos, maze_rows, maze_cols):
        self.start_pos = start_pos
        self.row, self.col = start_pos
        self.maze_rows = maze_rows
        self.maze_cols = maze_cols
        self.radius = int(TILE_SIZE * 0.35)

    def move(self, row_delta, col_delta, maze_layout):
        # moves the player and returns if it managed to move or not, and the reason why
        next_row = self.row + row_delta
        next_col = self.col + col_delta
        
        if not (0 <= next_row < self.maze_rows and 0 <= next_col < self.maze_cols):
            return False, "boundary"
        if maze_layout[next_row][next_col] == 'W':
            return False, "wall"
            
        self.row, self.col = next_row, next_col
        return True, "moved"

    def draw(self, screen):
        center_x = self.col * TILE_SIZE + TILE_SIZE // 2
        center_y = self.row * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, COLOR_PLAYER, (center_x, center_y), self.radius)

    def reset(self):
        # back to start
        self.row, self.col = self.start_pos
