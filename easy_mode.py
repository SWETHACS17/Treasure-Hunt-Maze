import pygame
import random
import time
import tkinter as tk
from tkinter import messagebox
from collections import deque
import heapq

# Constants
WIDTH, HEIGHT = 600, 650
ROWS, COLS = 21, 21
CELL_SIZE = WIDTH // COLS
TOP_MARGIN = 60

# Colors
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)
GREEN = (34, 177, 76)
RED = (237, 28, 36)
BLUE = (0, 162, 232)
PURPLE = (128, 0, 128)  # Enemy color

# Directions
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class MazeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 25, bold=True)
        
        # Load and scale treasure chest image with alpha transparency
        self.treasure_image = pygame.image.load('treasure.png').convert_alpha()
        self.treasure_image = pygame.transform.scale(self.treasure_image, (int(CELL_SIZE * 1.5), int(CELL_SIZE * 1.5)))

        # Load and scale player image with alpha transparency
        self.player_image = pygame.image.load('girl-1.png').convert_alpha()
        self.player_image = pygame.transform.scale(self.player_image, (int(CELL_SIZE * 1.5), int(CELL_SIZE * 1.5)))

        # Load and scale enemy image with alpha transparency
        self.enemy_image = pygame.image.load('enemy.png').convert_alpha()
        self.enemy_image = pygame.transform.scale(self.enemy_image, (int(CELL_SIZE * 1.5), int(CELL_SIZE * 1.5)))

        self.start_screen()
        self.maze = self.generate_maze(ROWS, COLS)
        self.treasure = (ROWS - 2, COLS - 2)
        self.player = (1, 1)
        self.enemy = (ROWS - 4, COLS - 4)  # Moved enemy to a different location
        self.start_time = time.time()
        self.moves = 0
        self.running = True
        self.last_enemy_move = time.time()

        self.game_loop()

    def start_screen(self):
        for count in range(3, 0, -1):
            self.screen.fill(BLACK)
            text = self.font.render(str(count), True, WHITE)
            self.screen.blit(text, (WIDTH // 2 - 20, HEIGHT // 2 - 20))
            pygame.display.flip()
            time.sleep(1)
        
        self.screen.fill(BLACK)
        text = self.font.render("Press any key to Start", True, WHITE)
        self.screen.blit(text, (WIDTH // 2 - 120, HEIGHT // 2 - 20))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def generate_maze(self, rows, cols):
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

    def game_loop(self):
        while self.running:
            self.clock.tick(10)
            self.handle_events()
            self.move_enemy()
            self.draw_maze()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.move_player(-1, 0)
                elif event.key == pygame.K_DOWN:
                    self.move_player(1, 0)
                elif event.key == pygame.K_LEFT:
                    self.move_player(0, -1)
                elif event.key == pygame.K_RIGHT:
                    self.move_player(0, 1)

    def move_player(self, dx, dy):
        new_x, new_y = self.player[0] + dx, self.player[1] + dy
        if 0 <= new_x < ROWS and 0 <= new_y < COLS and self.maze[new_x][new_y] == 1:
            self.player = (new_x, new_y)
            self.moves += 1
            if self.player == self.treasure:
                self.show_popup("You Won!", "Time Taken: {:.2f} seconds\nMoves: {}".format(time.time() - self.start_time, self.moves))
                self.running = False
            elif self.player == self.enemy:
                self.show_popup("You Lost!", "The enemy caught you!")
                self.running = False

    def dijkstra_find_path(self, start, goal):
        """
        Find the shortest path using Dijkstra's algorithm
        
        Args:
        start (tuple): Starting coordinates (x, y)
        goal (tuple): Target coordinates (x, y)
        
        Returns:
        list: Shortest path from start to goal
        """
        
        pq = [(0, start, [])]
        
        visited = {}
        
        while pq:
            current_distance, current_node, path = heapq.heappop(pq)
            
            if current_node == goal:
                return path + [current_node]
            
            if current_node in visited and visited[current_node] <= current_distance:
                continue
            
            visited[current_node] = current_distance
            
            for dx, dy in DIRECTIONS:
                nx, ny = current_node[0] + dx, current_node[1] + dy
                
                if (0 <= nx < ROWS and 0 <= ny < COLS and 
                    self.maze[nx][ny] == 1 and (nx, ny) not in visited):
                    
                    new_distance = current_distance + 1
                    
                    heapq.heappush(pq, (new_distance, (nx, ny), path + [current_node]))
        
        return []

    def find_path(self, start, goal):
        """
        Fallback BFS path finding method
        """
        queue = deque([(start, [])])
        visited = set()
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                return path + [(x, y)]
            visited.add((x, y))
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < ROWS and 0 <= ny < COLS and self.maze[nx][ny] == 1 and (nx, ny) not in visited:
                    queue.append(((nx, ny), path + [(x, y)]))
        return []

    def move_enemy(self):
        """
        Modified enemy movement using Dijkstra's algorithm
        """
        if time.time() - self.last_enemy_move >= 3:
            self.last_enemy_move = time.time()
            
            path = self.dijkstra_find_path(self.enemy, self.player)
            
            if not path:
                path = self.find_path(self.enemy, self.player)
            
            if path and len(path) > 1:
                self.enemy = path[1]
                
                if self.enemy == self.player:
                    self.show_popup("You Lost!", "The enemy caught you!")
                    self.running = False

    def show_popup(self, title, message):
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
        root.destroy()

    def draw_maze(self):
        self.screen.fill(WHITE)
        
     
        elapsed_time = time.time() - self.start_time
        timer_text = self.font.render(f"Time: {elapsed_time:.2f}s", True, BLACK)
        moves_text = self.font.render(f"Moves: {self.moves}", True, BLACK)
        
       
        self.screen.blit(timer_text, (10, 10))
        self.screen.blit(moves_text, (WIDTH - 150, 10))
        
        # Draw maze
        for x in range(ROWS):
            for y in range(COLS):
                rect = (y * CELL_SIZE, x * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
                # Change the drawing of maze blocks to use rounded rectangles
                pygame.draw.rect(self.screen, BLACK if self.maze[x][y] == 0 else WHITE, rect, border_radius=6)
        
       
        treasure_rect = self.treasure_image.get_rect()
        treasure_rect.center = (self.treasure[1] * CELL_SIZE + CELL_SIZE // 2, 
                                self.treasure[0] * CELL_SIZE + TOP_MARGIN + CELL_SIZE // 2)
        self.screen.blit(self.treasure_image, treasure_rect)
        
      
        enemy_rect = self.enemy_image.get_rect()
        enemy_rect.center = (self.enemy[1] * CELL_SIZE + CELL_SIZE // 2, 
                             self.enemy[0] * CELL_SIZE + TOP_MARGIN + CELL_SIZE // 2)
        self.screen.blit(self.enemy_image, enemy_rect)
        
       
        player_rect = self.player_image.get_rect()
        player_rect.center = (self.player[1] * CELL_SIZE + CELL_SIZE // 2, 
                              self.player[0] * CELL_SIZE + TOP_MARGIN + CELL_SIZE // 2)
        self.screen.blit(self.player_image, player_rect)

if __name__ == "__main__":
    MazeGame()