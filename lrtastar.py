import pygame
import random
import heapq
from enum import Enum

# Constants
WIDTH, HEIGHT = 600, 600
GRID_WIDTH, GRID_HEIGHT = 3, 20  # 3 lanes (width) and 20 height
CELL_SIZE = 30
FPS = 10  # Slow down the frame rate for better visualization

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Maze Layout (Road with 3 lanes)
maze = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]  # All cells are open spaces (0)

# NPC and FSM Logic
class NPCState(Enum):
    IDLE = 0
    MOVING = 1
    GOAL_REACHED = 2


class NPC:
    def __init__(self, start, goal):
        self.position = start
        self.previous_position = None  # Track the previous position
        self.goal = goal
        self.path = [start]  # Incremental path construction starts with the start position
        self.visited = []  # Track visited cells for backtracking
        self.fsm = NPCState.MOVING
        self.speed = 1  # Move one node at a time
        self.frame_counter = 0

    def heuristic(self, a, b):
        """Manhattan distance as heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):
        """Get valid neighboring positions considering the maze"""
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and maze[ny][nx] == 0:
                neighbors.append((nx, ny))
        return neighbors

    def update(self, barriers):
        """Incrementally calculate the next step with backtracking and heuristic updates."""
        if self.fsm != NPCState.MOVING:
            return

        current = self.position
        self.visited.append(current)

        # If we've reached the goal, stop
        if current == self.goal:
            self.fsm = NPCState.GOAL_REACHED
            return

        neighbors = self.get_neighbors(current)
        if not neighbors:
            print(f"No valid neighbors for {current}. Backtracking...")
            self.backtrack()
            return

        # Choose the best neighbor based on heuristic
        next_cell = min(neighbors, key=lambda n: self.heuristic(n, self.goal))
        self.update_heuristic(current, next_cell)

        # Handle backtracking if we're revisiting
        if next_cell in self.visited:
            print(f"Revisiting {next_cell}. Backtracking...")
            self.backtrack()
            return

        # Move to the chosen neighbor
        self.previous_position = self.position
        self.position = next_cell
        self.path.append(next_cell)

    def backtrack(self):
        """Remove the last step and move to the previous position."""
        if len(self.path) > 1:
            self.path.pop()
            self.position = self.path[-1]
        else:
            print("No path to backtrack. Stuck!")

    def update_heuristic(self, current, next_cell):
        """Update the heuristic dynamically."""
        current_h = self.heuristic(current, self.goal)
        next_h = self.heuristic(next_cell, self.goal)
        maze[current[1]][current[0]] = min(current_h, next_h)

    def draw(self, screen):
        """Draw the NPC (red rectangle) on the screen."""
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


class Barrier:
    def __init__(self):
        self.barriers = []
        self.frame_counter = 0
        self.initial_spawned = False

    def spawn_barrier(self):
        """Spawn a barrier at a random top row (row 0)."""
        x = random.randint(0, GRID_WIDTH - 1)  # Random column
        self.barriers.append((x, 0))  # Spawn in the top row

    def update(self):
        """Move barriers down one step and respawn them in the top row when they reach the bottom."""
        if not self.initial_spawned:
            # Initial spawn of 4 vehicles
            for _ in range(4):
                self.barriers.append((random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)))  # Full random placement
            self.initial_spawned = True

        # Move barriers down by one step
        new_barriers = []
        for x, y in self.barriers:
            maze[y][x] = 0  # Clear the previous position
            if y + 1 < GRID_HEIGHT:
                new_barriers.append((x, y + 1))  # Move down
            else:
                # Respawn in the top row
                self.spawn_barrier()

        self.barriers = new_barriers

    def draw(self, screen):
        for x, y in self.barriers:
            pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def check_collision(self, npc_position, npc_previous_position):
        """Check if NPC collides or crosses paths with any barrier."""
        for x, y in self.barriers:
            # Direct collision
            if (x, y) == npc_position:
                return True
            # Path crossing detection
            barrier_previous_position = (x, y - 1)  # Previous position of the barrier
            if npc_position == barrier_previous_position and npc_previous_position == (x, y):
                return True
        return False


def draw_grid(screen, npc, barriers):
    screen.fill(WHITE)
    # Draw maze grid (Road)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WHITE
            if maze[y][x] == 1:  # If there is a barrier
                color = GRAY
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    # Draw NPC and Barriers
    npc.draw(screen)
    barriers.draw(screen)

    pygame.display.update()


def restart_game(npc, barriers):
    """Restart the game by resetting the maze, NPC, and barriers."""
    global maze
    maze = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]  # Reset maze

    # Reset NPC's position and goal
    npc.position = (random.randint(0, GRID_WIDTH - 1), GRID_HEIGHT - 1)  # Start at a random bottom position
    npc.previous_position = None  # Reset previous position
    npc.goal = (random.randint(0, GRID_WIDTH - 1), 0)  # Set a random top goal
    npc.path = [npc.position]  # Start a fresh path
    npc.visited = []  # Clear visited nodes
    npc.fsm = NPCState.MOVING  # Set NPC state to moving

    # Reset barriers
    barriers.barriers.clear()
    barriers.initial_spawned = False
    barriers.frame_counter = 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("LRTA* Dynamic Road")
    clock = pygame.time.Clock()

    # Initialize NPC and barriers
    npc = NPC(start=(random.randint(0, GRID_WIDTH - 1), GRID_HEIGHT - 1), goal=(random.randint(0, GRID_WIDTH - 1), 0))
    barriers = Barrier()

    frame_counter = 0  # Shared counter for synchronized movement
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Increment the shared frame counter
        frame_counter += 1

        # Update NPC and barriers only once every frame
        if frame_counter % FPS == 0:
            barriers.update()
            npc.update(barriers)

        # Check for collision or path crossing
        if barriers.check_collision(npc.position, npc.previous_position):
            print("Collision detected! Restarting game...")
            restart_game(npc, barriers)

        # Check if the NPC reached the goal
        if npc.fsm == NPCState.GOAL_REACHED:
            print("Goal reached! Restarting game...")
            restart_game(npc, barriers)

        # Draw the grid, NPC, and barriers
        draw_grid(screen, npc, barriers)

        # Control the frame rate
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
