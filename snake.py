import pygame
import random
import sys

# تشغيل pygame
pygame.init()

# إعدادات اللعبة
CELL = 20
COLS = 30
ROWS = 25
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake - لعبة الثعبان")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 25)
small_font = pygame.font.SysFont("arial", 20)

# الألوان
BLACK = (20, 20, 25)
GREEN = (50, 220, 90)
DARK_GREEN = (25, 160, 60)
RED = (240, 65, 65)
WHITE = (245, 245, 245)
GRAY = (55, 55, 65)
GOLD = (255, 205, 60)


def new_food(snake):
    while True:
        food = (
            random.randrange(COLS),
            random.randrange(ROWS)
        )
        if food not in snake:
            return food


def draw_cell(color, position):
    x, y = position
    pygame.draw.rect(
        screen,
        color,
        (x * CELL + 1, y * CELL + 51, CELL - 2, CELL - 2),
        border_radius=5
    )


def show_message(title, subtitle):
    screen.fill(BLACK)

    title_surface = font.render(title, True, WHITE)
    subtitle_surface = small_font.render(subtitle, True, GOLD)

    screen.blit(
        title_surface,
        title_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 20)
        )
    )
    screen.blit(
        subtitle_surface,
        subtitle_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 20)
        )
    )
    pygame.display.flip()


def play_game():
    snake = [(COLS // 2, ROWS // 2)]
    direction = (1, 0)
    next_direction = direction
    food = new_food(snake)
    score = 0
    game_over = False
    won = False

    while True:
        # استقبال ضغطات لوحة المفاتيح
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if game_over:
                    if event.key == pygame.K_SPACE:
                        return
                    continue

                # منع الثعبان من الرجوع مباشرة إلى الخلف
                if event.key in (pygame.K_UP, pygame.K_w):
                    if direction != (0, 1):
                        next_direction = (0, -1)

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if direction != (0, -1):
                        next_direction = (0, 1)

                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if direction != (1, 0):
                        next_direction = (-1, 0)

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if direction != (-1, 0):
                        next_direction = (1, 0)

        if not game_over:
            direction = next_direction

            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            eating = new_head == food
            body_to_check = snake if eating else snake[:-1]

            # الاصطدام بالجدار أو بجسم الثعبان
            if (
                new_head[0] < 0
                or new_head[0] >= COLS
                or new_head[1] < 0
                or new_head[1] >= ROWS
                or new_head in body_to_check
            ):
                game_over = True
            else:
                snake.insert(0, new_head)

                if eating:
                    score += 1

                    if len(snake) == COLS * ROWS:
                        won = True
                        game_over = True
                    else:
                        food = new_food(snake)
                else:
                    snake.pop()

        # رسم الشاشة
        screen.fill(BLACK)

        # شريط النقاط
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 50))
        score_text = font.render(f"Score: {score}", True, WHITE)
        scre
