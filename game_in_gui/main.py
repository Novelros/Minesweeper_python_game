import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from time import time


class MinesweeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Сапёр")  # названия окна для игры сапер

        # Настройки игры
        self.grid_size = 9
        self.max_bombs = 80
        self.min_bombs = 1
        self.default_bombs = 10
        self.bomb_count = self.default_bombs

        # Состояние игры
        self.flags = set()
        self.correct_flags = set()
        self.first_click = True
        self.game_started = False
        self.start_time = 0

        # Элементы интерфейса (таймер)
        self.timer_label = None
        self.buttons = []

        # Инициализация интерфейса
        self.create_menu()
        self.create_game_interface()
        self.init_game()

    def create_menu(self):
        """Создает меню игры"""
        menubar = tk.Menu(self.root)

        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.start_new_game)
        game_menu.add_command(label="Настройки", command=self.change_settings)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Игра", menu=game_menu)

        self.root.config(menu=menubar)

    def create_game_interface(self):
        """Создает игровой интерфейс (таймер и поле)"""
        # Создаем таймер
        self.timer_label = tk.Label(
            self.root,
            text="Время: 0 сек",
            font=('Calibri', 12)
        )
        self.timer_label.grid(row=0, column=0, columnspan=self.grid_size, sticky="ew")

        # Создаем кнопки для клеток
        self.create_buttons()

    def init_game(self):
        """Инициализирует новую игру"""
        self.game_started = False
        self.first_click = True
        self.flags = set()
        self.correct_flags = set()

        # Инициализация карт
        self.hidden_map = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.mines = set()
        self.player_map = [['-' for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Обновляем интерфейс
        self.update_timer()
        self.update_buttons()

    def count_adjacent_mines(self, row, col):
        """Считает количество мин вокруг указанной клетки"""
        count = 0
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if (0 <= r < self.grid_size and 0 <= c < self.grid_size and
                        self.hidden_map[r][c] == 'M'):
                    count += 1
        return count

    def place_mines(self, first_row, first_col):
        """Размещает мины на поле, избегая первой клетки и соседей"""
        # Определяем безопасную зону вокруг первого клика
        safe_zone = set()
        for r in range(first_row - 1, first_row + 2):
            for c in range(first_col - 1, first_col + 2):
                if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                    safe_zone.add((r, c))

        # Размещаем мины
        self.mines = set()
        while len(self.mines) < self.bomb_count:
            r, c = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            if (r, c) not in safe_zone:
                self.mines.add((r, c))
                self.hidden_map[r][c] = 'M'

        # Заполняем числами (количество мин вокруг)
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.hidden_map[r][c] != 'M':
                    count = self.count_adjacent_mines(r, c)
                    if count > 0:
                        self.hidden_map[r][c] = str(count)

    def create_buttons(self):
        """Создает кнопки игрового поля"""

        # Создаем новые кнопки
        self.buttons = []
        for row in range(self.grid_size):
            button_row = []
            for col in range(self.grid_size):
                btn = tk.Button(
                    self.root,
                    text=' ',
                    width=3,
                    height=1,
                    font=('Calibri', 12, 'bold'),
                    command=lambda r=row, c=col: self.on_left_click(r, c)
                )
                btn.bind('<Button-3>', lambda event, r=row, c=col: self.on_right_click(r, c))
                btn.grid(row=row + 1, column=col, sticky='nsew')  # +1 чтобы пропустить строку с таймером
                button_row.append(btn)
            self.buttons.append(button_row)

    def start_game_timer(self):
        """Запускает таймер игры"""
        self.game_started = True
        self.start_time = time()
        self.update_timer()

    def update_timer(self):
        """Обновляет отображение таймера"""
        if self.game_started:
            elapsed = int(time() - self.start_time)
            self.timer_label.config(text=f"Время: {elapsed} сек")
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Время: 0 сек")

    def on_left_click(self, row, col):
        """Обрабатывает левый клик мыши (открытие клетки)"""
        if (row, col) in self.flags:  # Не открываем помеченные флажками клетки
            return

        if self.first_click:
            self.place_mines(row, col)
            self.start_game_timer()
            self.first_click = False

        if self.hidden_map[row][col] == 'M':
            self.game_over(False)
            return

        self.reveal_cells(row, col)
        self.update_buttons()

        if self.check_win():
            self.game_over(True)

    def on_right_click(self, row, col):
        """Обрабатывает правый клик мыши (установка/снятие флага)"""
        if self.player_map[row][col] != '-':  # Не ставим флаги на открытые клетки
            return

        if (row, col) in self.flags:
            self.flags.remove((row, col))
            if (row, col) in self.correct_flags:
                self.correct_flags.remove((row, col))
        else:
            self.flags.add((row, col))
            if self.hidden_map[row][col] == 'M':
                self.correct_flags.add((row, col))

        self.update_buttons()

        # Проверяем победу (все мины правильно помечены)
        if (len(self.correct_flags) == self.bomb_count and
                len(self.flags) == self.bomb_count):
            self.game_over(True)

    def reveal_cells(self, row, col):
        """Рекурсивно открывает клетки"""
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size) or self.player_map[row][col] != '-':
            return

        self.player_map[row][col] = self.hidden_map[row][col]

        # Если клетка пустая, открываем соседей
        if self.hidden_map[row][col] == ' ':
            for r in range(row - 1, row + 2):
                for c in range(col - 1, col + 2):
                    if r != row or c != col:  # Не проверяем саму клетку
                        self.reveal_cells(r, c)

    def update_buttons(self):
        """Обновляет внешний вид кнопок в соответствии с состоянием игры"""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) in self.flags:
                    self.buttons[row][col].config(text='🚩', fg='red', bg='SystemButtonFace')
                elif self.player_map[row][col] == '-':
                    self.buttons[row][col].config(text=' ', bg='SystemButtonFace')
                else:
                    cell = self.player_map[row][col]
                    self.buttons[row][col].config(text=cell, bg='light gray')

                    # Разные цвета для цифр
                    if cell.isdigit():
                        num = int(cell)
                        colors = ['', 'blue', 'green', 'red', 'dark blue',
                                  'brown', 'teal', 'black', 'gray']
                        self.buttons[row][col].config(fg=colors[num])

    def check_win(self):
        """Проверяет условия победы"""
        # Все безопасные клетки должны быть открыты
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.hidden_map[row][col] != 'M' and self.player_map[row][col] == '-':
                    return False
        return True

    def game_over(self, won):
        """Обрабатывает завершение игры"""
        self.game_started = False

        # Показываем все мины
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.hidden_map[row][col] == 'M':
                    self.buttons[row][col].config(
                        text='💣',
                        bg='light green' if won else 'orange'
                    )

        # Отключаем все кнопки
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.buttons[row][col].config(state='disabled')

        # Показываем сообщение
        if won:
            elapsed = int(time() - self.start_time)
            messagebox.showinfo("Победа!", f"Поздравляем! Вы выиграли за {elapsed} секунд!")
        else:
            messagebox.showinfo("Поражение", "Вы наступили на мину!")

    def start_new_game(self):
        """Начинает новую игру"""
        self.init_game()

    def change_settings(self):
        """Изменяет настройки игры (количество мин)"""
        bombs = simpledialog.askinteger(
            "Количество мин",
            f"Введите количество мин ({self.min_bombs}-{self.max_bombs}):",
            parent=self.root,
            minvalue=self.min_bombs,
            maxvalue=self.max_bombs,
            initialvalue=self.bomb_count
        )

        if bombs is not None:  # Если пользователь не нажал "Отмена"
            self.bomb_count = bombs
            self.start_new_game()


if __name__ == "__main__":
    root = tk.Tk()
    game = MinesweeperGUI(root)
    root.mainloop()
