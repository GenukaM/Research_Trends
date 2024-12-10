import pygame
import random
import heapq
from enum import Enum

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE =20
CELL_SIZE = 30
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Maze Layout
maze = [
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2,2,0,0,0,2,2,2,2,2,2,2,2], 
]

# NPC and FSM Logic
class NPCState(Enum):
    IDLE = 0
    MOVING = 1
    GOAL_REACHED = 2

class NPC:
    def __init__(self, start, goal):
        self.position = start
        self.goal = self.validate_goal(goal)  # Ensure goal is valid
        self.path = self.calculate_path(start, self.goal)
        self.fsm = NPCState.MOVING
        self.speed = 25  # Slower speed for movement
        self.frame_counter = 0

    def validate_goal(self, goal):
        """Ensure that the goal is in an open space."""
        x, y = goal
        if maze[y][x] != 0:  # If the goal is not open, find a new valid goal
            # For simplicity, let's find the first available open space for the goal
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if maze[j][i] == 0 and j == 0:  # Goal is on top row
                        return (i, j)
        return goal

    def calculate_path(self, start, goal):
        """A* pathfinding."""
        return self.a_star(start, goal)

    def a_star(self, start, goal):
        """A* algorithm to find the shortest path."""
        open_list = []
        closed_list = set()
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        heapq.heappush(open_list, (f_score[start], start))

        while open_list:
            _, current = heapq.heappop(open_list)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            closed_list.add(current)

            for neighbor in self.get_neighbors(current):
                if neighbor in closed_list:
                    continue

                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

        return []

    def heuristic(self, a, b):
        """Heuristic for A*: Manhattan distance."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):
        """Get valid neighboring positions considering the maze."""
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] != 2:
                neighbors.append((nx, ny))
        return neighbors

    def update(self):
        """Move along the path with a delay between steps."""
        if self.fsm == NPCState.MOVING and self.path:
            self.frame_counter += 1  # Increment the frame counter
            if self.frame_counter >= self.speed:  # Only move after a certain number of frames
                self.frame_counter = 0
                self.position = self.path.pop(0)
                if not self.path:  # Goal reached
                    self.fsm = NPCState.GOAL_REACHED

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class Barriers:
    def __init__(self):
        self.barriers = []
        self.frame_counter = 0
        self.travel_counter = 0  # New counter to track node travel distance

    def spawn_barrier(self):
        """Spawn a barrier at a random top position."""
        x = random.randint(0, GRID_SIZE - 1)
        while maze[0][x] == 2:  # Ensure barrier spawns in open space
            x = random.randint(0, GRID_SIZE - 1)
        self.barriers.append((x, 0))

    def update(self):
        """Move barriers down and spawn a new one after they travel 2 nodes."""
        self.frame_counter += 1
        if self.frame_counter % 12 == 0:  # Slow barrier speed (move every 8 frames)
            self.frame_counter = 0
            new_barriers = []
            for x, y in self.barriers:
                maze[y][x] = 0  # Clear previous position
                if y + 1 < GRID_SIZE:
                    new_barriers.append((x, y + 1))
                    if y + 1 > 1:  # Check if a barrier has traveled two nodes
                        self.travel_counter += 1  # Increment travel counter
            self.barriers = new_barriers

            # Spawn a new barrier after one has traveled 2 nodes
            if self.travel_counter >= len(self.barriers) * 4: # Delay condition
                self.travel_counter = 0  # Reset counter
                self.spawn_barrier()

    def draw(self, screen):
        for x, y in self.barriers:
            pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Metrics Tracking
collision_count = 0
success_count = 0
nodes_traveled = 0
previous_position = None  # To track NPC's last position
start_time = pygame.time.get_ticks()
end_time = 0

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Maze Game")
clock = pygame.time.Clock()

# Game Variables
start_x = random.randint(0, GRID_SIZE - 1)
while maze[GRID_SIZE - 1][start_x] == 2:  # Ensure the start is not in a blocked space
    start_x = random.randint(0, GRID_SIZE - 1)
npc = NPC((start_x, GRID_SIZE - 1), (random.randint(0, GRID_SIZE - 1), 0))  # Start from random bottom row, goal at random top row
barriers = Barriers()

# Main Game Loop
running = True
while running:
    screen.fill(WHITE)

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update Game Logic
    npc.update()
    barriers.update()

    # Track nodes traveled only when NPC moves
    if previous_position != npc.position:
        nodes_traveled += 1
        previous_position = npc.position

    # Draw Maze
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color = WHITE
            if maze[y][x] == 2:
                color = GRAY
            elif maze[y][x] == 1:
                color = BLUE
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

    # Draw NPC and Barriers
    npc.draw(screen)
    barriers.draw(screen)

    # Check for collisions with barriers
    if npc.position in barriers.barriers:
        # Update metrics for collision
        collision_count += 1
        end_time = pygame.time.get_ticks()
        elapsed_time = (end_time - start_time) / 1000.0

        print(f"Collision! Time Elapsed: {elapsed_time:.2f}s, Nodes Traveled: {nodes_traveled},Collision Rate: {collision_count / (success_count + collision_count):.2%}, Success Rate: {success_count / (success_count + collision_count):.2%}")
        start_time = pygame.time.get_ticks()  # Reset timer
        nodes_traveled = 0  # Reset traveled nodes
        previous_position = None  # Reset previous position

        # Reset game
        start_x = random.randint(0, GRID_SIZE - 1)
        while maze[GRID_SIZE - 1][start_x] == 2:
            start_x = random.randint(0, GRID_SIZE - 1)
        npc = NPC((start_x, GRID_SIZE - 1), (random.randint(0, GRID_SIZE - 1), 0))  # Reset NPC

    # Check if NPC reached the goal
    if npc.fsm == NPCState.GOAL_REACHED:
        # Update metrics for success
        success_count += 1
        end_time = pygame.time.get_ticks()
        elapsed_time = (end_time - start_time) / 1000.0

        print(f"Success! Time Elapsed: {elapsed_time:.2f}s, Nodes Traveled: {nodes_traveled},  Collision Rate: {collision_count / (success_count + collision_count):.2%}, Success Rate: {success_count / (success_count + collision_count):.2%},")
        start_time = pygame.time.get_ticks()  # Reset timer
        nodes_traveled = 0  # Reset traveled nodes
        previous_position = None  # Reset previous position

        # Reset game
        start_x = random.randint(0, GRID_SIZE - 1)
        while maze[GRID_SIZE - 1][start_x] == 2:
            start_x = random.randint(0, GRID_SIZE - 1)
        npc = NPC((start_x, GRID_SIZE - 1), (random.randint(0, GRID_SIZE - 1), 0))  # Reset NPC

    # Display metrics on the screen
    font = pygame.font.SysFont(None, 24)
    collision_text = font.render(f"Collisions: {collision_count}", True, BLACK)
    success_text = font.render(f"Successes: {success_count}", True, BLACK)
    nodes_text = font.render(f"Nodes Traveled: {nodes_traveled}", True, BLACK)
    screen.blit(collision_text, (10, 10))
    screen.blit(success_text, (10, 40))
    screen.blit(nodes_text, (10, 70))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

