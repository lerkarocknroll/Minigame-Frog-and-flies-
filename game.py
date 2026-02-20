import pygame
import sys
import random
import math
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Лягушка и злые мухи")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Размеры
FROG_SIZE = 50
MUSHROOM_SIZE = 30
FLY_SIZE = 25

# Глобальные переменные игры
score = 0
level = 1
lives = 3
frog_x = WIDTH // 2 - FROG_SIZE // 2
frog_y = HEIGHT - 100
frog_speed = 6
mushrooms = []
flies = []
particles = []
effects = {}  # для временных эффектов: 'slow' или 'invincible'

# Параметры сложности (настраиваются)
BASE_FLY_SPEED = 2.5
FLY_SPAWN_COUNT = 2
MUSHROOM_FALL_SPEED = 3
MUSHROOM_SPAWN_RATE = 30  # кадров между появлением
BONUS_CHANCE = 0.15        # 15% шанс золотого гриба

# Счётчики
frame = 0
fly_respawn_timer = 0
game_over = False

# Класс лягушки с анимацией
class Frog:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = FROG_SIZE
        self.height = FROG_SIZE
        self.speed = frog_speed
        self.lives = lives
        self.animation_timer = 0
        self.tongue_out = False
        self.tongue_length = 0
        self.hit_flash = 0
        self.invincible = False
        self.invincible_timer = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x <= WIDTH - self.width:
            self.x = new_x
        if 0 <= new_y <= HEIGHT - self.height:
            self.y = new_y
        self.animation_timer += 1

    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.hit_flash = 10
            self.invincible = True
            self.invincible_timer = 120  # 2 секунды при 60 fps

    def update_effects(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        else:
            self.invincible = False
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def tongue(self):
        self.tongue_out = True
        self.tongue_length = 20

    def draw(self, screen):
        # Если вспышка урона, рисуем красным
        color = RED if self.hit_flash > 0 else GREEN
        # Мигание при неуязвимости
        if self.invincible and (self.invincible_timer // 5) % 2 == 0:
            color = LIGHT_GREEN

        # Тело лягушки (овал)
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height-10)
        pygame.draw.ellipse(screen, color, body_rect)
        # Глаза
        eye_offsets = [(10, 8), (self.width-20, 8)]
        for ox, oy in eye_offsets:
            pygame.draw.circle(screen, WHITE, (self.x+ox, self.y+oy), 8)
            pygame.draw.circle(screen, BLACK, (self.x+ox+2, self.y+oy-1), 4)
        # Зрачки двигаются (моргание)
        if self.animation_timer % 40 < 10:  # каждые 40 кадров моргание 10 кадров
            pygame.draw.line(screen, BLACK, (self.x+5, self.y+12), (self.x+15, self.y+12), 2)
            pygame.draw.line(screen, BLACK, (self.x+35, self.y+12), (self.x+45, self.y+12), 2)
        # Язык
        if self.tongue_out:
            start = (self.x + self.width//2, self.y + 5)
            end = (self.x + self.width//2, self.y - self.tongue_length)
            pygame.draw.line(screen, RED, start, end, 5)
            self.tongue_length -= 2
            if self.tongue_length <= 0:
                self.tongue_out = False

# Класс гриба с анимацией
class Mushroom:
    def __init__(self, bonus=False):
        self.size = MUSHROOM_SIZE
        self.x = random.randint(0, WIDTH - self.size)
        self.y = -self.size
        self.speed = MUSHROOM_FALL_SPEED + random.uniform(-1, 1)
        self.bonus = bonus
        self.rotation = 0
        self.pulse = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        self.y += self.speed
        self.rotation += 2
        self.pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3

    def is_off_screen(self):
        return self.y > HEIGHT

    def draw(self, screen):
        color = GOLD if self.bonus else BROWN
        # Ножка
        pygame.draw.rect(screen, color, (self.x + 10, self.y + 15, 10, 15))
        # Шляпка (полукруг)
        cap_rect = pygame.Rect(self.x, self.y, self.size, self.size//2)
        pygame.draw.ellipse(screen, color, cap_rect)
        # Точечки на шляпке
        if self.bonus:
            pygame.draw.circle(screen, YELLOW, (self.x + 8, self.y + 8), 3)
            pygame.draw.circle(screen, YELLOW, (self.x + 22, self.y + 12), 3)
        else:
            pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 8), 3)
            pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 12), 3)
        # Лёгкое свечение для бонусных
        if self.bonus:
            s = pygame.Surface((self.size+10, self.size+10), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 0, 50), (15, 15), 20)
            screen.blit(s, (self.x-5, self.y-5))

# Класс мухи с анимацией крыльев
class Fly:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = FLY_SIZE
        self.speed = speed
        self.target_x = x
        self.target_y = y
        self.wing_phase = 0
        self.direction = random.choice([-1, 1])

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self, target):
        # Плавное движение к цели (лягушке) с небольшими отклонениями
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            angle = math.atan2(dy, dx)
            angle += random.uniform(-0.2, 0.2)  # случайные колебания
            move_x = math.cos(angle) * self.speed
            move_y = math.sin(angle) * self.speed
            self.x += move_x
            self.y += move_y
        # Не вылетаем за экран
        self.x = max(0, min(self.x, WIDTH - self.size))
        self.y = max(0, min(self.y, HEIGHT - self.size))
        # Анимация крыльев
        self.wing_phase = (self.wing_phase + 0.5) % (2 * math.pi)

    def draw(self, screen):
        # Тело
        pygame.draw.ellipse(screen, RED, self.get_rect())
        # Глаза
        pygame.draw.circle(screen, WHITE, (int(self.x+7), int(self.y+7)), 4)
        pygame.draw.circle(screen, WHITE, (int(self.x+18), int(self.y+7)), 4)
        pygame.draw.circle(screen, BLACK, (int(self.x+8), int(self.y+7)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x+19), int(self.y+7)), 2)
        # Крылья (движутся)
        wing_span = 10 + 5 * math.sin(self.wing_phase)
        left_wing = (self.x+5, self.y+10)
        right_wing = (self.x+20, self.y+10)
        pygame.draw.line(screen, (200, 200, 200), left_wing,
                         (left_wing[0]-wing_span, left_wing[1]-5), 3)
        pygame.draw.line(screen, (200, 200, 200), right_wing,
                         (right_wing[0]+wing_span, right_wing[1]-5), 3)

# Класс частиц
class Particle:
    def __init__(self, x, y, color, velocity, life):
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # гравитация
        self.life -= 1

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (2, 2), 2)
        screen.blit(s, (int(self.x), int(self.y)))

# Рисование фона
def draw_background():
    # Небо
    screen.fill(BLUE)
    # Облака (движутся)
    cloud_offset = (pygame.time.get_ticks() // 10) % WIDTH
    for i in range(3):
        x = (i * 300 + cloud_offset) % WIDTH - 100
        pygame.draw.ellipse(screen, WHITE, (x, 50, 150, 50))
        pygame.draw.ellipse(screen, WHITE, (x+30, 30, 120, 40))
    # Трава (полосы)
    for i in range(0, HEIGHT, 20):
        shade = LIGHT_GREEN if (i // 20) % 2 else GREEN
        pygame.draw.rect(screen, shade, (0, HEIGHT-i, WIDTH, 10))
    # Травинки (анимированные линии)
    for blade in range(0, WIDTH, 30):
        sway = math.sin(pygame.time.get_ticks() * 0.005 + blade) * 5
        pygame.draw.line(screen, GREEN, (blade, HEIGHT-20), (blade+sway, HEIGHT-50), 2)

# Сброс игры
def reset_game():
    global frog, mushrooms, flies, particles, effects, score, level, lives, game_over, frame, fly_respawn_timer
    frog = Frog(WIDTH//2 - FROG_SIZE//2, HEIGHT - 100)
    mushrooms.clear()
    flies.clear()
    particles.clear()
    effects.clear()
    score = 0
    level = 1
    lives = 3
    frog.lives = lives
    game_over = False
    frame = 0
    fly_respawn_timer = 0
    # Создаём начальных мух
    for _ in range(FLY_SPAWN_COUNT):
        x = random.randint(0, WIDTH - FLY_SIZE)
        y = random.randint(0, HEIGHT - FLY_SIZE)
        flies.append(Fly(x, y, BASE_FLY_SPEED))

# Основной цикл
def game_loop():
    global score, level, lives, game_over, frame, fly_respawn_timer, frog, mushrooms, flies, particles, effects
    reset_game()
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)

    while True:
        dt = clock.tick(60)
        frame += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_r and game_over:
                reset_game()

        if not game_over:
            # Управление
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[K_LEFT]:
                dx = -frog.speed
            if keys[K_RIGHT]:
                dx = frog.speed
            if keys[K_UP]:
                dy = -frog.speed
            if keys[K_DOWN]:
                dy = frog.speed
            frog.move(dx, dy)

            # Обновление эффектов
            frog.update_effects()
            if 'slow' in effects:
                effects['slow'] -= 1
                if effects['slow'] <= 0:
                    del effects['slow']
            if 'invincible' in effects:
                effects['invincible'] -= 1
                if effects['invincible'] <= 0:
                    frog.invincible = False
                    del effects['invincible']

            # Спавн грибов
            if frame % MUSHROOM_SPAWN_RATE == 0:
                bonus = random.random() < BONUS_CHANCE
                mushrooms.append(Mushroom(bonus))

            # Обновление грибов
            for mush in mushrooms[:]:
                mush.update()
                if mush.is_off_screen():
                    mushrooms.remove(mush)
                elif frog.get_rect().colliderect(mush.get_rect()):
                    mushrooms.remove(mush)
                    if mush.bonus:
                        score += 50
                        # Бонус: случайный эффект
                        eff = random.choice(['slow', 'invincible'])
                        if eff == 'slow':
                            effects['slow'] = 300  # 5 секунд
                        else:
                            frog.invincible = True
                            effects['invincible'] = 300
                    else:
                        score += 10
                    frog.tongue()
                    # Частицы
                    for _ in range(10):
                        vx = random.uniform(-2, 2)
                        vy = random.uniform(-3, 0)
                        particles.append(Particle(mush.x + mush.size//2, mush.y + mush.size//2,
                                                  YELLOW if mush.bonus else BROWN, (vx, vy), 30))

            # Обновление мух
            for fly in flies[:]:
                fly.update(frog)
                if frog.get_rect().colliderect(fly.get_rect()):
                    if not frog.invincible and 'invincible' not in effects:
                        frog.hit()
                        flies.remove(fly)
                        # Частицы
                        for _ in range(15):
                            vx = random.uniform(-3, 3)
                            vy = random.uniform(-2, 2)
                            particles.append(Particle(fly.x + fly.size//2, fly.y + fly.size//2,
                                                      RED, (vx, vy), 30))
                        fly_respawn_timer = 30  # через полсекунды новая муха
                        if frog.lives <= 0:
                            game_over = True
                    else:
                        # Если неуязвим, муха отскакивает
                        fly.x += random.randint(-50, 50)
                        fly.y += random.randint(-50, 50)

            # Воскрешение мух
            if fly_respawn_timer > 0:
                fly_respawn_timer -= 1
            else:
                if len(flies) < FLY_SPAWN_COUNT + level - 1:
                    x = random.randint(0, WIDTH - FLY_SIZE)
                    y = random.randint(0, HEIGHT - FLY_SIZE)
                    speed = BASE_FLY_SPEED + (level-1) * 0.3
                    flies.append(Fly(x, y, speed))

            # Обновление частиц
            particles = [p for p in particles if p.life > 0]
            for p in particles:
                p.update()

            # Повышение уровня
            if score // 200 > level - 1:
                level += 1
                # Увеличиваем сложность
                global MUSHROOM_FALL_SPEED
                MUSHROOM_FALL_SPEED += 0.5
                # Добавляем муху сразу
                flies.append(Fly(random.randint(0, WIDTH-FLY_SIZE), random.randint(0, HEIGHT-FLY_SIZE),
                                 BASE_FLY_SPEED + (level-1)*0.3))

        # Отрисовка
        draw_background()

        # Рисуем объекты
        for mush in mushrooms:
            mush.draw(screen)
        for fly in flies:
            fly.draw(screen)
        frog.draw(screen)
        for p in particles:
            p.draw(screen)

        # Отображение текста
        score_text = font.render(f"Очки: {score}", True, WHITE)
        lives_text = font.render(f"Жизни: {frog.lives}", True, WHITE)
        level_text = font.render(f"Уровень: {level}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(level_text, (10, 90))

        if 'slow' in effects:
            slow_text = font.render("ЗАМЕДЛЕНИЕ", True, BLUE)
            screen.blit(slow_text, (WIDTH-200, 10))
        if 'invincible' in effects or frog.invincible:
            inv_text = font.render("НЕУЯЗВИМОСТЬ", True, GOLD)
            screen.blit(inv_text, (WIDTH-250, 50))

        if game_over:
            over_text = big_font.render("GAME OVER", True, RED)
            score_final = font.render(f"Вы набрали {score} очков", True, WHITE)
            restart = font.render("Нажмите R для рестарта", True, WHITE)
            screen.blit(over_text, (WIDTH//2-200, HEIGHT//2-100))
            screen.blit(score_final, (WIDTH//2-120, HEIGHT//2))
            screen.blit(restart, (WIDTH//2-150, HEIGHT//2+60))

        pygame.display.flip()

if __name__ == "__main__":
    game_loop()
