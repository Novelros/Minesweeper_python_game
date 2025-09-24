import pygame
from game import Minesweeper3D
from menu import GameMenu


def main():
    pygame.init()

    # Создаем окно меню
    menu_screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("3D Minesweeper - Menu")

    # Создаем меню
    menu = GameMenu(menu_screen)
    game_settings = menu.run()

    if game_settings:  # Если пользователь начал игру
        # Закрываем меню и создаем игровое окно
        pygame.quit()

        # Перезапускаем pygame для игрового окна
        pygame.init()

        # Создаем и запускаем игру с выбранными настройками
        game = Minesweeper3D(game_settings)
        game.run()


if __name__ == "__main__":
    main()