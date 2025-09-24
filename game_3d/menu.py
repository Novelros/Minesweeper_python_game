import pygame


class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        # Шрифты - подбираем на глаз
        self.big_font = pygame.font.SysFont('Times New Roman', 50)
        self.normal_font = pygame.font.SysFont('Times New Roman', 35)

        # Настройки по умолчанию - стандартные значения
        self.grid_size = 10  # Размер поля
        self.mine_count = 15  # Мины для начала
        self.lighting_on = True  # Освещение включено

        # Вычисляем позиции относительно размера экрана
        self.middle_x = self.width // 2  # Центр экрана

        # Высоты элементов - отступаем от верха пропорционально
        self.title_y = self.height // 8  # Заголовок в верхней части
        self.first_slider_y = self.height // 4  # Первый слайдер чуть ниже
        self.slider_spacing = self.height // 10  # Расстояние между слайдерами
        self.toggle_y = self.first_slider_y + self.slider_spacing * 2  # Переключатель после двух слайдеров
        self.button_y = self.toggle_y + self.slider_spacing  # Кнопка внизу

        # Ширины элементов - пропорционально ширине экрана
        self.slider_length = self.width // 4  # Слайдер занимает четверть экрана
        self.btn_width = self.width // 5  # Кнопка поменьше
        self.btn_height = 50  # Высота кнопки стандартная

        # Для удобства - отступ слайдера от центра
        self.slider_offset_x = self.width // 9

        # Состояния перетаскивания
        self.grid_dragging = False
        self.mines_dragging = False

        # Флаг работы меню
        self.running = True

    def run(self):
        """Главный цикл - открыт пока пользователь не выберет настройки"""
        while self.running:
            # Текущая позиция мыши для обработки hover эффектов
            # P.S. hover-эффект — это изменение вида элемента, когда пользователь наводит на него курсор мыши
            mouse_pos = pygame.mouse.get_pos()

            # Разбираем все события которые накопились
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # Выход из игры если закрыли окно

                # Нажатие кнопки мыши - возможно начало перетаскивания или клик
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(mouse_pos)

                # Отпустили кнопку - заканчиваем перетаскивание
                if event.type == pygame.MOUSEBUTTONUP:
                    self.grid_dragging = False
                    self.mines_dragging = False

                # Клавиша ESC - выход в меню
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None

            # Если тащим слайдер - обновляем его значение
            if self.grid_dragging or self.mines_dragging:
                self.update_slider_values(mouse_pos)

            # Рисуем все элементы интерфейса
            self.draw_interface()
            pygame.display.flip()

            # Не грузим процессор - ждем немного
            pygame.time.delay(30)

        # Возвращаем настройки когда пользователь нажал "Начать игру"
        return self.get_settings()

    def handle_mouse_down(self, mouse_pos):
        """Обрабатываем клик мыши - проверяем куда попали"""
        x, y = mouse_pos

        # Позиция начала слайдера (левый край)
        slider_start_x = self.middle_x - self.slider_offset_x

        # Вычисляем где должна быть ручка слайдера размера сетки
        grid_handle_x = slider_start_x + (self.grid_size - 5) * (self.slider_length / 15)

        # Область ручки - немного расширяем для удобства клика
        handle_left = grid_handle_x - 15
        handle_right = grid_handle_x + 15
        handle_top = self.first_slider_y - 5
        handle_bottom = self.first_slider_y + 25

        # Проверяем попали ли в ручку слайдера размера сетки
        if (handle_left < x < handle_right and handle_top < y < handle_bottom):
            self.grid_dragging = True

        # Аналогично для слайдера количества мин (он ниже)
        mines_handle_x = slider_start_x + (self.mine_count - 5) * (self.slider_length / 95)
        mines_handle_top = self.first_slider_y + self.slider_spacing - 5
        mines_handle_bottom = mines_handle_top + 30

        if (mines_handle_x - 15 < x < mines_handle_x + 15 and
                mines_handle_top < y < mines_handle_bottom):
            self.mines_dragging = True

        # Проверяем клик по переключателю освещения
        toggle_rect = pygame.Rect(self.middle_x - 70, self.toggle_y, 140, 40)
        if toggle_rect.collidepoint(mouse_pos):
            self.lighting_on = not self.lighting_on  # Переключаем состояние

        # Проверяем клик по кнопке "Начать игру"
        start_rect = pygame.Rect(self.middle_x - self.btn_width // 2, self.button_y,
                                 self.btn_width, self.btn_height)
        if start_rect.collidepoint(mouse_pos):
            self.running = False  # Заканчиваем работу меню

    def update_slider_values(self, mouse_pos):
        """Обновляем значения когда тащим слайдер"""
        x, y = mouse_pos
        slider_start_x = self.middle_x - self.slider_offset_x

        # Обновляем размер сетки если тащим первый слайдер
        if self.grid_dragging:
            # Вычисляем относительное положение мыши на слайдере
            relative_x = x - slider_start_x
            # Ограничиваем в пределах слайдера
            relative_x = max(0, min(relative_x, self.slider_length))
            # Пересчитываем в значение от 5 до 20
            self.grid_size = 5 + int(relative_x / self.slider_length * 15)

        # Аналогично для количества мин
        if self.mines_dragging:
            relative_x = x - slider_start_x
            relative_x = max(0, min(relative_x, self.slider_length))
            self.mine_count = 5 + int(relative_x / self.slider_length * 95)

            # Защита от дурака - не может быть мин больше чем клеток (минус 9 для безопасной зоны)
            max_possible_mines = self.grid_size * self.grid_size - 9
            if self.mine_count > max_possible_mines:
                self.mine_count = max_possible_mines

    def draw_interface(self):
        """Рисуем весь интерфейс меню"""
        # Заливаем фон темно-синим цветом
        self.screen.fill((40, 40, 80))

        # Заголовок игры по центру сверху
        title = self.big_font.render("Сапер 3D", True, (255, 255, 200))
        title_rect = title.get_rect(center=(self.middle_x, self.title_y))
        self.screen.blit(title, title_rect)

        # Рисуем два слайдера - для размера поля и количества мин
        self.draw_slider("Размер поля:", self.grid_size, self.first_slider_y,
                         f"{self.grid_size}×{self.grid_size}")
        self.draw_slider("Количество мин:", self.mine_count,
                         self.first_slider_y + self.slider_spacing, str(self.mine_count))

        # Переключатель освещения
        self.draw_lighting_toggle()

        # Кнопка начала игры
        self.draw_start_button()

    def draw_slider(self, label, value, y_pos, value_text):
        """Рисуем один слайдер с меткой и значением"""
        # Начало слайдера (левый край)
        slider_start_x = self.middle_x - self.slider_offset_x

        # Метка слева от слайдера
        label_surface = self.normal_font.render(label, True, (255, 255, 255))
        # Размещаем метку слева от слайдера с выравниванием по базовой линии
        self.screen.blit(label_surface, (slider_start_x - label_surface.get_width() - 20, y_pos))

        # Значение справа от слайдера
        value_surface = self.normal_font.render(value_text, True, (255, 255, 200))
        self.screen.blit(value_surface, (slider_start_x + self.slider_length + 10, y_pos))

        # Фоновая полоса слайдера
        pygame.draw.rect(self.screen, (80, 80, 120),
                         (slider_start_x, y_pos + 15, self.slider_length, 8))

        # Заполненная часть - показывает текущее значение
        if value > 5:
            # Вычисляем ширину заполненной части в зависимости от типа слайдера
            if "Размер" in label:
                fill_width = (value - 5) * (self.slider_length / 15)
            else:
                fill_width = (value - 5) * (self.slider_length / 95)

            pygame.draw.rect(self.screen, (0, 120, 220),
                             (slider_start_x, y_pos + 15, fill_width, 8))

        # Ручка слайдера - кружок по текущей позиции
        if "Размер" in label:
            handle_x = slider_start_x + (value - 5) * (self.slider_length / 15)
        else:
            handle_x = slider_start_x + (value - 5) * (self.slider_length / 95)

        pygame.draw.circle(self.screen, (255, 255, 255), (int(handle_x), y_pos + 19), 12)

    def draw_lighting_toggle(self):
        """Рисуем переключатель освещения"""
        # Позиция переключателя - по центру
        toggle_x = self.middle_x - 70
        toggle_y = self.toggle_y

        # Метка слева
        label = self.normal_font.render("Освещение:", True, (255, 255, 255))
        self.screen.blit(label, (toggle_x - label.get_width() - 30, toggle_y))

        # Сам переключатель - зеленный если включено, красный если выключено
        toggle_color = (50, 200, 50) if self.lighting_on else (200, 50, 50)
        pygame.draw.rect(self.screen, toggle_color,
                         (toggle_x, toggle_y, 140, 40), border_radius=20)

        # Текст на переключателе
        state_text = "ВКЛ" if self.lighting_on else "ВЫКЛ"
        text_surface = self.normal_font.render(state_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(toggle_x + 70, toggle_y + 20))
        self.screen.blit(text_surface, text_rect)

    def draw_start_button(self):
        """Рисуем кнопку начала игры"""
        # Позиция кнопки - по центру внизу
        btn_x = self.middle_x - self.btn_width // 2
        btn_y = self.button_y

        # Цвет кнопки - зеленый, можно добавить hover эффект потом
        button_color = (30, 150, 30)

        # Рисуем саму кнопку со скругленными углами
        pygame.draw.rect(self.screen, button_color,
                         (btn_x, btn_y, self.btn_width, self.btn_height), border_radius=10)
        # Обводка кнопки
        pygame.draw.rect(self.screen, (200, 200, 200),
                         (btn_x, btn_y, self.btn_width, self.btn_height), 2, border_radius=10)

        # Текст на кнопке
        text_surface = self.normal_font.render("Начать игру", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(btn_x + self.btn_width // 2, btn_y + self.btn_height // 2))
        self.screen.blit(text_surface, text_rect)

    def get_settings(self):
        """Возвращаем выбранные пользователем настройки"""
        return {
            'grid_size': self.grid_size,
            'mine_count': self.mine_count,
            'lighting_enabled': self.lighting_on
        }