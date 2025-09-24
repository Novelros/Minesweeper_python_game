import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
from renderer import Renderer


class Minesweeper3D:
    def __init__(self, settings):
        self.settings = settings
        self.grid_size = settings['grid_size']
        self.mine_count = settings['mine_count']

        self.last_arrow_time = 0
        self.width, self.height =  (1280, 1024)


        # Создаем OpenGL окно
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Minesweeper - Use WASD, Arrows, Q/E, Space, F, R")

        # Инициализация рендерера
        self.renderer = Renderer(self.width, self.height, self.grid_size, self.settings['lighting_enabled'])
        # Инициализация игры
        self.init_game()

    def init_game(self):
        """Инициализация или сброс игрового состояния"""
        # Создаем сетку клеток с начальными значениями
        self.grid = [[{'mine': False, 'revealed': False, 'flagged': False, 'adjacent': 0}
                      for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Позиция курсора (начинаем в центре)
        self.cursor_pos = [self.grid_size // 2, self.grid_size // 2]

        # Состояние игры
        self.game_over = False
        self.win = False
        self.first_click = True
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0


        # Словарь для отслеживания состояния клавиш
        self.keys_pressed = {
            pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False,
            pygame.K_q: False, pygame.K_e: False, pygame.K_UP: False, pygame.K_DOWN: False,
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_ESCAPE: False
        }

    def place_mines(self, safe_x, safe_y):
        """
                Размещение мин на поле с гарантией безопасной зоны вокруг первого клика

                Args:
                    safe_x, safe_y: Координаты безопасной клетки (первый клик)
        """
        mines_placed = 0
        safe_cells = set()

        # Создаем безопасную зону вокруг первого клика
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    safe_cells.add((nx, ny))

        # Размещаем мины
        while mines_placed < self.mine_count:
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            if (x, y) not in safe_cells and not self.grid[y][x]['mine']:
                self.grid[y][x]['mine'] = True
                mines_placed += 1

                # Обновляем счетчики соседних мин
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                            self.grid[ny][nx]['adjacent'] += 1

    def reveal_cell(self, x, y):
        """Вскрытие клетки и рекурсивное вскрытие соседей"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return

        cell = self.grid[y][x]
        if cell['revealed'] or cell['flagged']:
            return

        # Первый клик - гарантируем безопасность
        if self.first_click:
            self.first_click = False
            self.place_mines(x, y)

        cell['revealed'] = True

        # Проверка на мину
        if cell['mine']:
            self.game_over = True
            # Показываем все мины при проигрыше
            for row in self.grid:
                for cell_data in row:
                    if cell_data['mine']:
                        cell_data['revealed'] = True
            return

        # Рекурсивное вскрытие пустых клеток
        if cell['adjacent'] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        self.reveal_cell(x + dx, y + dy)

    def check_win(self):
        """Проверка условия победы"""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell = self.grid[y][x]
                if not cell['mine'] and not cell['revealed']:
                    return False
        self.win = True
        return True

    def handle_input(self):
        """Обработка ввода с клавиатуры"""
        current_time = pygame.time.get_ticks()

        # Управление камерой
        speed = 2.0
        if self.keys_pressed[pygame.K_w]:
            self.renderer.camera_rotation_x = (self.renderer.camera_rotation_x - speed) % 360
        if self.keys_pressed[pygame.K_s]:
            self.renderer.camera_rotation_x = (self.renderer.camera_rotation_x + speed) % 360
        if self.keys_pressed[pygame.K_a]:
            self.renderer.camera_rotation_y = (self.renderer.camera_rotation_y - speed) % 360
        if self.keys_pressed[pygame.K_d]:
            self.renderer.camera_rotation_y = (self.renderer.camera_rotation_y + speed) % 360

        # Приближение/отдаление
        if self.keys_pressed[pygame.K_q]:
            self.renderer.camera_distance = min(-5, self.renderer.camera_distance + speed * 0.5)
        if self.keys_pressed[pygame.K_e]:
            self.renderer.camera_distance = max(-40, self.renderer.camera_distance - speed * 0.5)

        # Управление курсором
        if self.keys_pressed[pygame.K_UP] and current_time - self.last_arrow_time > 150:
            self.cursor_pos[1] = min(self.grid_size - 1, self.cursor_pos[1] + 1)
            self.last_arrow_time = current_time
        if self.keys_pressed[pygame.K_DOWN] and current_time - self.last_arrow_time > 150:
            self.cursor_pos[1] = max(0, self.cursor_pos[1] - 1)
            self.last_arrow_time = current_time
        if self.keys_pressed[pygame.K_LEFT] and current_time - self.last_arrow_time > 150:
            self.cursor_pos[0] = max(0, self.cursor_pos[0] - 1)
            self.last_arrow_time = current_time
        if self.keys_pressed[pygame.K_RIGHT] and current_time - self.last_arrow_time > 150:
            self.cursor_pos[0] = min(self.grid_size - 1, self.cursor_pos[0] + 1)
            self.last_arrow_time = current_time

    def run(self):
        """Главный игровой цикл"""
        clock = pygame.time.Clock()
        running = True

        while running:
            # Обновление времени
            current_time = pygame.time.get_ticks()
            if not self.game_over and not self.win:
                self.elapsed_time = (current_time - self.start_time) // 1000

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in self.keys_pressed:
                        self.keys_pressed[event.key] = True

                    # Выход в меню по ESC
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Перезапуск игры
                    if (self.game_over or self.win) and event.key == pygame.K_r:
                        self.init_game()
                        continue

                    # Игровые действия
                    if not self.game_over and not self.win:
                        if event.key == pygame.K_SPACE:
                            x, y = self.cursor_pos
                            self.reveal_cell(x, y)
                            if not self.game_over and not self.first_click:
                                self.check_win()
                        elif event.key == pygame.K_f:
                            x, y = self.cursor_pos
                            if not self.grid[y][x]['revealed']:
                                self.grid[y][x]['flagged'] = not self.grid[y][x]['flagged']

                elif event.type == pygame.KEYUP:
                    if event.key in self.keys_pressed:
                        self.keys_pressed[event.key] = False

            # Обработка непрерывного ввода
            self.handle_input()

            # Очистка экрана
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Обновление камеры
            self.renderer.update_camera()

            # Отрисовка игрового поля
            self.renderer.draw_grid(self.grid, self.cursor_pos, self.grid_size)

            # Отображение интерфейса
            self.draw_interface()

            # Обновление дисплея
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def draw_interface(self):
        """Отрисовка интерфейса поверх игры"""
        # Статус игры
        if self.game_over:
            self.renderer.draw_text("GAME OVER! Press R to restart", self.width // 1.5, self.height // 2, background=True)
        elif self.win:
            self.renderer.draw_text("YOU WIN! Press R to restart", self.width // 1.5, self.height // 2, background=True)

        # Время и мины (с фоном)
        time_text = f"Time: {self.elapsed_time}s"
        mines_text = f"Mines: {self.mine_count}"
        grid_text = f"Grid: {self.grid_size}x{self.grid_size}"

        # Вычисляем относительные отступы от краев экрана
        margin_x = self.width * 0.05  # 5% от ширины экрана
        margin_y = self.height * 0.2  # 5% от высоты экрана
        text_spacing = 40 + self.width * 0.05 # Фиксированный интервал между строками

        # Левая колонка (информация)
        self.renderer.draw_text(time_text, margin_x, margin_y, background=True)
        self.renderer.draw_text(mines_text, margin_x, margin_y + text_spacing, background=True)

        # Правая колонка (информация) - отступаем от правого края
        right_margin_x = self.width - 200  # Фиксированная ширина текста или можно сделать относительной
        self.renderer.draw_text(grid_text, right_margin_x, margin_y, background=True)

        # Подсказки управления (нижний левый угол)
        controls_text = "WASD: Camera  Q/E: Zoom  Arrows: Move  Space: Reveal  F: Flag"
        self.renderer.draw_text(controls_text, margin_x, self.height - margin_y, background=True)

        # Клавиши управления (нижний правый угол)
        control_keys = "R: Restart  ESC: Menu"
        right_controls_x = self.width - 200
        self.renderer.draw_text(control_keys, right_controls_x, self.height - margin_y, background=True)
