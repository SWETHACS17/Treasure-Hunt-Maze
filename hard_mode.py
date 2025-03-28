import pygame
import random
import time
import heapq

# Constants
WIDTH, HEIGHT = 600, 650  # Space for UI
ROWS, COLS = 21, 21  # Maze size
CELL_SIZE = WIDTH // COLS
TOP_MARGIN = 60  # Space for UI elements

# Colors
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game - Escape the Enemy!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30, bold=True)

# Load images with slightly larger scaling (1.2x original size)
girl_img = pygame.transform.scale(pygame.image.load("girl-1.png"), (int(CELL_SIZE * 1.2), int(CELL_SIZE * 1.2)))
treasure_img = pygame.transform.scale(pygame.image.load("treasure.png"), (int(CELL_SIZE * 1.2), int(CELL_SIZE * 1.2)))
enemy_img = pygame.transform.scale(pygame.image.load("enemy.png"), (int(CELL_SIZE * 1.2), int(CELL_SIZE * 1.2)))

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Enemy movement difficulty
ENEMY_SPEED = 5  # Lower value = slower enemy
PATROL_AREA = [(3, 3), (3, COLS - 4), (ROWS - 4, COLS - 4), (ROWS - 4, 3)]
RANDOM_MOVE_CHANCE = 0.2

def generate_maze(rows, cols):
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    start_x, start_y = 1, 1
    grid[start_x][start_y] = 1
    walls = [(start_x + dx, start_y + dy) for dx, dy in DIRECTIONS if 0 <= start_x + dx < rows and 0 <= start_y + dy < cols]
    random.shuffle(walls)

    while walls:
        wx, wy = walls.pop()
        if grid[wx][wy] == 0:
            neighbors = [(wx + dx, wy + dy) for dx, dy in DIRECTIONS if 0 <= wx + dx < rows and 0 <= wy + dy < cols and grid[wx + dx][wy + dy] == 1]
            if len(neighbors) == 1:
                grid[wx][wy] = 1
                for dx, dy in DIRECTIONS:
                    nx, ny = wx + dx, wy + dy
                    if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0:
                        walls.append((nx, ny))
        random.shuffle(walls)

    grid[rows - 2][cols - 2] = 1
    return grid

def a_star_search(maze, start, goal):
    heap = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while heap:
        _, current = heapq.heappop(heap)
        if current == goal:
            break
        
        for dx, dy in DIRECTIONS:
            next_pos = (current[0] + dx, current[1] + dy)
            if 0 <= next_pos[0] < ROWS and 0 <= next_pos[1] < COLS and maze[next_pos[0]][next_pos[1]] == 1:
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + abs(goal[0] - next_pos[0]) + abs(goal[1] - next_pos[1])
                    heapq.heappush(heap, (priority, next_pos))
                    came_from[next_pos] = current
    
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    return path[::-1]

def move_enemy():
    global enemy, enemy_moves
    if random.random() < RANDOM_MOVE_CHANCE:
        random.shuffle(DIRECTIONS)
        for dx, dy in DIRECTIONS:
            next_pos = (enemy[0] + dx, enemy[1] + dy)
            if 0 <= next_pos[0] < ROWS and 0 <= next_pos[1] < COLS and maze[next_pos[0]][next_pos[1]] == 1:
                enemy = next_pos
                return
    path = a_star_search(maze, enemy, player)
    if len(path) > 2:
        enemy = path[1]
    enemy_moves += 1

def show_popup(message):
    popup = pygame.Surface((400, 200))
    popup.fill(WHITE)
    pygame.draw.rect(popup, BLACK, popup.get_rect(), 5)
    text = font.render(message, True, BLACK)
    popup.blit(text, (50, 80))
    screen.blit(popup, (100, 200))
    pygame.display.flip()
    time.sleep(3)

def draw_maze():
    screen.fill(WHITE)
    for x in range(ROWS):
        for y in range(COLS):
            rect = (y * CELL_SIZE, x * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK if maze[x][y] == 0 else WHITE, rect, border_radius=6)
    
    # Draw treasure with adjusted positioning to center the larger image
    screen.blit(treasure_img, (treasure[1] * CELL_SIZE - int(CELL_SIZE * 0.1), treasure[0] * CELL_SIZE + TOP_MARGIN - int(CELL_SIZE * 0.1)))
    
    # Draw player (girl) with adjusted positioning to center the larger image
    screen.blit(girl_img, (player[1] * CELL_SIZE - int(CELL_SIZE * 0.1), player[0] * CELL_SIZE + TOP_MARGIN - int(CELL_SIZE * 0.1)))
    
    # Draw enemy with adjusted positioning to center the larger image
    screen.blit(enemy_img, (enemy[1] * CELL_SIZE - int(CELL_SIZE * 0.1), enemy[0] * CELL_SIZE + TOP_MARGIN - int(CELL_SIZE * 0.1)))
    
    move_text = font.render(f"Moves: {moves}  Time: {int(time.time() - start_time)}s", True, BLACK)
    screen.blit(move_text, (20, 15))

maze = generate_maze(ROWS, COLS)
treasure = (ROWS - 2, COLS - 2)
player = (1, 1)
enemy = random.choice(PATROL_AREA)
moves = 0
enemy_moves = 0
player_headstart = 7
start_time = time.time()

running = True
while running:
    clock.tick(ENEMY_SPEED)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            dx, dy = {pygame.K_UP: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_RIGHT: (0, 1)}.get(event.key, (0, 0))
            if maze[player[0] + dx][player[1] + dy] == 1:
                player = (player[0] + dx, player[1] + dy)
                moves += 1
    
    if moves > player_headstart and moves % 5 == 0:
        move_enemy()
    
    if player == treasure:
        show_popup(f"You Won! Time: {int(time.time() - start_time)}s")
        running = False
    elif player == enemy:
        running = False
    
    draw_maze()
    pygame.display.flip()

pygame.quit()