import pygame
import random
import psycopg2
import sys

# ---------------- PostgreSQL CONFIG ----------------
def get_connection():
    return psycopg2.connect(
        database="snake_db",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )

def get_or_create_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if user:
        user_id = user[0]
        print(f"Қош келдің, {username}!")
        cur.execute("SELECT score, level FROM user_score WHERE user_id = %s ORDER BY score DESC LIMIT 1", (user_id,))
        last_result = cur.fetchone()
        if last_result:
            print(f"Сенің рекордың: {last_result[0]} ұпай, {last_result[1]} деңгей.")
        else:
            print("Бұл пайдаланушыда әлі рекорд жоқ.")
    else:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"Жаңа пайдаланушы қосылды: {username}")
    cur.close()
    conn.close()
    return user_id

def save_score(user_id, score, level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO user_score (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
    conn.commit()
    cur.close()
    conn.close()
    print("Нәтиже базаға сақталды.")

# ---------------- Snake Game ----------------
pygame.init()
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with PostgreSQL")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)

WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
RED = (255,0,0)
GRAY = (100,100,100)

block_size = 20

def draw_snake(snake_list):
    for x in snake_list:
        pygame.draw.rect(win, GREEN, [x[0], x[1], block_size, block_size])

def get_walls(level):
    if level == 2:
        return [[100, 100], [120, 100], [140, 100], [160, 100]]
    elif level == 3:
        return [[0, 100], [20, 100], [40, 100], [60, 100], [80, 100]]
    elif level >= 4:
        return [[300, 200], [320, 200], [340, 200], [360, 200],
                [300, 220], [360, 220]]
    return []

def game_loop(user_id):
    game_over = False
    x, y = WIDTH // 2, HEIGHT // 2
    dx, dy = 0, 0

    speed = 10
    level = 1

    snake_list = []
    length = 1

    food_x = round(random.randrange(0, WIDTH - block_size) / 20.0) * 20.0
    food_y = round(random.randrange(0, HEIGHT - block_size) / 20.0) * 20.0

    score = 0
    walls = []

    while not game_over:
        walls = get_walls(level)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    dx = -block_size
                    dy = 0
                elif event.key == pygame.K_RIGHT:
                    dx = block_size
                    dy = 0
                elif event.key == pygame.K_UP:
                    dy = -block_size
                    dx = 0
                elif event.key == pygame.K_DOWN:
                    dy = block_size
                    dx = 0
                elif event.key == pygame.K_p:
                    paused = True
                    pause_text = font.render("PAUSED - Press C to continue", True, WHITE)
                    win.blit(pause_text, [WIDTH//4, HEIGHT//2])
                    pygame.display.update()
                    while paused:
                        for pe in pygame.event.get():
                            if pe.type == pygame.KEYDOWN and pe.key == pygame.K_c:
                                paused = False
                elif event.key == pygame.K_s:
                    save_score(user_id, score, level)

        x += dx
        y += dy

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_over = True

        win.fill(BLACK)

        for wall in walls:
            pygame.draw.rect(win, GRAY, [wall[0], wall[1], block_size, block_size])

        pygame.draw.rect(win, RED, [food_x, food_y, block_size, block_size])

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > length:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_over = True

        if snake_head in walls:
            game_over = True

        draw_snake(snake_list)

        score_text = font.render(f"Score: {score} | Level: {level}", True, WHITE)
        win.blit(score_text, [10, 10])

        pygame.display.update()

        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - block_size) / 20.0) * 20.0
            food_y = round(random.randrange(0, HEIGHT - block_size) / 20.0) * 20.0
            length += 1
            score += 10
            if score % 50 == 0:
                level += 1
                speed += 2

        clock.tick(speed)

    save_score(user_id, score, level)
    print(f"Ойын аяқталды! Жиналған ұпай: {score}, деңгей: {level}")

if __name__ == "__main__":
    username = input("Атыңды енгіз: ")
    user_id = get_or_create_user(username)
    game_loop(user_id)
