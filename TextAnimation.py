import pygame
import random
import time
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 1000, 350
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ИСКРА ТЕХНОЛОГИИ - Анимация с GUI")

# Цвета
PHASE3 = (124,252,0)
PHASE2 = (220,20,60)
PHASE1 = (255,215,0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (0, 150, 0)

# Шрифты
font_small = pygame.font.SysFont('Arial', 16)
font_medium = pygame.font.SysFont('Arial', 20)
font_large = pygame.font.SysFont('Arial', 24, bold=True)


# Элементы GUI
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.txt_surface = font_small.render(text, True, WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = DARK_GREEN if self.active else GRAY

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font_small.render(self.text, True, WHITE)
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.txt_surface = font_medium.render(text, True, WHITE)
        self.hover = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.hover
        return False

    def draw(self, screen):
        color = DARK_GREEN if self.hover else GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        screen.blit(self.txt_surface,
                    (self.rect.x + (self.rect.w - self.txt_surface.get_width()) // 2,
                     self.rect.y + (self.rect.h - self.txt_surface.get_height()) // 2))


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.knob_rect = pygame.Rect(x, y - 5, 20, h + 10)
        self.min = min_val
        self.max = max_val
        self.val = initial_val
        self.dragging = False
        self.update_knob()

    def update_knob(self):
        knob_x = self.rect.x + (self.val - self.min) / (self.max - self.min) * self.rect.w
        self.knob_rect.x = knob_x - 10

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = event.pos[0]
            mouse_x = max(self.rect.x, min(self.rect.x + self.rect.w, mouse_x))
            self.val = self.min + (mouse_x - self.rect.x) / self.rect.w * (self.max - self.min)
            self.update_knob()
            return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, DARK_GREEN, self.knob_rect)
        val_text = font_small.render(str(int(self.val)), True, WHITE)
        screen.blit(val_text, (self.rect.x + self.rect.w + 10, self.rect.y - 5))


# Создаем элементы GUI
input_box = InputBox(250, 150, 300, 30, "ГРЯДЕТ АТТЕСТАЦИЯ!")
size_slider = Slider(250, 220, 300, 10, 10, 100, 48)
start_button = Button(350, 300, 100, 40, "Старт")
back_button = Button(20, 20, 80, 30, "Назад")

# Основные переменные
animation_active = False
TEXT = "ГРЯДЕТ АТТЕСТАЦИЯ"
FONT_SIZE = 48
text_surface = None
text_rect = None
mask = None
pixels = []
clock = pygame.time.Clock()


def init_animation():
    global text_surface, text_rect, mask, pixels

    # Создаем поверхность с текстом
    font = pygame.font.SysFont('Arial', FONT_SIZE, bold=True)
    text_surface = font.render(TEXT, True, GREEN)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Получаем маску текста
    mask = pygame.mask.from_surface(text_surface)

    # Создаем частицы
    pixels = []
    for x in range(text_rect.left, text_rect.right):
        for y in range(text_rect.top, text_rect.bottom):
            if mask.get_at((x - text_rect.left, y - text_rect.top)):
                start_x = random.randint(-100, -10)
                start_y = random.randint(0, HEIGHT)
                speed = random.uniform(1, 3)
                target_x, target_y = x, y
                pixels.append({
                    'x': start_x,
                    'y': start_y,
                    'speed': speed,
                    'target_x': target_x,
                    'target_y': target_y,
                    'reached': False,
                    'flying_out': False,
                    'fly_speed': random.uniform(1, 4)
                })


def run_animation():
    global animation_active

    animation_phase = "assembling"
    phase_start_time = 0
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        # Обработка кнопки "Назад"
        back_button.hover = back_button.rect.collidepoint(mouse_pos)
        if back_button.hover and mouse_clicked:
            running = False
            animation_active = False

        screen.fill(BLACK)

        current_time = time.time()

        if animation_phase == "assembling":
            all_reached = True

            for p in pixels:
                if not p['reached']:
                    if p['x'] < p['target_x']:
                        p['x'] += p['speed']
                    elif p['x'] > p['target_x']:
                        p['x'] = p['target_x']

                    if p['y'] < p['target_y']:
                        p['y'] += p['speed']
                    elif p['y'] > p['target_y']:
                        p['y'] = p['target_y']

                    if abs(p['x'] - p['target_x']) < 1 and abs(p['y'] - p['target_y']) < 1:
                        p['reached'] = True
                        p['x'] = p['target_x']
                        p['y'] = p['target_y']
                    else:
                        all_reached = False

                pygame.draw.rect(screen, PHASE1, (p['x'], p['y'], 2, 2))

            if all_reached:
                animation_phase = "holding"
                phase_start_time = current_time

        elif animation_phase == "holding":
            for p in pixels:
                pygame.draw.rect(screen, PHASE2, (p['x'], p['y'], 2, 2))

            if current_time - phase_start_time >= 1.0:
                animation_phase = "disassembling"
                for p in pixels:
                    p['reached'] = False
                    p['flying_out'] = True

        elif animation_phase == "disassembling":
            all_gone = True

            for p in pixels:
                if p['flying_out']:
                    p['x'] += p['fly_speed']

                    if p['x'] < WIDTH + 10:
                        all_gone = False
                    else:
                        p['flying_out'] = False

                if p['x'] < WIDTH + 10:
                    pygame.draw.rect(screen, PHASE3, (p['x'], p['y'], 2, 2))

            if all_gone:
                animation_phase = "waiting"
                phase_start_time = current_time

        elif animation_phase == "waiting":
            if current_time - phase_start_time >= 3.0:
                animation_phase = "assembling"
                for p in pixels:
                    p['x'] = random.randint(-100, -10)
                    p['y'] = random.randint(0, HEIGHT)
                    p['reached'] = False
                    p['flying_out'] = False

        # Рисуем кнопку "Назад"
        back_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# Основной цикл GUI
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

        # Обработка элементов GUI
        input_box.handle_event(event)
        if size_slider.handle_event(event):
            FONT_SIZE = int(size_slider.val)

    # Проверка нажатия кнопки "Старт"
    start_button.hover = start_button.rect.collidepoint(mouse_pos)
    if start_button.hover and mouse_clicked:
        TEXT = input_box.text if input_box.text else "ИИ ТЕХНОЛОГИИ"
        init_animation()
        animation_active = True
        run_animation()

    screen.fill(BLACK)

    if not animation_active:
        # Рисуем интерфейс настроек
        title = font_large.render("Настройки анимации", True, GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        text_label = font_medium.render("Текст:", True, WHITE)
        screen.blit(text_label, (50, 155))
        input_box.draw(screen)

        size_label = font_medium.render("Размер шрифта:", True, WHITE)
        screen.blit(size_label, (50, 215))
        size_slider.draw(screen)

        start_button.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()