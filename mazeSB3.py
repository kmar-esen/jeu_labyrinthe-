import pygame
import sys
import random
import gym
import numpy as np
from stable_baselines3 import PPO  # or DQN, A2C, etc.

# --- Pygame Init ---
pygame.init()
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
PLAYER_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game AI")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Level Layout ---
LEVELS = [
    [   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
]
MAZE = LEVELS[0]

# --- Assets ---
player1_jpg = pygame.transform.scale(pygame.image.load('player1.png'), (PLAYER_SIZE, PLAYER_SIZE))
player2_jpg = pygame.transform.scale(pygame.image.load('player2.png'), (PLAYER_SIZE, PLAYER_SIZE))

# --- Positions ---
player1_x = player1_y = 1
player2_x = player2_y = 1
goal_x, goal_y = 18, 9
enemies = [(5, 5), (10, 5), (15, 5)]

# --- SB3 ENV ---
class MazeEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = gym.spaces.Box(low=0, high=max(WIDTH, HEIGHT), shape=(4,), dtype=np.int32)
        self.action_space = gym.spaces.Discrete(4)  # up, down, left, right
        self.reset()

    def reset(self):
        self.player2_pos = [1, 1]
        return np.array(self.player2_pos + [goal_x, goal_y], dtype=np.int32)

    def step(self, action):
        x, y = self.player2_pos
        if action == 0 and MAZE[y - 1][x] == 0: y -= 1
        if action == 1 and MAZE[y + 1][x] == 0: y += 1
        if action == 2 and MAZE[y][x - 1] == 0: x -= 1
        if action == 3 and MAZE[y][x + 1] == 0: x += 1
        self.player2_pos = [x, y]
        done = (x, y) == (goal_x, goal_y)
        reward = 1 if done else -0.01
        return np.array(self.player2_pos + [goal_x, goal_y], dtype=np.int32), reward, done, {}

    def render(self, mode='human'):
        pass

env = MazeEnv()
model = PPO.load("ppo_maze.zip")  # Make sure this model is trained and saved

# --- Game Logic ---
def draw_maze():
    for row in range(len(MAZE)):
        for col in range(len(MAZE[row])):
            if MAZE[row][col] == 1:
                pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def show_popup(message):
    font = pygame.font.Font(None, 74)
    text = font.render(message, True, BLACK)
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.update()
    pygame.time.delay(2000)

def reset_level():
    global player1_x, player1_y, player2_x, player2_y
    player1_x = player1_y = 1
    player2_x = player2_y = 1

def move_enemy(enemy_pos):
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    random.shuffle(dirs)
    for dx, dy in dirs:
        nx, ny = enemy_pos[0] + dx, enemy_pos[1] + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and MAZE[ny][nx] == 0:
            return (nx, ny)
    return enemy_pos

# --- Main Game Loop ---
def game_loop():
    global player1_x, player1_y, player2_x, player2_y
    obs = env.reset()
    while True:
        screen.fill(WHITE)
        draw_maze()
        screen.blit(player1_jpg, (player1_x * CELL_SIZE, player1_y * CELL_SIZE))
        screen.blit(player2_jpg, (player2_x * CELL_SIZE, player2_y * CELL_SIZE))
        pygame.draw.rect(screen, GREEN, (goal_x * CELL_SIZE, goal_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Move enemies
        for i in range(len(enemies)):
            enemies[i] = move_enemy(enemies[i])
            pygame.draw.rect(screen, RED, (enemies[i][0]*CELL_SIZE, enemies[i][1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # AI decision
        action, _ = model.predict(obs)
        obs, _, done, _ = env.step(action)
        player2_x, player2_y = env.player2_pos

        # Collision detection
        if (player1_x, player1_y) == (goal_x, goal_y):
            show_popup("Player 1 Wins!")
            reset_level()
            obs = env.reset()
        if (player2_x, player2_y) == (goal_x, goal_y):
            show_popup("Player 2 Wins!")
            reset_level()
            obs = env.reset()

        pygame.display.flip()

        # Player 1 input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                nx, ny = player1_x, player1_y
                if event.key == pygame.K_UP: ny -= 1
                elif event.key == pygame.K_DOWN: ny += 1
                elif event.key == pygame.K_LEFT: nx -= 1
                elif event.key == pygame.K_RIGHT: nx += 1
                if MAZE[ny][nx] == 0:
                    player1_x, player1_y = nx, ny

        pygame.time.delay(100)

# --- Start Game ---
game_loop()
