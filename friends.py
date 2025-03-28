import pygame
import random
import time
import tkinter as tk
from tkinter import messagebox

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
BG_GRADIENT = [(200, 200, 255), (150, 150, 255)]

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25, bold=True)
large_font = pygame.font.SysFont("Arial", 36, bold=True)
countdown_font = pygame.font.SysFont("Arial", 200, bold=True)

# Directions for movement
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class AvatarSelector:
    def __init__(self):
        self.avatars = {
            'red': [
                pygame.image.load("girl-1.png"),
                pygame.image.load("girl-2.png"),
                pygame.image.load("boy-1.png"),
                pygame.image.load("boy-2.png")
            ],
            'blue': [
                pygame.image.load("girl-p2-1.png"),
                pygame.image.load("girl-p2-2.png"),
                pygame.image.load("boy-p2-1.png"),
                pygame.image.load("boy-p2-2.png")
            ]
        }
        self.selected_avatars = {
            'red': 0,
            'blue': 0
        }

    def draw_selection_screen(self):
        screen.fill(BLACK)
        
        # Title
        title = large_font.render("Select Your Avatars", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Red Player Avatar Selection
        red_label = font.render("Red Player", True, RED)
        screen.blit(red_label, (100, 150))
        
        current_red_avatar = self.avatars['red'][self.selected_avatars['red']]
        current_red_avatar = pygame.transform.scale(current_red_avatar, (100, 100))
        red_rect = current_red_avatar.get_rect(center=(150, 300))
        screen.blit(current_red_avatar, red_rect)
        
        # Blue Player Avatar Selection
        blue_label = font.render("Blue Player", True, BLUE)
        screen.blit(blue_label, (400, 150))
        
        current_blue_avatar = self.avatars['blue'][self.selected_avatars['blue']]
        current_blue_avatar = pygame.transform.scale(current_blue_avatar, (100, 100))
        blue_rect = current_blue_avatar.get_rect(center=(450, 300))
        screen.blit(current_blue_avatar, blue_rect)

        # Improved Navigation Instructions
        instructions = [
            ("A / D", "Change Red Avatar", RED),
            ("← / →", "Change Blue Avatar", BLUE),
            ("SPACE", "Start Game", WHITE)
        ]
        
        y_position = 450
        for key, text, color in instructions:
            key_text = font.render(key, True, color)
            desc_text = font.render(text, True, WHITE)

            key_x = WIDTH // 2 - key_text.get_width() - 10
            desc_x = WIDTH // 2 + 10

            screen.blit(key_text, (key_x, y_position))
            screen.blit(desc_text, (desc_x, y_position))
            y_position += 50

        pygame.display.flip()

    def countdown_screen(self):
        # Countdown sequence
        countdown_numbers = ['3', '2', '1', 'GO!']
        colors = [RED, BLUE, GREEN, WHITE]
        
        for i, number in enumerate(countdown_numbers):
            screen.fill(BLACK)
            
            # Render countdown number
            number_text = countdown_font.render(number, True, colors[i])
            number_rect = number_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(number_text, number_rect)
            
            pygame.display.flip()
            pygame.time.delay(1000)  # 1 second delay between numbers

    def handle_selection(self):
        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.KEYDOWN:
                    # Red player avatar selection
                    if event.key == pygame.K_a:
                        self.selected_avatars['red'] = (self.selected_avatars['red'] - 1) % len(self.avatars['red'])
                    elif event.key == pygame.K_d:
                        self.selected_avatars['red'] = (self.selected_avatars['red'] + 1) % len(self.avatars['red'])
                    
                    # Blue player avatar selection
                    if event.key == pygame.K_LEFT:
                        self.selected_avatars['blue'] = (self.selected_avatars['blue'] - 1) % len(self.avatars['blue'])
                    elif event.key == pygame.K_RIGHT:
                        self.selected_avatars['blue'] = (self.selected_avatars['blue'] + 1) % len(self.avatars['blue'])
                    
                    # Start game
                    if event.key == pygame.K_SPACE:
                        self.countdown_screen()
                        return True
            
            self.draw_selection_screen()
            clock.tick(10)

class MazeGame:
    def __init__(self, red_avatar, blue_avatar):
        self.red_avatar = red_avatar
        self.blue_avatar = blue_avatar
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Game")
        
        # Load images
        self.treasure_image = pygame.image.load("treasure.png")
        self.treasure_image = pygame.transform.scale(self.treasure_image, (CELL_SIZE, CELL_SIZE))
        
        # Load key and lock images
        self.key_image = pygame.image.load("key.png")
        self.key_image = pygame.transform.scale(self.key_image, (CELL_SIZE, CELL_SIZE))
        self.lock_image = pygame.image.load("lock.png")
        self.lock_image = pygame.transform.scale(self.lock_image, (CELL_SIZE, CELL_SIZE))
        
        self.maze = self.generate_maze(ROWS, COLS)
        self.treasure = (ROWS - 2, COLS - 2)
        self.player_red = (1, 1)
        self.player_blue = (1, COLS - 2)
        
        # Place keys and locks
        self.keys, self.locks = self.place_locks_and_keys()
        
        self.start_time = time.time()
        self.red_moves = 0
        self.blue_moves = 0
        self.red_keys = 0
        self.blue_keys = 0
        self.running = True

        self.game_loop()

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

    def place_locks_and_keys(self):
        empty_spaces = [(x, y) for x in range(ROWS) for y in range(COLS) if self.maze[x][y] == 1 and 
                        (x, y) not in [self.player_red, self.player_blue, self.treasure]]
        random.shuffle(empty_spaces)
        keys = empty_spaces[:2]
        locks = empty_spaces[2:4]
        return keys, locks

    def show_popup(self):
        root = tk.Tk()
        root.withdraw()
        end_time = time.time()
        
        # Determine the winner
        if self.player_red == self.treasure:
            winner = "Red Player"
        else:
            winner = "Blue Player"
        
        messagebox.showinfo("Game Over", 
            f"{winner} Won!\n\n"
            f"Red Moves: {self.red_moves}\n"
            f"Blue Moves: {self.blue_moves}\n"
            f"Time Taken: {end_time - self.start_time:.2f} seconds")
        root.destroy()

    def game_loop(self):
        while self.running:
            clock.tick(10)
            self.handle_events()
            self.draw_maze()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Red player movement (WASD)
                if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    dx, dy = 0, 0
                    if event.key == pygame.K_w:
                        dx, dy = -1, 0
                    elif event.key == pygame.K_s:
                        dx, dy = 1, 0
                    elif event.key == pygame.K_a:
                        dx, dy = 0, -1
                    elif event.key == pygame.K_d:
                        dx, dy = 0, 1
                    
                    new_x, new_y = self.player_red[0] + dx, self.player_red[1] + dy
                    
                    # Check for key collection
                    if (new_x, new_y) in self.keys:
                        self.keys.remove((new_x, new_y))
                        self.red_keys += 1
                    
                    # Check for lock interaction
                    if (new_x, new_y) in self.locks:
                        if self.red_keys > 0:
                            self.red_keys -= 1
                            self.locks.remove((new_x, new_y))
                        else:
                            continue
                    
                    # Normal movement
                    if 0 <= new_x < ROWS and 0 <= new_y < COLS and self.maze[new_x][new_y] == 1:
                        self.player_red = (new_x, new_y)
                        self.red_moves += 1

                # Blue player movement (Arrow keys)
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP:
                        dx, dy = -1, 0
                    elif event.key == pygame.K_DOWN:
                        dx, dy = 1, 0
                    elif event.key == pygame.K_LEFT:
                        dx, dy = 0, -1
                    elif event.key == pygame.K_RIGHT:
                        dx, dy = 0, 1
                    
                    new_x, new_y = self.player_blue[0] + dx, self.player_blue[1] + dy
                    
                    # Check for key collection
                    if (new_x, new_y) in self.keys:
                        self.keys.remove((new_x, new_y))
                        self.blue_keys += 1
                    
                    # Check for lock interaction
                    if (new_x, new_y) in self.locks:
                        if self.blue_keys > 0:
                            self.blue_keys -= 1
                            self.locks.remove((new_x, new_y))
                        else:
                            continue
                    
                    # Normal movement
                    if 0 <= new_x < ROWS and 0 <= new_y < COLS and self.maze[new_x][new_y] == 1:
                        self.player_blue = (new_x, new_y)
                        self.blue_moves += 1

                # Check for treasure collection
                if self.player_red == self.treasure or self.player_blue == self.treasure:
                    self.show_popup()
                    self.running = False

    def draw_maze(self):
        # Background gradient
        for i in range(HEIGHT):
            color = (
                BG_GRADIENT[0][0] + (BG_GRADIENT[1][0] - BG_GRADIENT[0][0]) * i // HEIGHT,
                BG_GRADIENT[0][1] + (BG_GRADIENT[1][1] - BG_GRADIENT[0][1]) * i // HEIGHT,
                BG_GRADIENT[0][2] + (BG_GRADIENT[1][2] - BG_GRADIENT[0][2]) * i // HEIGHT,
            )
            pygame.draw.line(self.screen, color, (0, i), (WIDTH, i))

        # Timer and moves
        elapsed_time = time.time() - self.start_time
        timer_text = font.render(f"Time: {elapsed_time:.2f}s", True, BLACK)
        red_moves_text = font.render(f"Red Moves: {self.red_moves}", True, BLACK)
        blue_moves_text = font.render(f"Blue Moves: {self.blue_moves}", True, BLACK)
        red_keys_text = font.render(f"Red Keys: {self.red_keys}", True, BLACK)
        blue_keys_text = font.render(f"Blue Keys: {self.blue_keys}", True, BLACK)
        
        self.screen.blit(timer_text, (20, 15))
        self.screen.blit(blue_moves_text, (WIDTH // 2 - 120, 15))
        self.screen.blit(blue_keys_text, (WIDTH // 2 - 120, 40))
        self.screen.blit(red_moves_text, (WIDTH - 180, 15))
        self.screen.blit(red_keys_text, (WIDTH - 180, 40))

        # Draw maze
        for x in range(ROWS):
            for y in range(COLS):
                rect = (y * CELL_SIZE, x * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
                if self.maze[x][y] == 0:
                    pygame.draw.rect(self.screen, BLACK, rect, border_radius=6)
                elif (x, y) == self.treasure:
                    # Draw larger treasure image
                    enlarged_treasure = pygame.transform.scale(self.treasure_image, (CELL_SIZE + 10, CELL_SIZE + 10))
                    self.screen.blit(enlarged_treasure, (y * CELL_SIZE - 5, x * CELL_SIZE + TOP_MARGIN - 5))

        # Draw keys
        for key in self.keys:
            self.screen.blit(self.key_image, (key[1] * CELL_SIZE, key[0] * CELL_SIZE + TOP_MARGIN))

        # Draw locks
        for lock in self.locks:
            self.screen.blit(self.lock_image, (lock[1] * CELL_SIZE, lock[0] * CELL_SIZE + TOP_MARGIN))

        # Draw players with larger avatars
        enlarged_red_avatar = pygame.transform.scale(self.red_avatar, (CELL_SIZE + 10, CELL_SIZE + 10))
        enlarged_blue_avatar = pygame.transform.scale(self.blue_avatar, (CELL_SIZE + 10, CELL_SIZE + 10))
        
        self.screen.blit(enlarged_red_avatar, (self.player_red[1] * CELL_SIZE - 5, self.player_red[0] * CELL_SIZE + TOP_MARGIN - 5))
        self.screen.blit(enlarged_blue_avatar, (self.player_blue[1] * CELL_SIZE - 5, self.player_blue[0] * CELL_SIZE + TOP_MARGIN - 5))

def main():
    # Avatar Selection
    avatar_selector = AvatarSelector()
    if not avatar_selector.handle_selection():
        pygame.quit()
        return

    # Get selected avatars
    red_avatar = avatar_selector.avatars['red'][avatar_selector.selected_avatars['red']]
    blue_avatar = avatar_selector.avatars['blue'][avatar_selector.selected_avatars['blue']]

    # Start the game with selected avatars
    MazeGame(red_avatar, blue_avatar)

if __name__ == "__main__":
    main()
