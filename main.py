import pygame
import random
import networkx as nx

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 15, 15
CELL_SIZE = WIDTH // COLS

# Colors
WHITE, BLACK, GREEN, RED = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Directions for movement
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up

def generate_maze(rows, cols):
    """ Generates a maze using Prim's Algorithm. """
    G = nx.grid_2d_graph(rows, cols)
    maze = set()
    walls = set(G.edges())
    
    start = (0, 0)
    visited = {start}
    
    edges = [(start, neighbor) for neighbor in G.neighbors(start)]
    
    while edges:
        edge = random.choice(edges)
        edges.remove(edge)

        if edge[1] not in visited:
            maze.add(edge)  # Keep the path
            visited.add(edge[1])
            edges.extend([(edge[1], n) for n in G.neighbors(edge[1]) if n not in visited])

    return maze

def bfs_path(maze, start, goal):
    """ Finds the shortest path using BFS. """
    queue = [(start, [start])]
    visited = set()
    
    while queue:
        (node, path) = queue.pop(0)
        
        if node == goal:
            return path
        
        for dx, dy in DIRECTIONS:
            neighbor = (node[0] + dx, node[1] + dy)
            if ((node, neighbor) in maze or (neighbor, node) in maze) and neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
                visited.add(neighbor)
    
    return []

# Initialize maze and entities
maze = generate_maze(ROWS, COLS)
treasure = (ROWS - 1, COLS - 1)
player = (0, 0)
path = bfs_path(maze, player, treasure)

def draw_maze():
    """ Draws the maze, player, and treasure. """
    screen.fill(WHITE)
    
    # Draw walls
    for x in range(COLS):
        for y in range(ROWS):
            if ((y, x), (y, x + 1)) not in maze and x < COLS - 1:
                pygame.draw.line(screen, BLACK, ((x + 1) * CELL_SIZE, y * CELL_SIZE),
                                 ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE), 3)
            if ((y, x), (y + 1, x)) not in maze and y < ROWS - 1:
                pygame.draw.line(screen, BLACK, (x * CELL_SIZE, (y + 1) * CELL_SIZE),
                                 ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE), 3)
    
    # Draw border walls
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 3)
    
    # Draw Treasure
    pygame.draw.rect(screen, GREEN, (treasure[1] * CELL_SIZE, treasure[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw Player
    pygame.draw.rect(screen, RED, (player[1] * CELL_SIZE, player[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Game Loop
running = True
while running:
    clock.tick(10)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP:
                dx, dy = -1, 0
            elif event.key == pygame.K_DOWN:
                dx, dy = 1, 0
            elif event.key == pygame.K_LEFT:
                dx, dy = 0, -1
            elif event.key == pygame.K_RIGHT:
                dx, dy = 0, 1
            
            new_pos = (player[0] + dx, player[1] + dy)
            
            if ((player, new_pos) in maze or (new_pos, player) in maze):
                player = new_pos

    draw_maze()
    pygame.display.flip()

pygame.quit()