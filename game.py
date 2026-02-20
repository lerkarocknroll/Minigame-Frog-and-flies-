import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки экрана
screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Лягушка и злые мухи")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# Параметры игры (можно менять для настройки сложности)
INITIAL_LIVES = 3
MUSHROOM_SPEED = 4          # скорость падения грибов
FLY_SPEED = 2                # базовая скорость мух
FLY_COUNT = 2                 # начальное количество мух
MUSHROOM_FREQUENCY = 25       # чем меньше число, тем чаще появляются грибы (кадры)
LEVEL_UP_SCORE = 10           # очков для повышения уровня
SPEED_INCREASE_PER_LEVEL = 0.5 # добавка к скорости мух за уровень

# Размеры объектов
FROG_SIZE = 40
MUSHROOM_SIZE = 30
FLY_SIZE = 30

# Класс лягушки
class Frog:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = FROG_SIZE
        self.height = FROG_SIZE
        self.speed = 6
        self.lives = INITIAL_LIVES

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        # Не выходим за границы экрана
        if 0 <= new_x <= screen_size[0] - self.width:
            self.x = new_x
        if 0 <= new_y <= screen_size[1] - self.height:
            self.y = new_y

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.get_rect())
        # Глазки
        eye_size = 5
        pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 10), eye_size)
        pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 10), eye_size)
        pygame.draw.circle(screen, BLACK, (self.x + 12, self.y + 12), 2)
        pygame.draw.circle(screen, BLACK, (self.x + 32, self.y + 12), 2)

# Класс гриба
class Mushroom:
    def __init__(self):
        self.size = MUSHROOM_SIZE
        self.x = random.randint(0, screen_size[0] - self.size)
        self.y = -self.size  # начинаем за верхней границей
        self.speed = MUSHROOM_SPEED

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        self.y += self.speed

    def is_off_screen(self):
        return self.y > screen_size[1]

    def draw(self, screen):
        pygame.draw.rect(screen, BROWN, self.get_rect())
        # Шляпка
        pygame.draw.circle(screen, (160, 82, 45), (self.x + self.size//2, self.y + 5), self.size//2)

# Класс мухи
class Fly:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = FLY_SIZE
        self.speed = speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self, target):
        # Движение к лягушке (target - объект Frog)
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        # Не вылетаем за экран (остаёмся в пределах)
        self.x = max(0, min(self.x, screen_size[0] - self.size))
        self.y = max(0, min(self.y, screen_size[1] - self.size))

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.get_rect())
        # Крылышки
        pygame.draw.line(screen, BLACK, (self.x + 5, self.y + 5), (self.x + 25, self.y + 15), 2)
        pygame.draw.line(screen, BLACK, (self.x + 25, self.y + 5), (self.x + 5, self.y + 15), 2)
        # Глаза
        pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 8), 3)
        pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 8), 3)
        pygame.draw.circle(screen, BLACK, (self.x + 9, self.y + 9), 2)
        pygame.draw.circle(screen, BLACK, (self.x + 23, self.y + 9), 2)

# Основная функция игры
def game_loop():
    clock = pygame.time.Clock()
    frog = Frog(screen_size[0]//2 - FROG_SIZE//2, screen_size[1] - 100)

    mushrooms = []
    flies = []
    # Создаём начальных мух
    for _ in range(FLY_COUNT):
        x = random.randint(0, screen_size[0] - FLY_SIZE)
        y = random.randint(0, screen_size[1] - FLY_SIZE)
        flies.append(Fly(x, y, FLY_SPEED))

    score = 0
    level = 1
    frame_counter = 0
    game_over = False

    # Шрифты
    font = pygame.font.Font(None, 36)

    while not game_over:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Управление лягушкой
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -frog.speed
        if keys[pygame.K_RIGHT]:
            dx = frog.speed
        if keys[pygame.K_UP]:
            dy = -frog.speed
        if keys[pygame.K_DOWN]:
            dy = frog.speed
        frog.move(dx, dy)

        # Создание новых грибов
        frame_counter += 1
        if frame_counter % MUSHROOM_FREQUENCY == 0:
            mushrooms.append(Mushroom())

        # Обновление грибов
        for mush in mushrooms[:]:
            mush.update()
            if mush.is_off_screen():
                mushrooms.remove(mush)
            elif frog.get_rect().colliderect(mush.get_rect()):
                # Лягушка поймала гриб
                mushrooms.remove(mush)
                score += 1
                # Проверка повышения уровня
                if score % LEVEL_UP_SCORE == 0:
                    level += 1
                    levelup_sound.play()
                    # Добавляем новую муху
                    flies.append(Fly(
                        random.randint(0, screen_size[0] - FLY_SIZE),
                        random.randint(0, screen_size[1] - FLY_SIZE),
                        FLY_SPEED + (level-1) * SPEED_INCREASE_PER_LEVEL
                    ))
                    # Увеличиваем скорость всех мух
                    for fly in flies:
                        fly.speed = FLY_SPEED + (level-1) * SPEED_INCREASE_PER_LEVEL

        # Обновление мух
        for fly in flies[:]:
            fly.update(frog)
            if frog.get_rect().colliderect(fly.get_rect()):
                # Муха ужалила лягушку
                flies.remove(fly)
                frog.lives -= 1
                # Если жизни кончились - конец игры
                if frog.lives <= 0:
                    game_over = True
                    break
                # Создаём новую муху взамен (чтобы количество не уменьшалось)
                flies.append(Fly(
                    random.randint(0, screen_size[0] - FLY_SIZE),
                    random.randint(0, screen_size[1] - FLY_SIZE),
                    FLY_SPEED + (level-1) * SPEED_INCREASE_PER_LEVEL
                ))

        # Отрисовка
        screen.fill(BLACK)
        frog.draw(screen)
        for mush in mushrooms:
            mush.draw(screen)
        for fly in flies:
            fly.draw(screen)

        # Отображение счёта, жизней, уровня
        score_text = font.render(f"Грибы: {score}", True, WHITE)
        lives_text = font.render(f"Жизни: {frog.lives}", True, WHITE)
        level_text = font.render(f"Уровень: {level}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(level_text, (10, 90))

        pygame.display.flip()
        clock.tick(60)

    # Экран окончания игры
    screen.fill(BLACK)
    game_over_text = font.render("ИГРА ОКОНЧЕНА", True, RED)
    final_score_text = font.render(f"Вы собрали {score} грибов", True, WHITE)
    screen.blit(game_over_text, (screen_size[0]//2 - 100, screen_size[1]//2 - 30))
    screen.blit(final_score_text, (screen_size[0]//2 - 120, screen_size[1]//2 + 10))
    pygame.display.flip()
    pygame.time.wait(4000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
