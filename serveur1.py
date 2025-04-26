import socket
import threading
import pickle
import time
import random

HOST = 'localhost'
PORT = 5555

MAZE = [...]  # Paste your MAZE here
goal = (18, 9)
enemies = [(5, 5), (10, 5), (15, 5)]
players = {1: [1, 1], 2: [1, 1]}

def move_enemy(enemy_pos):
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    random.shuffle(dirs)
    for dx, dy in dirs:
        nx, ny = enemy_pos[0] + dx, enemy_pos[1] + dy
        if MAZE[ny][nx] == 0:
            return [nx, ny]
    return enemy_pos

def handle_client(conn, player_id):
    global players
    conn.send(pickle.dumps({"id": player_id, "state": players, "goal": goal, "enemies": enemies}))
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            direction = pickle.loads(data)

            x, y = players[player_id]
            if direction == "UP" and MAZE[y - 1][x] == 0: y -= 1
            if direction == "DOWN" and MAZE[y + 1][x] == 0: y += 1
            if direction == "LEFT" and MAZE[y][x - 1] == 0: x -= 1
            if direction == "RIGHT" and MAZE[y][x + 1] == 0: x += 1
            players[player_id] = [x, y]
        except:
            break
        conn.sendall(pickle.dumps({"players": players, "goal": goal, "enemies": enemies}))
    conn.close()

def update_enemies():
    global enemies
    while True:
        enemies[:] = [move_enemy(e) for e in enemies]
        time.sleep(1)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

print("Server started, waiting for clients...")

threading.Thread(target=update_enemies, daemon=True).start()

player_id = 1
while player_id <= 2:
    conn, addr = server.accept()
    print(f"Player {player_id} connected.")
    threading.Thread(target=handle_client, args=(conn, player_id), daemon=True).start()
    player_id += 1
