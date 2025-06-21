# CONSTANTS

# Colors
COLOR_BACKGROUND = (30, 30, 40)      # not seen but just in case
COLOR_WALL = (70, 70, 85)            # Grey walls
COLOR_WALL_BORDER = (50, 50, 65)     # Slightly darker borders
COLOR_PATH = (160, 160, 170)         # light grey path
COLOR_PLAYER = (255, 0, 0)           # red player
COLOR_EXIT_BORDER = (255, 215, 0)    # gold exit (border)
COLOR_EXIT = (255, 235, 100)         # gold exit
COLOR_INFO_TEXT = (230, 230, 230)    # text colour
COLOR_INFO_BG = (40, 40, 50)
COLOR_SUCCESS = (100, 255, 100)
COLOR_WARNING = (255, 255, 100)
COLOR_FAIL = (255, 100, 100)
COLOR_MESSAGE_TEXT = (230, 230, 230) # For config display
COLOR_MESSAGE_BG = (50, 50, 60, 200) # For config display

TILE_SIZE = 20
INFO_PANEL_HEIGHT = 60

# RL Agent Actions
# Maps action index to (row_delta, col_delta, direction_name)
ACTION_MAP = {
    0: (-1, 0, 'N'),  # up
    1: (1, 0, 'S'),   # dwon
    2: (0, -1, 'W'),  # left
    3: (0, 1, 'E')    # right
}
NUM_ACTIONS = len(ACTION_MAP)
