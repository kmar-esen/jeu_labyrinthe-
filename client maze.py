import pygame
import socket
import pickle
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Client")

WHITE = (255, 255, 255)
BLACK = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5555))

data = pickle.loads(client.recv(2048))
player_id = data["id"]
MAZE = [...]  # Paste same MAZE here
goal = data["goal"]

player1_img = pygame.transform.scale(pygame.image.load("player1.png"), (CELL_SIZE, CELL_SIZE))
player2_img = pygame.transform.scale(pygame.image.load("player2.png"), (CELL_SIZE, CELL_SIZE))

def draw_maze():
    for y, row in enumerate(MAZE):
        for x, val in enumerate(row):
            if val == 1:
                pygame.draw.rect(screen, BLACK, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def send_move(direction):
    client.send(pickle.dumps(direction))

def game_loop():
    while True:
        screen.fill(WHITE)
        draw_maze()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: send_move("UP")
                if event.key == pygame.K_DOWN: send_move("DOWN")
                if event.key == pygame.K_LEFT: send_move("LEFT")
                if event.key == pygame.K_RIGHT: send_move("RIGHT")

        data = pickle.loads(client.recv(2048))
        players = data["players"]
        enemies = data["enemies"]

        screen.blit(player1_img, (players[1][0]*CELL_SIZE, players[1][1]*CELL_SIZE))
        screen.blit(player2_img, (players[2][0]*CELL_SIZE, players[2][1]*CELL_SIZE))
        pygame.draw.rect(screen, GREEN, (goal[0]*CELL_SIZE, goal[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for e in enemies:
            pygame.draw.rect(screen, RED, (e[0]*CELL_SIZE, e[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()
        pygame.time.delay(100)

game_loop()
