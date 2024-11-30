import pygame
import random
from enum import Enum

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Maze Layout
maze = [
    [2, 2, 0, 0, 0, 0, 0, 0, 2, 2],
    [2, 2, 0, 1, 0, 0, 0, 0, 2, 2],
    [2, 2, 0, 0, 0, 0, 0, 0, 2, 2],
    [2, 2, 0, 0, 1, 0, 0, 0, 2, 2],
    [2, 2, 0, 0, 0, 0, 0, 0, 2, 2],
    [2, 2, 0, 0, 1, 0, 0, 0, 2, 2],
    [2, 2, 0, 0, 0, 0, 0, 0, 2, 2],
    [2, 2, 1, 0, 0, 0, 0, 0, 2, 2],
    [2, 2, 0, 0, 1, 0, 0, 0, 2, 2],
    [2, 2, 0, 0, 0, 0, 0, 0, 2, 2],
]

# FSM for NPC states
class NPCState(Enum):
    IDLE = 0
    MOVING = 1
    GOAL_REACHED = 2

class FSM:
    def __init__(self):
        self.state = NPCState.IDLE

    def transition(self, new_state):
        self.state = new_state

# Exception for collision detection
class CollisionException(Exception):
    pass

# NPC class
class NPC:
    def __init__(self, start, goal, speed=20):
        self.position = start
        self.goal = goal
        self.path = self.calculate_path(start, goal)
        self.fsm = FSM()
        self.fsm.transition(NPCState.MOVING if self.path else NPCState.IDLE)
        self.speed = speed
        self.frame_counter = 0

    def calculate_path(self, start, goal):
        path = [start]
        while path[-1] != goal:
            x, y = path[-1]
            if x < goal[0]:
                x += 1
            elif x > goal[0]:
                x -= 1
            elif y < goal[1]:
                y += 1
            elif y > goal[1]:
                y -= 1
            path.append((x, y))
        return path

    def update(self):
        self.frame_counter += 1

        if self.fsm.state == NPCState.MOVING and self.frame_counter >= self.speed:
            if self.path:
                next_position = self.path.pop(0)
                if maze[next_position[1]][next_position[0]] == 1:
                    raise CollisionException
                self.position = next_position
            if not self.path:
                self.fsm.transition(NPCState.GOAL_REACHED)
            self.frame_counter = 0

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class MovingBarriers:
    def __init__(self, speed=15):
        self.directions = {}
        self.frame_counter = 0
        self.speed = speed  # Number of frames to wait before moving

    def initialize_directions(self):
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 1:
                    self.directions[(x, y)] = random.choice([-1, 1])

    def update(self):
        # Increment frame counter
        self.frame_counter += 1

        # Only update when frame counter reaches the speed threshold
        if self.frame_counter < self.speed:
            return
        self.frame_counter = 0  # Reset counter after updating

        # Create a copy of the maze to work with
        new_maze = [row[:] for row in maze]

        for (x, y), direction in list(self.directions.items()):
            new_x = x + direction

            # Ensure the new position is within bounds and not blocked
            if new_x < 0 or new_x >= GRID_SIZE or maze[y][new_x] == 2:
                # Reverse direction if at boundary or blocked
                self.directions[(x, y)] *= -1
                new_x = x + self.directions[(x, y)]

            # Move the barrier only if the target cell is empty
            if maze[y][new_x] == 0:
                new_maze[y][x] = 0  # Clear the current position
                new_maze[y][new_x] = 1  # Move the barrier to the new position
                self.directions[(new_x, y)] = self.directions.pop((x, y))  # Update the direction for the new position

        # Update the maze with new barrier positions
        for y in range(GRID_SIZE):
            maze[y] = new_maze[y]



# Helper functions
def get_start():
    row = GRID_SIZE - 1
    col = random.choice([i for i, val in enumerate(maze[row]) if val == 0])
    return (col, row)

def get_goal():
    row = 0
    col = random.choice([i for i, val in enumerate(maze[row]) if val == 0])
    return (col, row)

# Main function
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("A* Maze Pathfinding")
    clock = pygame.time.Clock()

    moving_barriers = MovingBarriers()
    moving_barriers.initialize_directions()

    start = get_start()
    goal = get_goal()
    npc = NPC(start, goal)

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            moving_barriers.update()

            if npc.fsm.state == NPCState.GOAL_REACHED:
                start = get_start()
                goal = get_goal()
                npc = NPC(start, goal)

            # Draw maze
            for y in range(len(maze)):
                for x in range(len(maze[y])):
                    color = BLACK if maze[y][x] == 1 else GRAY if maze[y][x] == 2 else WHITE
                    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

            # Draw goal
            pygame.draw.rect(screen, GREEN, (goal[0] * CELL_SIZE, goal[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            npc.update()
            npc.draw(screen)

        except CollisionException:
            start = get_start()
            goal = get_goal()
            npc = NPC(start, goal)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
