import pygame
import sys
import threading
import time
from collections import deque

# Konstanta
GRID_SIZE = 5
TILE_SIZE = 100
SCREEN_SIZE = GRID_SIZE * TILE_SIZE
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# Inisialisasi
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 80))
pygame.display.set_caption("Sokoban 5x5 - Player vs AI (BFS)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Status game
game_over = False
winner = None

# Posisi awal
player_pos = [0, 0]
ai_pos = [4, 4]
box_pos = [2, 2]
target_pos = [3, 3]

# Fungsi validasi gerakan
def valid_move(pos):
    return 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE

# BFS untuk AI
def bfs(start, goal, avoid=[]):
    queue = deque()
    queue.append((start, []))
    visited = set()
    visited.add(tuple(start))

    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_pos = [current[0] + dx, current[1] + dy]
            if valid_move(new_pos) and tuple(new_pos) not in visited and new_pos not in avoid:
                queue.append((new_pos, path + [(dx, dy)]))
                visited.add(tuple(new_pos))
    return []

# Thread AI
def ai_thread():
    global ai_pos, box_pos, game_over, winner
    while not game_over:
        time.sleep(0.5)
        if game_over:
            break

        # Jika box bisa didorong ke arah target
        dx = target_pos[0] - box_pos[0]
        dy = target_pos[1] - box_pos[1]
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))

        behind_box = [box_pos[0] - dx, box_pos[1] - dy]
        if valid_move(behind_box) and behind_box != player_pos:
            path = bfs(ai_pos, behind_box, avoid=[player_pos, box_pos])
            if path:
                step = path[0]
                ai_pos[0] += step[0]
                ai_pos[1] += step[1]
                if ai_pos == behind_box:
                    new_box_pos = [box_pos[0] + dx, box_pos[1] + dy]
                    if valid_move(new_box_pos) and new_box_pos != player_pos:
                        box_pos = new_box_pos
                        ai_pos = [box_pos[0] - dx, box_pos[1] - dy]

        if box_pos == target_pos:
            game_over = True
            winner = "AI"

# Gerakan pemain
def move_player(dx, dy):
    global player_pos, box_pos, game_over, winner
    if game_over:
        return

    new_pos = [player_pos[0] + dx, player_pos[1] + dy]
    if valid_move(new_pos):
        if new_pos == box_pos:
            box_new = [box_pos[0] + dx, box_pos[1] + dy]
            if valid_move(box_new) and box_new != ai_pos:
                box_pos = box_new
                player_pos = new_pos
        elif new_pos != ai_pos:
            player_pos = new_pos

    if box_pos == target_pos:
        game_over = True
        winner = "Player"

# Gambar elemen
def draw():
    screen.fill(WHITE)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pygame.draw.rect(screen, GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    pygame.draw.rect(screen, GREEN, (target_pos[0]*TILE_SIZE, target_pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (box_pos[0]*TILE_SIZE+10, box_pos[1]*TILE_SIZE+10, TILE_SIZE-20, TILE_SIZE-20))
    pygame.draw.circle(screen, BLUE, (player_pos[0]*TILE_SIZE+TILE_SIZE//2, player_pos[1]*TILE_SIZE+TILE_SIZE//2), 30)
    pygame.draw.circle(screen, ORANGE, (ai_pos[0]*TILE_SIZE+TILE_SIZE//2, ai_pos[1]*TILE_SIZE+TILE_SIZE//2), 30)

    if game_over:
        msg = font.render(f"{winner} wins!", True, (0, 0, 0))
        screen.blit(msg, (SCREEN_SIZE // 2 - msg.get_width() // 2, SCREEN_SIZE + 10))

    pygame.draw.rect(screen, (100, 200, 100), (SCREEN_SIZE // 2 - 60, SCREEN_SIZE + 40, 120, 40))
    text = font.render("Restart", True, (255, 255, 255))
    screen.blit(text, (SCREEN_SIZE // 2 - 45, SCREEN_SIZE + 45))

    pygame.display.flip()

# Reset game
def reset_game():
    global player_pos, ai_pos, box_pos, target_pos, game_over, winner
    player_pos = [0, 0]
    ai_pos = [4, 4]
    box_pos = [2, 2]
    target_pos = [3, 3]
    game_over = False
    winner = None
    threading.Thread(target=ai_thread, daemon=True).start()

# Jalankan AI pertama kali
threading.Thread(target=ai_thread, daemon=True).start()

# Loop utama
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_LEFT:
                move_player(-1, 0)
            elif event.key == pygame.K_RIGHT:
                move_player(1, 0)
            elif event.key == pygame.K_UP:
                move_player(0, -1)
            elif event.key == pygame.K_DOWN:
                move_player(0, 1)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if SCREEN_SIZE // 2 - 60 <= x <= SCREEN_SIZE // 2 + 60 and SCREEN_SIZE + 40 <= y <= SCREEN_SIZE + 80:
                reset_game()

    draw()
    clock.tick(60)