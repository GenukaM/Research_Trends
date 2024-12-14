import pygame
import heapq  # For priority queue to maintain open list based on f(x)
import random

# Define constants
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 30
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Define NPC state
class NPCState:
    MOVING = 1
    GOAL_REACHED = 2
    BACKTRACKING = 3

# Create a simple maze as a 2D grid
maze = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
# Add some walls (represented by 1)
for _ in range(100):
    maze[random.randint(0, GRID_HEIGHT-1)][random.randint(0, GRID_WIDTH-1)] = 1
maze[0][0] = maze[GRID_HEIGHT-1][GRID_WIDTH-1] = 0  # Start and Goal are open

class NPC:
    def __init__(self, start, goal):
        self.position = start
        self.previous_position = None  # Track the previous position
        self.goal = goal
        self.path = [start]  # Incremental path construction starts with the start position
        self.visited = []  # Track visited cells for backtracking
        self.fsm = NPCState.MOVING
        self.cell_costs = {}  # Store adaptive costs for each cell based on past experience

        # A* specific
        self.open_list = []  # Priority queue for A* open list
        self.closed_list = set()  # Set for A* closed list

    def heuristic(self, a, b):
        """Manhattan distance as heuristic, adjusted with dynamic cell costs."""
        base_heuristic = abs(a[0] - b[0]) + abs(a[1] - b[1])
        adjusted_cost = self.cell_costs.get(a, 0)  # Get adjusted cost for the current position
        return base_heuristic + adjusted_cost

    def get_neighbors(self, pos):
        """Get valid neighboring positions considering the maze"""
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and maze[ny][nx] == 0:
                neighbors.append((nx, ny))
        return neighbors

    def update(self):
        """Incrementally calculate the next step with A*."""
        if self.fsm != NPCState.MOVING:
            return

        current = self.position
        self.visited.append(current)

        # If we've reached the goal, stop
        if current == self.goal:
            self.fsm = NPCState.GOAL_REACHED
            return

        # Initialize open list if it's the first time moving
        if not self.open_list:
            heapq.heappush(self.open_list, (0, current))  # Push the start node with f(x) = 0

        # Perform A* search
        if self.open_list:
            # Pop node with lowest f(x) from open list
            _, current = heapq.heappop(self.open_list)
            self.closed_list.add(current)

            # Get neighbors and evaluate their costs
            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor in self.closed_list:
                    continue  # Skip already visited nodes

                # Calculate cost and heuristic
                g_cost = self.cell_costs.get(neighbor, 0)  # Cost of moving to this neighbor
                h_cost = self.heuristic(neighbor, self.goal)  # Heuristic to goal
                f_cost = g_cost + h_cost

                # Update the path if a better f(x) is found
                heapq.heappush(self.open_list, (f_cost, neighbor))
                self.path.append(neighbor)
                self.position = neighbor

                # Update dynamic cost of the new position
                self.cell_costs[neighbor] = self.cell_costs.get(neighbor, 0) + 1  # Penalize based on past visits

        # Handle backtracking
        if not self.open_list:
            self.backtrack()

    def backtrack(self):
        """Remove the last step and move to the previous position."""
        if len(self.path) > 1:
            self.path.pop()
            self.position = self.path[-1]
        else:
            print("No path to backtrack. Stuck!")

    def draw(self, screen):
        """Draw the NPC (red rectangle) on the screen."""
        x, y = self.position
        pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_maze(screen):
    """Draw the maze on the screen."""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WHITE if maze[y][x] == 0 else BLUE
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("NPC A* Pathfinding")
    clock = pygame.time.Clock()

    start = (0, 0)  # Start position
    goal = (GRID_WIDTH - 1, GRID_HEIGHT - 1)  # Goal position

    npc = NPC(start, goal)

    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill screen with black
        draw_maze(screen)  # Draw the maze
        npc.update()  # Update NPC's position and path
        npc.draw(screen)  # Draw NPC

        pygame.display.flip()
        clock.tick(10)  # Run at 10 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()
