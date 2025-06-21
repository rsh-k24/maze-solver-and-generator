from collections import deque
from random import choice
from constants import ACTION_MAP

class Maze:
    # handles maze generation, storage, and pathfinding
    def __init__(self, rows, cols):
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1
        self.rows = rows
        self.cols = cols
        
        print(f"Generating a {self.rows}x{self.cols} maze...")
        self.layout, self.start_pos, self.exit_pos = self._generate_layout()
        print(f"-> Player Start: {self.start_pos}, Exit: {self.exit_pos}")

        self.shortest_path_length = self._find_shortest_path_bfs()
        if self.shortest_path_length == -1:
            print("!!! WARNING: Generated an unsolvable maze. This is rare and should not happen with this algorithm.")
        else:
            print(f"-> Optimal path length is {self.shortest_path_length} steps.")

    def _generate_layout(self):
        # algorithm called recursive backtracking
        # dont FULLY understand this yet
        # TODO read more about the algorithms
        # understand the steps taken, but not how they make a maze

        maze = [['W' for _ in range(self.cols)] for _ in range(self.rows)] # fill with walls initially
        # stacks of trails left behid
        stack = []

        start_row, start_col = (1, 1)
        # turns our starting point into a path (not wall)
        maze[start_row][start_col] = ' '
        stack.append((start_row, start_col)) # add to the trail stack

        # as long as there are trails that haven't been backtracked to
        while stack:
            # our position is the last trail we left
            current_row, current_col = stack[-1]

            # find unvisited neighbors 2 cells away
            # this list stores the possible coordinates to make a path to
            neighbors = []
            # it checks up down left and right TWO spots away not one
            for row_delta, col_delta in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                neighbor_row, neighbor_col = current_row + row_delta, current_col + col_delta
                # if it's in bounds and available to make a path
                if 0 < neighbor_row < self.rows-1 and 0 < neighbor_col < self.cols-1 and maze[neighbor_row][neighbor_col] == 'W':
                    neighbors.append((neighbor_row, neighbor_col))

            # if there ARE points to make a path to:
            if neighbors:
                # random choice of available points to make a path to (crucial for variation)
                next_row, next_col = choice(neighbors)

                # break wall between current cell and chosen neighbor
                wall_row = current_row + (next_row - current_row) // 2
                wall_col = current_col + (next_col - current_col) // 2
                maze[wall_row][wall_col] = ' ' # turn wall into a path
                
                maze[next_row][next_col] = ' '
                # leave another trail in the stack
                stack.append((next_row, next_col))
            else:
                # if there aren't any neighbours available to go to
                # then simply go back to the last point where you WERE able to make a trail
                # and simply try another path
                stack.pop()

        # MAZE GENERATION COMPLETE
        # now player, entry, exit

        player_start_pos = (1, 1)
        
        # make a point of exit far from the starting point
        # choose from a list of possible exits stored in this list
        possible_exits = []
        # Iterate over all valid path cells to find a valid exit
        for r in range(1, self.rows, 2):
            for c in range(1, self.cols, 2):
                if (r, c) != player_start_pos:
                    possible_exits.append((r, c))
        
        # now calculate which one is the furtherest
        farthest_exit = None
        max_dist = -1

        for pos in possible_exits:
            # how many steps up/down and how many steps left/right?
            # then add these two to find total distance
            distance = abs(pos[0] - player_start_pos[0]) + abs(pos[1] - player_start_pos[1])
            # if this distance is more than the last highest, its the new highest
            if distance > max_dist:
                max_dist = distance
                farthest_exit = pos
        exit_pos = farthest_exit

        # Mark player and exit on the layout
        maze[player_start_pos[0]][player_start_pos[1]] = 'P'
        maze[exit_pos[0]][exit_pos[1]] = 'E'
        
        return ["".join(row) for row in maze], player_start_pos, exit_pos

    def _find_shortest_path_bfs(self):
        # Finds the shortest path from start to exit using Breadth-First Search
        queue = deque([(self.start_pos, 0)]) # ((row, col), distance)
        visited = {self.start_pos}
        
        while queue:
            (row, col), distance = queue.popleft()
            
            if (row, col) == self.exit_pos: 
                return distance
            
            for row_delta, col_delta, _ in ACTION_MAP.values():
                next_row, next_col = row + row_delta, col + col_delta
                
                # Check if the next cell is valid and unvisited
                if 0 <= next_row < self.rows and 0 <= next_col < self.cols and \
                   self.layout[next_row][next_col] != 'W' and (next_row, next_col) not in visited:
                    visited.add((next_row, next_col))
                    queue.append(((next_row, next_col), distance + 1))
        return -1 # Should not be reached in a valid maze
