from OpenGL.GL import *
from OpenGL.GLU import *
import pygame


class Renderer:
    def __init__(self, width, height, grid_size, lighting_enabled=True):
        """
        Инициализация рендерера для 3D-визуализации игрового поля

        Args:
            width: Ширина окна отображения
            height: Высота окна отображения
            grid_size: Размер игрового поля (количество клеток)
            lighting_enabled: Флаг включения освещения (по умолчанию True)
        """
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cell_size = 2  # Размер одной клетки в 3D-пространстве
        self.depth = 0.7  # Глубина клеток

        # Создание квадриков для отрисовки 3D-объектов (мины и шипы)
        self.mine_quadric = gluNewQuadric()
        self.spike_quadric = gluNewQuadric()

        # Параметры камеры
        self.camera_distance = -30  # Дистанция камеры от центра сцены
        self.camera_rotation_x = 30  # Угол поворота по оси X (наклон)
        self.camera_rotation_y = -45  # Угол поворота по оси Y (вращение)

        # Настройка OpenGL
        gluPerspective(60, (width / height), 0.1, 75.0)  # Перспективная проекция
        glTranslatef(0.0, 0.0, self.camera_distance)  # Позиционирование камеры
        glRotatef(self.camera_rotation_x, 1, 0, 0)  # Поворот по оси X
        glRotatef(self.camera_rotation_y, 0, 1, 0)  # Поворот по оси Y
        glEnable(GL_DEPTH_TEST)  # Включение теста глубины
        glEnable(GL_COLOR_MATERIAL)  # Включение цветовых материалов

        # Настройка освещения если включено
        if lighting_enabled:
            self.setup_lighting()

        # Инициализация шрифта для текстовых надписей
        pygame.font.init()
        self.font = pygame.font.SysFont('Times New Roman', 24)

    def setup_lighting(self):
        """
        Настройка системы освещения сцены с двумя источниками света

        Создает основное и дополнительное освещение для лучшей визуализации 3D-объектов
        """
        glEnable(GL_LIGHTING)  # Включение системы освещения
        glEnable(GL_LIGHT0)  # Активация первого источника света
        glEnable(GL_LIGHT1)  # Активация второго источника света

        # Расчет половины размера игрового поля для позиционирования света
        field_half_size = (self.grid_size * self.cell_size) / 2

        # Настройка первого источника света (верхний-правый)
        glLightfv(GL_LIGHT0, GL_POSITION, (field_half_size, -field_half_size, 10, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))  # Рассеянный свет
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))  # Фоновое освещение

        # Настройка второго источника света (спереди-сверху)
        glLightfv(GL_LIGHT1, GL_POSITION, (0, 0, 100, 1))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))  # Рассеянный свет
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.2, 0.2, 0.2, 1))  # Фоновое освещение

    def update_camera(self):
        """
        Обновление позиции и ориентации камеры в 3D-пространстве

        Сбрасывает матрицу преобразований и применяет текущие параметры камеры
        """
        glLoadIdentity()  # Сброс матрицы преобразований
        gluPerspective(60, (self.width / self.height), 0.1, 75.0)  # Установка перспективы
        glTranslatef(0.0, 0.0, self.camera_distance)  # Перемещение камеры
        glRotatef(self.camera_rotation_x, 1, 0, 0)  # Поворот по оси X (вертикальный наклон)
        glRotatef(self.camera_rotation_y, 0, 1, 0)  # Поворот по оси Y (горизонтальное вращение)

    def draw_cube(self, x, y, z, color):
        """
            Метод создает и отрисовывает трехмерный куб:

            Args:
                x, y, z - координаты переднего верхнего угла куба в 3D-пространстве
                color - цвет заливки граней куба
        """
        vertices = [
            [x, y, z], [x + self.cell_size, y, z], [x + self.cell_size, y + self.cell_size, z],
            [x, y + self.cell_size, z], # Передняя грань (ближняя к наблюдателю)
            [x, y, z - self.depth], [x + self.cell_size, y, z - self.depth],
            [x + self.cell_size, y + self.cell_size, z - self.depth], [x, y + self.cell_size, z - self.depth]
            # Задняя грань (дальняя от наблюдателя)
        ]

        faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]]

        glBegin(GL_QUADS)
        glColor3fv(color)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

    def draw_grid(self, grid, cursor_pos, grid_size):
        """
        Отрисовка игрового поля с клетками, минами, флагами и курсором

        Args:
            grid: Двумерный массив клеток игрового поля
            cursor_pos: Текущая позиция курсора (x, y)
            grid_size: Размер игрового поля
        """
        # Смещение для центрирования поля относительно начала координат
        offset_x = -grid_size * self.cell_size / 2
        offset_y = -grid_size * self.cell_size / 2

        # Отрисовка всех клеток поля
        for y in range(grid_size):
            for x in range(grid_size):
                cell_x = offset_x + x * self.cell_size
                cell_y = offset_y + y * self.cell_size
                cell = grid[y][x]

                # Выбор цвета клетки в зависимости от состояния
                if cell['revealed']:
                    color = (1, 0, 0) if cell['mine'] else (0.8, 0.8, 0.8)  # Красный для мин, серый для пустых
                else:
                    color = (0.4, 0.4, 0.8)  # Синий для неоткрытых клеток

                # Отрисовка базового куба клетки
                self.draw_cube(cell_x, cell_y, 0, color)

                # Отрисовка содержимого открытых клеток
                if cell['revealed']:
                    if cell['mine']:
                        self.draw_mine(cell_x, cell_y)  # Мина
                    elif cell['adjacent'] > 0:
                        self.draw_number(cell_x, cell_y, cell['adjacent'])  # Число соседних мин
                elif cell['flagged']:
                    self.draw_flag(cell_x, cell_y)  # Флаг

        # Отрисовка курсора (желтая рамка поверх клетки)
        cursor_x = offset_x + cursor_pos[0] * self.cell_size
        cursor_y = offset_y + cursor_pos[1] * self.cell_size
        glColor3f(1, 1, 0)  # Желтый цвет
        glBegin(GL_LINE_LOOP)
        glVertex3f(cursor_x, cursor_y, 0.1)  # Лево-низ
        glVertex3f(cursor_x + self.cell_size, cursor_y, 0.1)  # Право-низ
        glVertex3f(cursor_x + self.cell_size, cursor_y + self.cell_size, 0.1)  # Право-верх
        glVertex3f(cursor_x, cursor_y + self.cell_size, 0.1)  # Лево-верх
        glEnd()

    def draw_text(self, text, x, y, background=False):
        """
        Отрисовка 2D-текста поверх 3D-сцены с опциональным фоном

        Args:
            text: Текст для отображения
            x, y: Координаты левого верхнего угла
            background: Добавлять ли полупрозрачный фон
        """
        # Сохраняем текущие матрицы и настройки
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Отключаем глубину и освещение для 2D
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # Включаем blending для прозрачности
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Рендерим текст
        text_surface = self.font.render(text, True, (0, 255, 0, 255))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()

        try:
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            glRasterPos2f(x, y)

            # Устанавливаем цвет текста (белый)
            glColor4f(0 , 0, 0, 5)

            glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        except Exception as e:
            print(f"Error drawing text: {e}")

        # Восстанавливаем настройки
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_number(self, x, y, number):
        """
                Рисование 3D-числа, показывающего количество мин вокруг

                Args:
                    x, y: Координаты клетки
                    number: Число для отображения (1-8)
                """
        if number == 0:
            return  # Не рисуем 0

        # Цвета для разных чисел (как в классическом сапере)
        colors = [
            (0, 0, 255),  # 1 - синий
            (0, 255, 0),  # 2 - зеленый
            (255, 0, 0),  # 3 - красный
            (0, 0, 0.5),  # 4 - темно-синий
            (0.5, 0, 0),  # 5 - темно-красный
            (0, 0.5, 0.5),  # 6 - бирюзовый
            (0, 0, 0),  # 7 - черный
            (0.5, 0.5, 0.5)  # 8 - серый
        ]

        # Выбираем цвет в зависимости от числа
        color = colors[number - 1] if number <= 8 else (1, 0, 1)  # Фиолетовый для чисел >8

        # Сохраняем текущую матрицу преобразований
        glPushMatrix()

        # Перемещаемся в центр клетки и немного выше поверхности
        glTranslatef(x + self.cell_size / 2, y + self.cell_size / 2, 0.1)

        # Масштабируем текст до нужного размера
        glScalef(0.003, 0.003, 0.003)  # Отрицательный масштаб по X исправляет зеркальность

        # Центрируем текст (компенсируем отрицательное масштабирование)
        text_width = len(str(number)) * 80  # Примерная ширина текста
        glTranslatef(-text_width / 2, -150, 0)  # Центрируем и опускаем немного вниз
        glColor3fv(color)

        # Рисуем число с помощью встроенных символов OpenGL
        # (заменяем GLUT_STROKE_ROMAN на базовые примитивы)
        self.draw_text_primitive(str(number))

        # Восстанавливаем предыдущую матрицу
        glPopMatrix()

    def draw_text_primitive(self, text):
        """
        Рисование текста с помощью базовых примитивов OpenGL
        Простая реализация для цифр 0-9

        Args:
            text: Текст для отображения
        """
        for char in text:
            if char == '1':
                glBegin(GL_LINES)
                glVertex2f(40, -150)
                glVertex2f(40, 150)
                glEnd()
                glTranslatef(100, 0, 0)


            elif char == '2':
                glBegin(GL_LINE_STRIP)
                glVertex2f(10, 150)  # Левая нижняя
                glVertex2f(90, 150)  # Правая нижняя
                glVertex2f(90, 0)  # Правая середина
                glVertex2f(10, 0)  # Левая середина
                glVertex2f(10, -150)  # Левая верхняя
                glVertex2f(90, -150)  # Правая верхняя
                glEnd()
                glTranslatef(120, 0, 0)

            elif char == '3':
                glBegin(GL_LINE_STRIP)
                glVertex2f(10, -150)
                glVertex2f(90, -150)
                glVertex2f(90, 0)
                glVertex2f(10, 0)
                glVertex2f(90, 0)
                glVertex2f(90, 150)
                glVertex2f(10, 150)
                glEnd()
                glTranslatef(120, 0, 0)

            elif char == '4':
                glBegin(GL_LINES)
                glVertex2f(10, 150)
                glVertex2f(10, 0)  # Левая вертикаль
                glVertex2f(10, 0)
                glVertex2f(90, 0)  # Горизонталь
                glVertex2f(90, 150)
                glVertex2f(90, -150)  # Правая вертикаль
                glEnd()
                glTranslatef(120, 0, 0)

            elif char == '5':
                glBegin(GL_LINE_STRIP)
                glVertex2f(90, 150)
                glVertex2f(10, 150)
                glVertex2f(10, 0)
                glVertex2f(90, 0)
                glVertex2f(90, -150)
                glVertex2f(10, -150)
                glEnd()
                glTranslatef(120, 0, 0)

            elif char == '6':
                glBegin(GL_LINE_STRIP)
                glVertex2f(90, -150)
                glVertex2f(10, -150)
                glVertex2f(10, 150)
                glVertex2f(90, 150)
                glVertex2f(90, 0)
                glVertex2f(10, 0)
                glEnd()
                glTranslatef(120, 0, 0)

            elif char == '7':
                glBegin(GL_LINE_STRIP)
                glVertex2f(10, 150)
                glVertex2f(90, 150)
                glVertex2f(90, -150)
                glEnd()
                glTranslatef(120, 0, 0)

            elif char == '8':
                glBegin(GL_LINE_LOOP)
                glVertex2f(10, -150)
                glVertex2f(90, -150)
                glVertex2f(90, 150)
                glVertex2f(10, 150)
                glEnd()
                glBegin(GL_LINES)
                glVertex2f(10, 0)
                glVertex2f(90, 0)
                glEnd()
                glTranslatef(120, 0, 0)

            elif char == '9':
                glBegin(GL_LINE_STRIP)
                glVertex2f(10, 150)
                glVertex2f(90, 150)
                glVertex2f(90, -150)
                glVertex2f(10, -150)
                glVertex2f(10, 0)
                glVertex2f(90, 0)
                glEnd()
                glTranslatef(120, 0, 0)
            else:
                # Для неизвестных символов просто сдвигаемся
                glTranslatef(100, 0, 0)

    def draw_flag(self, x, y):
        """
               Рисование 3D-флага для помеченных клеток

               Args:
                   x, y: Координаты клетки с флагом
               """
        glPushMatrix()
        glTranslatef(x + self.cell_size / 2, y + self.cell_size / 2, 0.1)

        # Рисуем флагшток (коричневый прямоугольник)
        glColor3f(0.5, 0.3, 0.1)
        glBegin(GL_QUADS)
        glVertex3f(-0.1, -0.4, 0)
        glVertex3f(0.1, -0.4, 0)
        glVertex3f(0.1, 0.4, 0)
        glVertex3f(-0.1, 0.4, 0)
        glEnd()

        # Рисуем флаг (красный треугольник)
        glColor3f(1, 0, 0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.1, 0.4, 0)  # Верх флагштока
        glVertex3f(0.1, 0.1, 0)  # Низ флага
        glVertex3f(0.5, 0.25, 0)  # Кончик флага
        glEnd()

        glPopMatrix()

    def draw_mine(self, x, y):
        """
        Рисование 3D-мины в виде сферы с шипами

        Args:
            x, y: Координаты клетки с миной
        """
        glPushMatrix()
        glTranslatef(x + self.cell_size / 2, y + self.cell_size / 2, 0.1)

        # Рисуем черную сферу (тело мины)
        glColor3f(0, 0, 0)
        gluSphere(self.mine_quadric, 0.3, 20, 20)

        # Рисуем серые шипы вокруг мины
        glColor3f(0.5, 0.5, 0.5)
        for i in range(8):
            glPushMatrix()
            glRotatef(45 * i, 0, 0, 1)
            glTranslatef(0.5, 0, 0)
            gluSphere(self.spike_quadric, 0.1, 10, 10)
            glPopMatrix()

        glPopMatrix()
