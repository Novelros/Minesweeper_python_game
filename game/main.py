import random


def Generator_Map(mines):
    """Метод создания карты"""
    # Создаем пустую список
    size = 9
    map = [[' ' for _ in range(size)] for _ in range(size)]
    mines_count = mines

    mines = set()  # убрать дубликаты
    while len(mines) < mines_count:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)  # возвращает случайное число N, где a ≤ N ≤ b
        mines.add((x, y))
        map[x][y] = 'M'

    # Заполняем числами (количество мин вокруг) - список смещений для проверки 8 соседних клеток:
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    for x in range(size):
        for y in range(size):
            if map[x][y] != 'M':
                count = 0
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size:
                        if map[nx][ny] == 'M':
                            count += 1
                if count > 0:
                    map[x][y] = str(count)

    map_mines = [[' '] + list(range(1, size + 1))]
    for i in range(size):
        map_mines.append([i + 1] + map[i])

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
        count_of_bomb = int(input("Ввидите два число - количество мин от 1-80\n"))
        if abs(count_of_bomb - 40.5) > 39.5:
            continue
        return count_of_bomb
        break


def get_action():
    """Метод запроса действия: открыть или пометить"""
    while True:
        action = input("Выберите действие (d - открыть, f - пометить флагом): ").lower()
        if action in ('d', 'f'):
            return action
        print("Используйте 'd' или 'f'!")


def get_coordinates():
    """Получение координат с проверкой"""
    while True:
        try:
            coords = input("Введите координаты (формат Y-X): ").split('-')
            if len(coords) != 2:
                raise ValueError
            x, y = map(int, coords)
            if abs(x - 5.5) > 4.5 or abs(y - 5.5) > 4.5:
                print("Координаты должны быть от 1 до 9!")
                continue
            return x - 1, y - 1  # Переводим в индексы массива
        except ValueError:
            print("Ошибка! Используйте формат 'Y-X' (например, 3-5)")


def reveal_cells(map, player_map, display_map, x, y, size):
    """Рекурсивно открывает все соседние пустые клетки"""
    # Проверяем, что координаты в пределах поля и клетка еще не открыта
    if not (0 <= x < size and 0 <= y < size) or player_map[x][y] != '-':
        return

    # Открываем текущую клетку
    player_map[x][y] = map[x + 1][y + 1]  # +1 из-за заголовков в map
    display_map[x + 1][y + 1] = player_map[x][y]  # Обновляем отображаемую карту

    # Если клетка пустая (не число и не мина), открываем соседей
    if player_map[x][y] == ' ':
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        for dx, dy in directions:
            reveal_cells(map, player_map, display_map, x + dx, y + dy, size)


def main():
    dictionary_for_x_y = {'y': [], 'x': []}
    bomb_count = get_bomb_count()
    hidden_map = Generator_Map(bomb_count)
    player_map = [['-' for _ in range(9)] for _ in range(9)]
    flags = set()
    correct_flags = set()

    # Добавляем номера строк и столбцов для отображения
    display_map = []
    display_map.append([' '] + list(range(1, 10)))
    for i in range(9):
        display_map.append([i + 1] + player_map[i])

    while True:
        print("\nТекущая карта:")
        print_map(display_map, flags)
        action = get_action()
        x, y = get_coordinates()

        # Проверка на уже открытую клетку
        if player_map[x][y] != '-':
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
                print("\nПоздравляем! Вы правильно отметили все мины!")
                print("Игровое поле:")
                print_map(hidden_map)
                break
            continue

        # Действие: открыть клетку
        if (x, y) in flags:
            print("Сначала уберите флаг с этой клетки!")
            continue

        # Проверка на мину ДО открытия
        if hidden_map[x + 1][y + 1] == 'M':
            print("\nBOOM! Вы наступили на мину!")
            print("Игровое поле:")
            print_map(hidden_map)
            break

        # Открываем клетку и соседей (если пустая)
        reveal_cells(hidden_map, player_map, display_map, x, y, 9)

        # Добавляем в историю
        dictionary_for_x_y['y'].append(x + 1)
        dictionary_for_x_y['x'].append(y + 1)
        print(x + 1, y + 1, dictionary_for_x_y)

        # Проверка победы по открытым клеткам
        if all(player_map[i][j] != '-' or hidden_map[i + 1][j + 1] == 'M'
               for i in range(9) for j in range(9)):
            print("\nПоздравляем! Вы открыли все безопасные клетки!")
            print("Игровое поле:")
            print_map(hidden_map)
            break


main()
