import pygame
import heapq
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 10  # Grid size (10x10)
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Maze with barriers
maze = [
    [1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 0, 1, 0, 0, 0, 0, 1, 1],
    [1, 1, 1, 0, 0, 1, 0, 1, 1, 1],
    [1, 1, 0, 1, 0, 1, 0, 0, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 0, 1, 0, 0, 1, 0, 1, 1],
    [1, 1, 0, 0, 1, 0, 0, 0, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
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


# NPC Class (without FSM)
class NPC:
    def __init__(self, start, goal, speed=10):
        self.position = start
        self.goal = goal
        self.path = astar(maze, start, goal)
        self.speed = speed
        self.frame_counter = 0

    def update(self):
        self.frame_counter += 1

        if self.path and self.frame_counter >= self.speed:
            self.position = self.path.pop(0)
            self.frame_counter = 0

        # If the goal is reached, find a new goal
        if not self.path:
            self.position = self.goal
            self.goal = get_random_goal()
            self.path = astar(maze, self.position, self.goal)

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# Utility to find a random empty cell
def get_random_start():
    return (2, GRID_SIZE - 1)  # Fixed start at the first open cell in the bottom row




def get_random_goal():
    while True:
        x = random.randint(1, GRID_SIZE - 2)
        if maze[0][x] == 0:
            return (x, 0)


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Car Pathfinding with A*")
    clock = pygame.time.Clock()

    # Initial Start and Goal positions
    start = get_random_start()
    goal = get_random_goal()

    # Create NPC with correct start position
    npc = NPC(start=start, goal=goal)

    running = True
    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw maze
        for y in range(len(maze)):  # Loop through rows
            for x in range(len(maze[y])):  # Loop through columns in each row
                color = BLACK if maze[y][x] == 1 else WHITE
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # Draw goal
        pygame.draw.rect(screen, GREEN, (npc.goal[0] * CELL_SIZE, npc.goal[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Update and draw NPC
        npc.update()
        npc.draw(screen)

        # Display update
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
