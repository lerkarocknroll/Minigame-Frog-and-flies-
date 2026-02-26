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
pygame.display.set_caption("Лягушка и волшебные грибы")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (135, 206, 250)
PURPLE = (128, 0, 128)
PINK = (255, 182, 193)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_YELLOW = (255, 255, 224)
SKY_BLUE = (135, 206, 235)
DARK_SKY = (25, 25, 112)

# Размеры
FROG_SIZE = 60           # чуть крупнее для деталей
MUSHROOM_SIZE = 35
FLY_SIZE = 30

# Глобальные переменные
score = 0
level = 1
lives = 3
frog_x = WIDTH // 2 - FROG_SIZE // 2
frog_y = HEIGHT - 130
frog_speed = 6
mushrooms = []
flies = []
particles = []
effects = {}

# Параметры сложности
BASE_FLY_SPEED = 2.5
FLY_SPAWN_COUNT = 2
MUSHROOM_FALL_SPEED = 3
MUSHROOM_SPAWN_RATE = 30
BONUS_CHANCE = 0.15

# Счётчики
frame = 0
fly_respawn_timer = 0
game_over = False

# ----------------------------------------------------------------------
# Класс реалистичной лягушки
# ----------------------------------------------------------------------
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
        self.tongue_phase = 0
        self.hit_flash = 0
        self.invincible = False
        self.invincible_timer = 0
        self.glow = 0
        self.blink = False

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
        self.blink = (self.animation_timer % 60) < 5  # моргание раз в секунду

    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.hit_flash = 10
            self.invincible = True
            self.invincible_timer = 120

    def update_effects(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        else:
            self.invincible = False
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.glow > 0:
            self.glow -= 1

    def tongue(self):
        self.tongue_out = True
        self.tongue_length = 30
        self.tongue_phase = 0

    def draw(self, screen):
        # Определяем основной цвет
        body_color = RED if self.hit_flash > 0 else GREEN
        if self.invincible and (self.invincible_timer // 5) % 2 == 0:
            body_color = LIGHT_GREEN

        # Эффект свечения (бонус)
        if self.glow > 0:
            glow_surf = pygame.Surface((self.width+20, self.height+20), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 255, 100, 80), (0, 0, self.width+20, self.height+10))
            screen.blit(glow_surf, (self.x-10, self.y-10))

        # --- Тело лягушки (овал) ---
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height-10)
        pygame.draw.ellipse(screen, body_color, body_rect)

        # --- Задние лапки (справа и слева внизу) ---
        leg_color = DARK_GREEN if body_color == GREEN else body_color
        # Левая лапка
        pygame.draw.ellipse(screen, leg_color, (self.x-8, self.y+self.height-20, 15, 25))
        pygame.draw.ellipse(screen, leg_color, (self.x-5, self.y+self.height-15, 10, 20))
        # Правая лапка
        pygame.draw.ellipse(screen, leg_color, (self.x+self.width-7, self.y+self.height-20, 15, 25))
        pygame.draw.ellipse(screen, leg_color, (self.x+self.width-5, self.y+self.height-15, 10, 20))

        # --- Передние лапки (маленькие) ---
        pygame.draw.ellipse(screen, leg_color, (self.x-3, self.y+self.height//2, 8, 15))
        pygame.draw.ellipse(screen, leg_color, (self.x+self.width-5, self.y+self.height//2, 8, 15))

        # --- Глаза (с веками и бликами) ---
        eye_offsets = [(15, 10), (self.width-25, 10)]
        for i, (ox, oy) in enumerate(eye_offsets):
            # Белок
            pygame.draw.circle(screen, WHITE, (self.x+ox, self.y+oy), 10)
            # Зрачок (смотрит немного в сторону центра)
            pupil_x = self.x+ox + (2 if i==0 else -2)
            pupil_y = self.y+oy - 1
            pygame.draw.circle(screen, BLACK, (pupil_x, pupil_y), 5)
            # Блик
            pygame.draw.circle(screen, WHITE, (pupil_x-2, pupil_y-2), 2)

        # Веки (моргание)
        if self.blink:
            for ox, oy in eye_offsets:
                pygame.draw.arc(screen, body_color, (self.x+ox-10, self.y+oy-10, 20, 15), 0, math.pi, 3)

        # --- Рот (линия) ---
        pygame.draw.arc(screen, BLACK, (self.x+15, self.y+20, 30, 15), 0.1, math.pi-0.1, 2)

        # --- Язык (с изгибом) ---
        if self.tongue_out:
            start_x = self.x + self.width//2
            start_y = self.y + 15
            # Язык летит к цели (изгибается)
            points = [(start_x, start_y)]
            for t in range(1, self.tongue_length, 5):
                x = start_x + t * 0.5
                y = start_y - t * 0.8 + 5 * math.sin(t * 0.5 + self.tongue_phase)
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(screen, RED, False, points, 4)
            self.tongue_length -= 1
            self.tongue_phase += 0.3
            if self.tongue_length <= 0:
                self.tongue_out = False

# ----------------------------------------------------------------------
# Класс гриба (реалистичный мухомор)
# ----------------------------------------------------------------------
class Mushroom:
    def __init__(self, bonus=False):
        self.size = MUSHROOM_SIZE
        self.x = random.randint(0, WIDTH - self.size)
        self.y = -self.size
        self.speed = MUSHROOM_FALL_SPEED + random.uniform(-1, 1)
        self.bonus = bonus
        self.wobble = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        self.y += self.speed
        self.wobble = math.sin(pygame.time.get_ticks() * 0.02) * 3

    def is_off_screen(self):
        return self.y > HEIGHT

    def draw(self, screen):
        # Ножка (белая, чуть изогнутая)
        stem_x = self.x + self.size//2 - 3 + self.wobble * 0.2
        stem_rect = pygame.Rect(stem_x, self.y + self.size//2 - 5, 6, self.size//2+5)
        pygame.draw.rect(screen, WHITE, stem_rect)
        # Добавляем лёгкую тень на ножке
        pygame.draw.line(screen, (200, 200, 200), (stem_x+1, self.y+self.size//2), (stem_x+1, self.y+self.size-5), 2)

        # Шляпка (полукруг)
        cap_color = GOLD if self.bonus else RED
        dot_color = YELLOW if self.bonus else WHITE

        # Рисуем эллипс, затем обрезаем нижнюю половину (имитация полукруга)
        cap_surf = pygame.Surface((self.size, self.size//2+5), pygame.SRCALPHA)
        pygame.draw.ellipse(cap_surf, cap_color, (0, 0, self.size, self.size//2+5))
        # Накладываем на экран со смещением (шляпка нависает над ножкой)
        screen.blit(cap_surf, (self.x + self.wobble, self.y))

        # Точечки на шляпке (белые/жёлтые)
        dot_positions = [
            (self.x + 8 + self.wobble, self.y + 8),
            (self.x + 20 + self.wobble, self.y + 12),
            (self.x + 12 + self.wobble, self.y + 18),
            (self.x + 25 + self.wobble, self.y + 7)
        ]
        for dx, dy in dot_positions:
            pygame.draw.circle(screen, dot_color, (int(dx), int(dy)), 3)

        # Для золотых добавляем свечение
        if self.bonus:
            glow = pygame.Surface((self.size+10, self.size+5), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 215, 0, 60), (0, 0, self.size+10, self.size//2+10))
            screen.blit(glow, (self.x-5 + self.wobble, self.y-5))

# ----------------------------------------------------------------------
# Класс мухи (синяя, с прозрачными крыльями)
# ----------------------------------------------------------------------
class Fly:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = FLY_SIZE
        self.speed = speed
        self.wing_phase = 0
        self.direction = random.choice([-1, 1])

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            angle = math.atan2(dy, dx)
            angle += random.uniform(-0.2, 0.2)
            move_x = math.cos(angle) * self.speed
            move_y = math.sin(angle) * self.speed
            self.x += move_x
            self.y += move_y
        self.x = max(0, min(self.x, WIDTH - self.size))
        self.y = max(0, min(self.y, HEIGHT - self.size))
        self.wing_phase = (self.wing_phase + 0.5) % (2 * math.pi)

    def draw(self, screen):
        # Тело (синее, вытянутое)
        body_rect = pygame.Rect(self.x, self.y, self.size, self.size-5)
        pygame.draw.ellipse(screen, BLUE, body_rect)

        # Глаза (белые с чёрными зрачками)
        pygame.draw.circle(screen, WHITE, (int(self.x+8), int(self.y+7)), 6)
        pygame.draw.circle(screen, WHITE, (int(self.x+20), int(self.y+7)), 6)
        pygame.draw.circle(screen, BLACK, (int(self.x+9), int(self.y+7)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x+21), int(self.y+7)), 3)

        # Крылья (полупрозрачные, с жилками)
        wing_surf = pygame.Surface((40, 30), pygame.SRCALPHA)
        wing_span = 18 + 6 * math.sin(self.wing_phase)
        # Левое крыло
        pygame.draw.polygon(wing_surf, (180, 180, 255, 120),
                            [(5, 5), (5-wing_span, 0), (5-wing_span//2, 18)])
        # Правое крыло
        pygame.draw.polygon(wing_surf, (180, 180, 255, 120),
                            [(25, 5), (25+wing_span, 0), (25+wing_span//2, 18)])
        screen.blit(wing_surf, (self.x-10, self.y-10))

        # Жилки на крыльях
        pygame.draw.line(screen, (100, 100, 150), (self.x-3, self.y-2), (self.x-10, self.y-8), 1)
        pygame.draw.line(screen, (100, 100, 150), (self.x+30, self.y-2), (self.x+38, self.y-8), 1)

# ----------------------------------------------------------------------
# Класс частиц (цветные искры)
# ----------------------------------------------------------------------
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
        self.vy += 0.05
        self.life -= 1

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (3, 3), 3)
        screen.blit(s, (int(self.x), int(self.y)))

# ----------------------------------------------------------------------
# Реалистичный травяной фон
# ----------------------------------------------------------------------
def draw_background():
    # Градиентное небо
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(135 + (25 * ratio))
        g = int(206 + (20 * ratio))
        b = int(235 + (20 * ratio))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Облака (пушистые)
    cloud_offset = (pygame.time.get_ticks() // 30) % WIDTH
    for i in range(3):
        x = (i * 300 + cloud_offset) % WIDTH - 100
        # Несколько эллипсов, создающих объём
        pygame.draw.ellipse(screen, (255, 255, 255, 180), (x, 50, 150, 50))
        pygame.draw.ellipse(screen, (255, 255, 255, 200), (x+30, 30, 120, 40))
        pygame.draw.ellipse(screen, (255, 255, 255, 160), (x+60, 40, 130, 45))

    # --- Трава (детализированная) ---
    ground_y = HEIGHT - 70
    # Основа земли
    pygame.draw.rect(screen, (34, 139, 34), (0, ground_y, WIDTH, 100))
    # Тёмные пятна (имитация неровностей)
    for _ in range(20):
        x = random.randint(0, WIDTH)
        pygame.draw.ellipse(screen, (20, 80, 20), (x, ground_y+10, 40, 15))

    # Травинки (разной высоты, изогнутые)
    for i in range(0, WIDTH, 12):
        height = random.randint(20, 50)
        thickness = random.choice([1, 2])
        sway = math.sin(pygame.time.get_ticks() * 0.01 + i) * 3
        # Основная линия
        points = [(i, ground_y), (i-3+sway, ground_y-height), (i+3+sway, ground_y-height-5)]
        pygame.draw.lines(screen, (0, 100, 0), False, points[:2], thickness)
        # Вторая травинка рядом
        if random.random() > 0.7:
            points2 = [(i+5, ground_y), (i+5-2+sway, ground_y-height+10), (i+5+sway, ground_y-height+5)]
            pygame.draw.lines(screen, (0, 120, 0), False, points2[:2], 1)

    # Цветочки и мелкие камешки
    for _ in range(15):
        fx = random.randint(0, WIDTH)
        fy = ground_y - random.randint(5, 15)
        # Цветок (5 лепестков)
        if random.random() > 0.6:
            col = random.choice([PINK, YELLOW, WHITE, PURPLE])
            pygame.draw.circle(screen, col, (fx, fy), 4)
            pygame.draw.circle(screen, YELLOW, (fx, fy), 2)
        else:
            # Камешек
            pygame.draw.circle(screen, (100, 100, 100), (fx, fy), 3)

# ----------------------------------------------------------------------
# Сброс игры
# ----------------------------------------------------------------------
def reset_game():
    global frog, mushrooms, flies, particles, effects, score, level, lives, game_over, frame, fly_respawn_timer
    frog = Frog(WIDTH//2 - FROG_SIZE//2, HEIGHT - 130)
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
    for _ in range(FLY_SPAWN_COUNT):
        x = random.randint(0, WIDTH - FLY_SIZE)
        y = random.randint(0, HEIGHT - FLY_SIZE)
        flies.append(Fly(x, y, BASE_FLY_SPEED))

# ----------------------------------------------------------------------
# Основной цикл
# ----------------------------------------------------------------------
def game_loop():
    global score, level, lives, game_over, frame, fly_respawn_timer, frog, mushrooms, flies, particles, effects
    global MUSHROOM_FALL_SPEED
    reset_game()
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)

    while True:
        clock.tick(60)
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

            # Эффекты
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
            if 'glow' in effects:
                frog.glow = 30

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
                        eff = random.choice(['slow', 'invincible', 'glow'])
                        if eff == 'slow':
                            effects['slow'] = 300
                        elif eff == 'invincible':
                            frog.invincible = True
                            effects['invincible'] = 300
                        else:
                            effects['glow'] = 30
                    else:
                        score += 10
                    frog.tongue()
                    # Частицы
                    for _ in range(12):
                        vx = random.uniform(-2, 2)
                        vy = random.uniform(-4, 0)
                        col = YELLOW if mush.bonus else WHITE
                        particles.append(Particle(mush.x + mush.size//2, mush.y + mush.size//2,
                                                  col, (vx, vy), 30))

            # Обновление мух
            for fly in flies[:]:
                fly.update(frog)
                if frog.get_rect().colliderect(fly.get_rect()):
                    if not frog.invincible and 'invincible' not in effects:
                        frog.hit()
                        flies.remove(fly)
                        for _ in range(15):
                            vx = random.uniform(-2, 2)
                            vy = random.uniform(-2, 1)
                            particles.append(Particle(fly.x + fly.size//2, fly.y + fly.size//2,
                                                      BLUE, (vx, vy), 25))
                        fly_respawn_timer = 30
                        if frog.lives <= 0:
                            game_over = True
                    else:
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

            # Частицы
            particles = [p for p in particles if p.life > 0]
            for p in particles:
                p.update()

            # Повышение уровня
            if score // 200 > level - 1:
                level += 1
                MUSHROOM_FALL_SPEED += 0.5
                flies.append(Fly(random.randint(0, WIDTH-FLY_SIZE),
                                 random.randint(0, HEIGHT-FLY_SIZE),
                                 BASE_FLY_SPEED + (level-1)*0.3))

        # Отрисовка
        draw_background()

        for mush in mushrooms:
            mush.draw(screen)
        for fly in flies:
            fly.draw(screen)
        frog.draw(screen)
        for p in particles:
            p.draw(screen)

        # Текст с тенью
        def draw_text_with_shadow(text, x, y, color, font):
            shadow = font.render(text, True, BLACK)
            text_surf = font.render(text, True, color)
            screen.blit(shadow, (x+2, y+2))
            screen.blit(text_surf, (x, y))

        draw_text_with_shadow(f"Очки: {score}", 10, 10, WHITE, font)
        draw_text_with_shadow(f"Жизни: {frog.lives}", 10, 50, WHITE, font)
        draw_text_with_shadow(f"Уровень: {level}", 10, 90, YELLOW, font)

        if 'slow' in effects:
            draw_text_with_shadow("ЗАМЕДЛЕНИЕ", WIDTH-200, 10, LIGHT_BLUE, font)
        if 'invincible' in effects or frog.invincible:
            draw_text_with_shadow("НЕУЯЗВИМОСТЬ", WIDTH-250, 50, GOLD, font)

        if game_over:
            over_text = big_font.render("GAME OVER", True, RED)
            over_shadow = big_font.render("GAME OVER", True, BLACK)
            screen.blit(over_shadow, (WIDTH//2-198, HEIGHT//2-98))
            screen.blit(over_text, (WIDTH//2-200, HEIGHT//2-100))
            score_final = font.render(f"Вы набрали {score} очков", True, WHITE)
            restart = font.render("Нажмите R для рестарта", True, WHITE)
            screen.blit(score_final, (WIDTH//2-120, HEIGHT//2))
            screen.blit(restart, (WIDTH//2-150, HEIGHT//2+60))

        pygame.display.flip()

if __name__ == "__main__":
    game_loop()
