import pygame
import random
import time
import tkinter as tk
from tkinter import messagebox

# Constants
WIDTH, HEIGHT = 600, 650  # Space for UI
ROWS, COLS = 21, 21  # Maze size
CELL_SIZE = WIDTH // COLS
TOP_MARGIN = 60  # Space for UI elements
SCORE_FILE = "scores.txt"

# Colors
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)
GREEN = (34, 177, 76)
RED = (237, 28, 36)
BLUE = (0, 162, 232)
BG_GRADIENT = [(200, 200, 255), (150, 150, 255)]  # Gradient effect

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30, bold=True)
title_font = pygame.font.SysFont("Arial", 50, bold=True)

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def generate_maze(rows, cols):
    """ Generates a complex maze using Prim's Algorithm. """
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

def bfs_shortest_path(maze, start, end):
    """ Finds the shortest path in the maze using BFS. """
    queue = [(start, 0)]
    visited = set([start])
    while queue:
        (x, y), steps = queue.pop(0)
        if (x, y) == end:
            return steps
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < ROWS and 0 <= ny < COLS and maze[nx][ny] == 1 and (nx, ny) not in visited:
                queue.append(((nx, ny), steps + 1))
                visited.add((nx, ny))
    return float('inf')

def save_score(time_taken, moves, optimal_moves):
    """ Saves the score to a file. """
    with open(SCORE_FILE, "a") as file:
        file.write(f"{time_taken:.2f},{moves},{optimal_moves}\n")

def get_top_scores():
    """ Reads scores from file and returns top 5 performances. """
    scores = []
    try:
        with open(SCORE_FILE, "r") as file:
            for line in file:
                time_taken, moves, optimal_moves = map(float, line.strip().split(','))
                scores.append((moves, time_taken))
        scores.sort()
        return scores[:5]
    except FileNotFoundError:
        return []

def show_popup(time_taken, moves, optimal_moves):
    """ Displays a message box with performance stats. """
    save_score(time_taken, moves, optimal_moves)
    top_scores = get_top_scores()
    score_msg = "\n".join([f"{i+1}. Moves: {m}, Time: {t:.2f}s" for i, (m, t) in enumerate(top_scores)])
    messagebox.showinfo("Game Over", f"You won!\nTime Taken: {time_taken:.2f}s\nMoves: {moves}\nOptimal Moves: {optimal_moves}\n\nTop Scores:\n{score_msg}")

# Start Screen
def start_screen():
    screen.fill(BG_GRADIENT[0])
    title_text = title_font.render("Maze Game", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 200))
    button_rect = pygame.Rect(WIDTH // 2 - 75, 300, 150, 50)
    pygame.draw.rect(screen, GREEN, button_rect, border_radius=8)
    start_text = font.render("START", True, WHITE)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 310))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                return

start_screen()
maze = generate_maze(ROWS, COLS)
treasure = (ROWS - 2, COLS - 2)
player = (1, 1)
start_time = time.time()
moves = 0
optimal_moves = bfs_shortest_path(maze, (1, 1), treasure)

def draw_maze():
    screen.fill(BG_GRADIENT[0])
    elapsed_time = time.time() - start_time
    screen.blit(font.render(f"Time: {elapsed_time:.2f}s", True, BLACK), (20, 15))
    screen.blit(font.render(f"Moves: {moves}", True, BLACK), (WIDTH - 140, 15))
    for x in range(ROWS):
        for y in range(COLS):
            rect = (y * CELL_SIZE, x * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK if maze[x][y] == 0 else WHITE, rect, border_radius=6)
    pygame.draw.rect(screen, GREEN, (treasure[1] * CELL_SIZE, treasure[0] * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE), border_radius=8)
    pygame.draw.rect(screen, RED, (player[1] * CELL_SIZE, player[0] * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE), border_radius=10)

running = True
while running:
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            dx, dy = {pygame.K_UP: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_RIGHT: (0, 1)}.get(event.key, (0, 0))
            if maze[player[0] + dx][player[1] + dy] == 1:
                player = (player[0] + dx, player[1] + dy)
                moves += 1
    if player == treasure:
        show_popup(time.time() - start_time, moves, optimal_moves)
        running = False
    draw_maze()
    pygame.display.flip()
pygame.quit()
