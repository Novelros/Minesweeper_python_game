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

    map_mines = []
    map_mines.append([' '] + list(range(1, size + 1)))
    for i in range(size):
        map_mines.append([i + 1] + map[i])

    return map_mines


def print_map(map):
    """Метод прорисовки карты"""
    for row in map:
        print(' '.join(str(cell) for cell in row))


def get_bomb_count():
    """Метод запроса у пользователя количества мин"""
    while True:
        count_of_bomb = int(input("Ввидите два число - количество мин от 1-80\n"))
        if abs(count_of_bomb - 40.5) > 39.5:
            continue
        return count_of_bomb
        break


def get_coordinates():
    """Получение координат с проверкой"""
    while True:
        try:
            coords = input("Введите координаты (формат X-Y): ").split('-')
            if len(coords) != 2:
                raise ValueError
            x, y = map(int, coords)
            if abs(x - 5.5) > 4.5 or abs(y - 5.5) > 4.5:
                print("Координаты должны быть от 1 до 9!")
                continue
            return x - 1, y - 1  # Переводим в индексы массива
        except ValueError:
            print("Ошибка! Используйте формат 'X-Y' (например, 3-5)")


def reveal_cells(map, player_map, x, y, size):
    """Рекурсивно открывает все соседние пустые клетки"""
    # Проверяем, что координаты в пределах поля и клетка еще не открыта
    if not (0 <= x < size and 0 <= y < size) or player_map[x][y] != '-':
        return

    # Открываем текущую клетку
    player_map[x][y] = map[x + 1][y + 1]  # +1 из-за заголовков в map

    # Если клетка пустая (не число и не мина), открываем соседей
    if player_map[x][y] == ' ':
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        for dx, dy in directions:
            reveal_cells(map, player_map, x + dx, y + dy, size)


def main():
    dictionary_for_x_y = {'x': [], 'y': []}  # Словарь со списками для хранения истории
    bomb_count = get_bomb_count()  # Вызов метода get_bomb_count и запись в переменную
    hidden_map = Generator_Map(bomb_count)
    player_map = [['-' for _ in range(9)] for _ in range(9)]

    # Добавляем номера строк и столбцов для отображения
    display_map = []
    display_map.append([' '] + list(range(1, 10)))
    for i in range(9):
        display_map.append([i + 1] + player_map[i])
    while True:
        print("\nТекущая карта:")
        print_map(display_map)
        x, y = get_coordinates()

        if hidden_map[x + 1][y + 1] == 'M':
            print("\nBOOM! Вы наступили на мину!")
            print("Игровое поле:")
            print_map(hidden_map)
            break

        # Открываем клетку и соседей (если пустая)
        reveal_cells(hidden_map, player_map, x, y, 9)

        # Обновляем отображаемую карту
        display_map[x + 1][y + 1] = player_map[x][y]

        # Проверка победы
        if all(cell != '-' for row in player_map for cell in row):
            print("\nПоздравляем! Вы победили!")
            print("Игровое поле:")
            print_map(hidden_map)
            break

        found = False
        for i in range(len(dictionary_for_x_y['x'])):
            if dictionary_for_x_y['x'][i] == x+1 and dictionary_for_x_y['y'][i] == y+1:
                found = True
                break

        if found:
            print(f"Клетка {x+1}-{y+1} уже открыта!")
            continue

        dictionary_for_x_y['x'].append(x+1)  # добавление в список словаря
        dictionary_for_x_y['y'].append(y+1)
        print(x+1, y+1, dictionary_for_x_y)


main()
