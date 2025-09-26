import random


def Generator_Map(mines, first_move):
    """Метод создания карты"""
    # Задаем размер игрового поля (классический сапёр - 9x9)
    size = 9
    map_dict = {}  # Используем словарь вместо списка

    mines_count = mines
    mines = set()  # убрать дубликаты

    # Генерация случайных мин, исключая первую клетку игрока
    first_x, first_y = first_move
    while len(mines) < mines_count:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        if (x, y) != (first_x, first_y):  # Исключаем первую клетку игрока
            mines.add((x, y))
            map_dict[(x, y)] = 'M'  # Записываем мину в словарь

    # Заполняем числами (количество мин вокруг) - список смещений для проверки 8 соседних клеток:
    directions = [(-1, -1), (-1, 0), (-1, 1),  # Верхние соседи
                  (0, -1), (0, 1),  # Боковые соседи
                  (1, -1), (1, 0), (1, 1)]  # Нижние соседи

    # Проходим по всем клеткам поля для заполнения чисел
    for x in range(size):
        for y in range(size):
            if (x, y) not in map_dict:  # Если это не мина
                count = 0
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in map_dict and map_dict[(nx, ny)] == 'M':
                        count += 1
                if count > 0:
                    map_dict[(x, y)] = str(count)
                else:
                    map_dict[(x, y)] = ' '

    # Преобразуем словарь обратно в список
    map_mines = [[' '] + list(range(1, size + 1))]
    for i in range(size):
        row = [i + 1]
        for j in range(size):
            row.append(map_dict.get((i, j), ' '))
        map_mines.append(row)

    return map_mines


def print_map(map, flags=None):
    """Метод прорисовки карты"""
    if flags is None:
        flags = set()

    for i, row in enumerate(map):
        printed_row = []
        for j, cell in enumerate(row):
            if (i - 1, j - 1) in flags and cell == 'M':
                printed_row.append('F')
            elif (i - 1, j - 1) in flags:
                printed_row.append('?')
            else:
                printed_row.append(str(cell))
        print(' '.join(printed_row))


def get_bomb_count():
    """Метод запроса у пользователя количества мин"""
    while True:
        try: #1. Внесены изменения в проверку введенного количества бомб, сокращен диапазон для улучшения игрового процесса
            count_of_bomb = int(input("Введите одно число - количество мин от 1-15 шт.\n"))
            if 1 <= count_of_bomb <= 15:
                return count_of_bomb
            print("Число должно быть от 1 до 15!")
        except ValueError:
            print("Введите корректное число!")


def get_action():
    """Метод запроса действия: открыть, пометить или открыть вокруг""" #2. Добавлен функционал - открыть вокруг
    while True:
        action = input("Выберите действие (d - открыть, f - пометить флагом, o - открыть вокруг): ").lower()
        if action in ('d', 'f', 'o'):
            return action
        print("Используйте 'd', 'f' или 'o'!")


def get_coordinates():
    """Получение координат с проверкой"""
    MIN = 1
    MAX = 9
    while True:
        try:
            coords = input("Введите координаты (формат Y-X): ").strip().split('-')
            if len(coords) != 2:
                raise ValueError("Неправильный формат ввода")
            x, y = map(int, coords)
            if not (MIN <= x <= MAX) or not (MIN <= y <= MAX):
                print(f"Координаты должны быть от {MIN} до {MAX}!")
                continue
            return x - 1, y - 1  # Переводим в индексы массива (0-8)

        except ValueError as e:
            print("Ошибка! Используйте формат 'Y-X' (например, 3-5)")


def reveal_cells(map, player_map, display_map, x, y, size):
    """Итеративно открывает все соседние пустые клетки"""  #3. Рекурсия заменена на итерации
    stack = [(x, y)]
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    while stack:
        x, y = stack.pop()
        if not (0 <= x < size and 0 <= y < size) or player_map[x][y] != '-':
            continue

        player_map[x][y] = map[x + 1][y + 1]
        display_map[x + 1][y + 1] = player_map[x][y]

        if player_map[x][y] == ' ':
            for dx, dy in directions:
                stack.append((x + dx, y + dy))


def open_around_cell(hidden_map, player_map, display_map, x, y, flags, size):
    """Открывает все соседние клетки, если количество флагов соответствует цифре""" #4. Новый метод для функцтонала "открыть вокруг"
    # Проверяем, что клетка открыта и содержит цифру
    if player_map[x][y] == '-' or player_map[x][y] not in '12345678':
        print("Эта клетка не содержит цифру или не открыта!")
        return False

    # Получаем цифру в клетке
    number = int(player_map[x][y])

    # Подсчитываем количество флагов вокруг
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    flag_count = 0
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size and (nx, ny) in flags:
            flag_count += 1

    # Если количество флагов не соответствует цифре
    if flag_count != number:
        print(f"Количество флагов вокруг ({flag_count}) не соответствует цифре в клетке ({number})!")
        return False

    # Открываем все соседние клетки без флагов
    mine_hit = False
    cells_opened = 0

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            # Пропускаем клетки с флагами
            if (nx, ny) in flags:
                continue

            # Пропускаем уже открытые клетки
            if player_map[nx][ny] != '-':
                continue

            # Открываем клетку
            player_map[nx][ny] = hidden_map[nx + 1][ny + 1]
            display_map[nx + 1][ny + 1] = player_map[nx][ny]
            cells_opened += 1

            # Проверяем, не мина ли это
            if player_map[nx][ny] == 'M':
                mine_hit = True
            # Если клетка пустая, открываем соседей рекурсивно
            elif player_map[nx][ny] == ' ':
                reveal_cells(hidden_map, player_map, display_map, nx, ny, size)

    print(f"Открыто {cells_opened} клеток вокруг.")
    return not mine_hit  # Возвращаем False, если нашли мину


def main():  #5. Встроен новый метод - "открыть вокруг", переработана логика определения победы
    dictionary_for_x_y = {'y': [], 'x': []}
    bomb_count = get_bomb_count()

    # Получаем первый ход до генерации карты
    print("Сделайте первый ход:")
    first_x, first_y = get_coordinates()

    # Генерируем карту с минами, исключая первую клетку игрока
    hidden_map = Generator_Map(bomb_count, (first_x, first_y))

    player_map = [['-' for _ in range(9)] for _ in range(9)]
    flags = set()
    correct_flags = set()

    # Добавляем номера строк и столбцов для отображения
    display_map = []
    display_map.append([' '] + list(range(1, 10)))
    for i in range(9):
        display_map.append([i + 1] + player_map[i])

    # Обрабатываем первый ход
    reveal_cells(hidden_map, player_map, display_map, first_x, first_y, 9)

    while True:
        print("\nТекущая карта:")
        print_map(display_map, flags)
        action = get_action()

        if action == 'o':
            # Для действия "открыть вокруг" клетка должна быть уже открыта
            x, y = get_coordinates()
            if player_map[x][y] == '-':
                print("Сначала откройте эту клетку командой 'd'!")
                continue

            success = open_around_cell(hidden_map, player_map, display_map, x, y, flags, 9)
            if not success:
                print("\nBOOM! Вы наступили на мину")
                print("Игровое поле:")
                # Показываем все мины
                for i in range(9):
                    for j in range(9):
                        if hidden_map[i + 1][j + 1] == 'M':
                            display_map[i + 1][j + 1] = 'M'
                print_map(display_map)
                break
        else:
            x, y = get_coordinates()

            # Проверка на уже открытую клетку (кроме действия 'f')
            if action != 'f' and player_map[x][y] != '-':
                print("Эта клетка уже открыта!")
                continue

            if action == 'f':  # Пометить флагом
                if (x, y) in flags:
                    flags.remove((x, y))
                    if hidden_map[x + 1][y + 1] == 'M':
                        correct_flags.remove((x, y))
                else:
                    flags.add((x, y))
                    if hidden_map[x + 1][y + 1] == 'M':
                        correct_flags.add((x, y))

                # Проверка победы по флагам
                if len(correct_flags) == bomb_count and len(flags) == bomb_count:
                    print("\nПоздравляем! Вы правильно отметили все мины")
                    print("Игровое поле:")
                    print_map(hidden_map)
                    break
                continue

            # Действие: открыть клетку
            if (x, y) in flags:
                print("Сначала уберите флаг с этой клетки!")
                continue

            # Проверка на мину
            if hidden_map[x + 1][y + 1] == 'M':
                print("\nBOOM! Вы наступили на мину")
                print("Игровое поле:")
                # Показываем все мины
                for i in range(9):
                    for j in range(9):
                        if hidden_map[i + 1][j + 1] == 'M':
                            display_map[i + 1][j + 1] = 'M'
                print_map(display_map)
                break

            # Открываем клетку и соседей (если пустая)
            reveal_cells(hidden_map, player_map, display_map, x, y, 9)

        # Проверка победы по открытым клеткам (после каждого хода)
        closed_cells = sum(1 for i in range(9) for j in range(9)
                           if player_map[i][j] == '-' and hidden_map[i + 1][j + 1] != 'M')
        if closed_cells == 0:
            print("\nПоздравляем! Вы открыли все безопасные клетки")
            print("Игровое поле:")
            # Показываем все мины под флагами
            for i in range(9):
                for j in range(9):
                    if hidden_map[i + 1][j + 1] == 'M':
                        display_map[i + 1][j + 1] = 'M'
            print_map(display_map, flags)
            break


main()
