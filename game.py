# Что реализованно в игре
# Cоздание игрового окна
# Генерация волн и деревьев
# Отрисовка игрового поля
# Отрисовка вертолета
# Обработка событий
# Обновление экрана
# Система жизней для вертолета
# Цикл игры
# Завершение игры


import pygame
import random

# Инициализация Pygame
pygame.init()

# Размеры окна игры
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Создание игрового поля
game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Helicopter University Game")

# Размеры клетки на игровом поле
CELL_SIZE = 50

# Генерация рек
def generate_rivers(num_rivers):
    return [(random.randint(0, WINDOW_WIDTH // CELL_SIZE - 1), random.randint(0, WINDOW_HEIGHT // CELL_SIZE - 1)) for _ in range(num_rivers)]

# Генерация деревьев
def generate_trees(num_trees):
    return [(random.randint(0, WINDOW_WIDTH // CELL_SIZE - 1), random.randint(0, WINDOW_HEIGHT // CELL_SIZE - 1)) for _ in range(num_trees)]

# Проверка принадлежности клетки игровому полю
def is_valid_cell(x, y):
    return 0 <= x < WINDOW_WIDTH // CELL_SIZE and 0 <= y < WINDOW_HEIGHT // CELL_SIZE

# Отрисовка объекта на игровом поле
def draw_object(symbol, x, y):
    game_window.blit(pygame.font.SysFont("Segoe UI Emoji", 30).render(symbol, True, (0, 0, 0)), (x * CELL_SIZE + 10, y * CELL_SIZE + 10))

# Основной цикл игры
def game_loop():
    running = True

    # Генерация рек и деревьев
    rivers = generate_rivers(5)
    trees = generate_trees(10)

    # Позиция вертолета
    helicopter_x, helicopter_y = WINDOW_WIDTH // 2 // CELL_SIZE, WINDOW_HEIGHT // 2 // CELL_SIZE

    # Жизни игрока
    lives = 3

    while running and lives > 0:
        # Отрисовка фона
        game_window.fill((0, 255, 0))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            for x in range(0, WINDOW_WIDTH, CELL_SIZE):
                cell = (x // CELL_SIZE, y // CELL_SIZE)
                if cell in rivers:
                    pygame.draw.rect(game_window, (0, 0, 255), (x, y, CELL_SIZE, CELL_SIZE))
                    draw_object("🌊", *cell)
                else:
                    pygame.draw.rect(game_window, (0, 255, 0), (x, y, CELL_SIZE, CELL_SIZE))
                    draw_object("🟩", *cell)

        # Отрисовка деревьев
        for tree in trees:
            draw_object("🌳", *tree)

        # Отрисовка вертолета
        draw_object("🚁", helicopter_x, helicopter_y)

        # Отрисовка жизней в левом верхнем углу
        draw_object(f"❤️ {lives}", 0, 0)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Перемещение вертолета
                if event.key == pygame.K_UP and is_valid_cell(helicopter_x, helicopter_y - 1):
                    helicopter_y -= 1
                elif event.key == pygame.K_DOWN and is_valid_cell(helicopter_x, helicopter_y + 1):
                    helicopter_y += 1
                elif event.key == pygame.K_LEFT and is_valid_cell(helicopter_x - 1, helicopter_y):
                    helicopter_x -= 1
                elif event.key == pygame.K_RIGHT and is_valid_cell(helicopter_x + 1, helicopter_y):
                    helicopter_x += 1

                # Проверка столкновения вертолета с рекой или деревом
                if (helicopter_x, helicopter_y) in rivers or (helicopter_x, helicopter_y) in trees:
                    print("Collision!")
                    lives -= 1

        # Обновление экрана
        pygame.display.update()

    # Конец игры если закончились жизни
    print("Game Over")

# Запуск игры
game_loop()

# Завершение Pygame
pygame.quit()
