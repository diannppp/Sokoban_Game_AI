import pygame
import sys
import threading
import time
from collections import deque

# Konstanta
GRID_SIZE = 5  # Ukuran grid 5x5
TILE_SIZE = 100  # Ukuran masing-masing tile dalam pixel
SCREEN_SIZE = GRID_SIZE * TILE_SIZE  # Ukuran layar permainan
WHITE = (255, 255, 255)  # Warna latar belakang
GRAY = (200, 200, 200)  # Warna garis grid
BLUE = (0, 0, 255)  # Warna pemain (player)
GREEN = (0, 255, 0)  # Warna target
RED = (255, 0, 0)  # Warna kotak (box)
ORANGE = (255, 165, 0)  # Warna AI

# Inisialisasi pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 80))  # Tambahan 80px untuk tombol Restart
pygame.display.set_caption("Sokoban 5x5 - Player vs AI (BFS Improved)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Status game
game_over = False
winner = None

# Posisi awal pemain, AI, kotak, dan target
player_pos = [0, 0]
ai_pos = [4, 4]
box_pos = [2, 2]
target_pos = [3, 3]

# Cek apakah posisi valid dalam grid
def valid_move(pos):
    return 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE

# BFS untuk mencari jalur dari start ke goal sambil menghindari posisi tertentu (seperti kotak atau pemain)
def bfs(start, goal, avoid=[]):
    queue = deque()
    queue.append((start, []))  # Menyimpan posisi sekarang dan jalur yang diambil
    visited = set()
    visited.add(tuple(start))

    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path  # Kembalikan jalur jika goal ditemukan

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Cek semua arah: atas, bawah, kiri, kanan
            new_pos = [current[0] + dx, current[1] + dy]
            if valid_move(new_pos) and tuple(new_pos) not in visited and new_pos not in avoid:
                queue.append((new_pos, path + [(dx, dy)]))
                visited.add(tuple(new_pos))
    return []  # Kembalikan list kosong jika tidak ada jalur

# Fungsi untuk mencari semua kemungkinan posisi AI yang bisa mendorong kotak
def get_push_positions(box_pos):
    """
    Cari semua posisi yang memungkinkan AI berdiri di belakang kotak
    dan mendorongnya ke arah yang valid (tidak keluar dari grid).
    """
    positions = []
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        pos_behind = [box_pos[0] - dx, box_pos[1] - dy]  # Posisi AI sebelum dorong
        pos_push_to = [box_pos[0] + dx, box_pos[1] + dy]  # Posisi baru kotak setelah dorong
        if valid_move(pos_behind) and valid_move(pos_push_to):
            positions.append((pos_behind, pos_push_to))
    return positions

# Hitung jarak Manhattan sebagai heuristik (untuk menilai seberapa dekat ke target)
def manhattan_dist(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# Thread AI: dijalankan secara paralel agar AI bisa bergerak otomatis
def ai_thread():
    global ai_pos, box_pos, game_over, winner
    while not game_over:
        time.sleep(0.5)  # Tunggu sejenak setiap langkah

        if game_over:
            break

        push_positions = get_push_positions(box_pos)  # Cari semua arah dorong yang mungkin
        best_move = None
        best_dist = float('inf')  # Awalnya sangat besar

        for pos_behind, pos_push_to in push_positions:
            # Cek tabrakan dengan pemain atau posisi tidak valid
            if pos_push_to == player_pos or pos_push_to == box_pos:
                continue
            if pos_behind == player_pos:
                continue

            # Cari jalur ke posisi di belakang kotak untuk mendorong
            path = bfs(ai_pos, pos_behind, avoid=[player_pos, box_pos])
            if path:
                dist = manhattan_dist(pos_push_to, target_pos)
                if dist < best_dist:
                    best_dist = dist
                    best_move = (path, pos_behind, pos_push_to)

        if best_move:
            path, pos_behind, pos_push_to = best_move
            step = path[0]
            ai_pos[0] += step[0]
            ai_pos[1] += step[1]

            # Jika AI sudah berada di belakang kotak
            if ai_pos == pos_behind:
                if pos_push_to != player_pos and valid_move(pos_push_to):
                    box_pos = pos_push_to  # Pindahkan kotak
                    ai_pos = pos_behind  # Tetap di belakang kotak

        # Cek apakah AI menang
        if box_pos == target_pos:
            game_over = True
            winner = "AI"

# Fungsi untuk menggerakkan pemain berdasarkan arah input keyboard
def move_player(dx, dy):
    global player_pos, box_pos, game_over, winner
    if game_over:
        return

    new_pos = [player_pos[0] + dx, player_pos[1] + dy]

    if valid_move(new_pos):
        if new_pos == box_pos:
            # Coba dorong kotak
            box_new = [box_pos[0] + dx, box_pos[1] + dy]
            if valid_move(box_new) and box_new != ai_pos:
                box_pos = box_new
                player_pos = new_pos
        elif new_pos != ai_pos:
            player_pos = new_pos

    if box_pos == target_pos:
        game_over = True
        winner = "Player"

# Gambar semua elemen game di layar
def draw():
    screen.fill(WHITE)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pygame.draw.rect(screen, GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    # Gambar target, kotak, pemain, AI
    pygame.draw.rect(screen, GREEN, (target_pos[0]*TILE_SIZE, target_pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (box_pos[0]*TILE_SIZE+10, box_pos[1]*TILE_SIZE+10, TILE_SIZE-20, TILE_SIZE-20))
    pygame.draw.circle(screen, BLUE, (player_pos[0]*TILE_SIZE+TILE_SIZE//2, player_pos[1]*TILE_SIZE+TILE_SIZE//2), 30)
    pygame.draw.circle(screen, ORANGE, (ai_pos[0]*TILE_SIZE+TILE_SIZE//2, ai_pos[1]*TILE_SIZE+TILE_SIZE//2), 30)

    # Tampilkan pesan pemenang
    if game_over:
        msg = font.render(f"{winner} wins!", True, (0, 0, 0))
        screen.blit(msg, (SCREEN_SIZE // 2 - msg.get_width() // 2, SCREEN_SIZE + 10))

    # Tombol restart
    pygame.draw.rect(screen, (100, 200, 100), (SCREEN_SIZE // 2 - 60, SCREEN_SIZE + 40, 120, 40))
    text = font.render("Restart", True, (255, 255, 255))
    screen.blit(text, (SCREEN_SIZE // 2 - 45, SCREEN_SIZE + 45))

    pygame.display.flip()

# Reset ke kondisi awal game
def reset_game():
    global player_pos, ai_pos, box_pos, target_pos, game_over, winner
    player_pos = [0, 0]
    ai_pos = [4, 4]
    box_pos = [2, 2]
    target_pos = [3, 3]
    game_over = False
    winner = None
    threading.Thread(target=ai_thread, daemon=True).start()

# Mulai thread AI pertama kali
threading.Thread(target=ai_thread, daemon=True).start()

# Loop utama pygame
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