import random
import tkinter as tk
from tkinter import messagebox


class MinesweeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Сапёр")

        # Настройки по умолчанию
        self.size = 9
        self.bomb_count = 10
        self.flags = set()
        self.correct_flags = set()
        self.first_click = True

        # Создаем меню
        self.create_menu()

        # Инициализация игры
        self.init_game()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.new_game)
        game_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Игра", menu=game_menu)

        self.root.config(menu=menubar)

    def init_game(self):
        # Создаем игровое поле
        self.create_board()

        # Создаем кнопки для клеток
        self.create_buttons()

    def create_board(self):
        # Генерация карты с минами
        self.hidden_map = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.mines = set()

        # Карта, видимая игроку
        self.player_map = [['-' for _ in range(self.size)] for _ in range(self.size)]

        # Добавляем номера строк и столбцов
        self.display_map = [[' '] + list(range(1, self.size + 1))]
        for i in range(self.size):
            self.display_map.append([i + 1] + self.player_map[i])

    def place_mines(self, first_x, first_y):
        """Метод, который размещает мины, избегая первой нажатой клетки и соседей"""
        safe_zone = set()
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 0), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        for dx, dy in directions:
            nx, ny = first_x + dx, first_y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                safe_zone.add((nx, ny))

        while len(self.mines) < self.bomb_count:
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if (x, y) not in safe_zone:
                self.mines.add((x, y))
                self.hidden_map[x][y] = 'M'

        # Заполняем числами (количество мин вокруг)
        for x in range(self.size):
            for y in range(self.size):
                if self.hidden_map[x][y] != 'M':
                    count = 0
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if self.hidden_map[nx][ny] == 'M':
                                count += 1
                    if count > 0:
                        self.hidden_map[x][y] = str(count)

    def create_buttons(self):
        # Удаляем старые кнопки, если они есть
        for widget in self.root.grid_slaves():
            widget.destroy()

        # Создаем кнопки для каждой клетки
        self.buttons = []
        for x in range(self.size):
            row = []
            for y in range(self.size):
                btn = tk.Button(
                    self.root,
                    text=' ',
                    width=3,
                    height=1,
                    font=('Arial', 12, 'bold'),
                    command=lambda x=x, y=y: self.on_click(x, y)
                )
                btn.bind('<Button-3>', lambda event, x=x, y=y: self.on_right_click(x, y))
                btn.grid(row=x, column=y, sticky='nsew')
                row.append(btn)
            self.buttons.append(row)

    def on_click(self, x, y):
        """Обработка левого клика (открытие клетки)"""
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False

        if (x, y) in self.flags:
            return

        if self.hidden_map[x][y] == 'M':
            self.game_over(False)
            return

        self.reveal_cells(x, y)
        self.update_buttons()

        if self.check_win():
            self.game_over(True)

    def on_right_click(self, x, y):
        """Обработка правого клика (установка/снятие флага)"""
        if self.player_map[x][y] != '-':
            return

        if (x, y) in self.flags:
            self.flags.remove((x, y))
            if (x, y) in self.correct_flags:
                self.correct_flags.remove((x, y))
        else:
            self.flags.add((x, y))
            if self.hidden_map[x][y] == 'M':
                self.correct_flags.add((x, y))

        self.update_buttons()

        if len(self.correct_flags) == self.bomb_count and len(self.flags) == self.bomb_count:
            self.game_over(True)

    def reveal_cells(self, x, y):
        """Рекурсивное открытие клеток"""
        if not (0 <= x < self.size and 0 <= y < self.size) or self.player_map[x][y] != '-':
            return

        self.player_map[x][y] = self.hidden_map[x][y]

        if self.hidden_map[x][y] == ' ':
            directions = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1), (0, 1),
                          (1, -1), (1, 0), (1, 1)]
            for dx, dy in directions:
                self.reveal_cells(x + dx, y + dy)

    def update_buttons(self):
        """Обновляет внешний вид кнопок"""
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) in self.flags:
                    self.buttons[x][y].config(text='🚩', fg='red')
                elif self.player_map[x][y] == '-':
                    self.buttons[x][y].config(text=' ', bg='SystemButtonFace')
                else:
                    cell = self.player_map[x][y]
                    self.buttons[x][y].config(text=cell, bg='light gray')

                    # Разные цвета для цифр
                    if cell.isdigit():
                        num = int(cell)
                        colors = ['', 'blue', 'green', 'red', 'dark blue',
                                  'brown', 'teal', 'black', 'gray']
                        self.buttons[x][y].config(fg=colors[num])

    def check_win(self):
        """Проверка условий победы"""
        # Все безопасные клетки открыты
        for x in range(self.size):
            for y in range(self.size):
                if self.hidden_map[x][y] != 'M' and self.player_map[x][y] == '-':
                    return False
        return True

    def game_over(self, won):
        """Обработка конца игры"""
        # Показываем все мины
        for x in range(self.size):
            for y in range(self.size):
                if self.hidden_map[x][y] == 'M':
                    self.buttons[x][y].config(text='Bomb', bg='orange' if not won else 'light green')

        # Отключаем все кнопки
        for x in range(self.size):
            for y in range(self.size):
                self.buttons[x][y].config(state='disabled')

        # Показываем сообщение
        if won:
            messagebox.showinfo("Победа!", "Поздравляем! Вы выиграли!")
        else:
            messagebox.showinfo("Поражение", "Вы наступили на мину!")

    def new_game(self):
        """Начинает новую игру"""
        # Запрашиваем количество мин
        self.get_bomb_count()

        # Сбрасываем состояние игры
        self.first_click = True
        self.flags = set()
        self.correct_flags = set()

        # Инициализируем новую игру
        self.create_board()
        self.create_buttons()

    def get_bomb_count(self):
        """Запрашивает количество мин через диалоговое окно"""
        while True:
            try:
                count = tk.simpledialog.askinteger(
                    "Количество мин",
                    "Введите количество мин (1-80):",
                    parent=self.root,
                    minvalue=1,
                    maxvalue=80
                )
                if count is None:  # Пользователь нажал "Отмена"
                    count = 10
                self.bomb_count = count
                break
            except:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    game = MinesweeperGUI(root)
    root.mainloop()