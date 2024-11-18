import pygame
import heapq
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Simple maze
maze = [
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 1, 1, 0]
]
GRID_SIZE = len(maze)

# A* Pathfinding Algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(maze, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Reverse the path

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and maze[neighbor[1]][neighbor[0]] == 0:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

# FSM States
class NPCState:
    IDLE = "Idle"
    MOVING = "Moving"
    GOAL_REACHED = "GoalReached"

class NPC:
    def __init__(self, start, goal, speed=10):
        self.position = start
        self.goal = goal
        self.path = astar(maze, start, goal)
        self.state = NPCState.IDLE if not self.path else NPCState.MOVING
        self.speed = speed  # Determines how often to update the position (lower is faster)
        self.frame_counter = 0  # Frame counter to control speed

    def update(self):
        # Increment frame counter
        self.frame_counter += 1

        if self.state == NPCState.MOVING and self.frame_counter >= self.speed:
            # Move to the next position in the path
            if self.path:
                self.position = self.path.pop(0)
            if not self.path:
                self.state = NPCState.GOAL_REACHED

            # Reset frame counter
            self.frame_counter = 0

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# Utility to find a random empty cell
def get_random_empty_cell():
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if maze[y][x] == 0:
            return (x, y)

# Main function
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NPC Pathfinding with FSM and A*")
    clock = pygame.time.Clock()

    # Initial Start and Goal positions
    start = get_random_empty_cell()
    goal = get_random_empty_cell()
    while start == goal:  # Ensure start and goal are not the same
        goal = get_random_empty_cell()

    # Create NPC
    npc = NPC(start, goal)

    running = True
    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check if the NPC reached the goal
        if npc.state == NPCState.GOAL_REACHED:
            # Generate new start and goal points
            start = get_random_empty_cell()
            goal = get_random_empty_cell()
            while start == goal:
                goal = get_random_empty_cell()

            # Reinitialize NPC
            npc = NPC(start, goal)

        # Draw maze
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                color = BLACK if maze[y][x] == 1 else WHITE
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # Draw goal
        pygame.draw.rect(screen, GREEN, (goal[0] * CELL_SIZE, goal[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Update and draw NPC
        npc.update()
        npc.draw(screen)

        # Display update
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
