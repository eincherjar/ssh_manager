import os
import platform
import subprocess
import curses
from ssh_manager.config_handler import get_config_path


def menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    options = ["1. Dodaj nowy host", "2. Edytuj hosta", "3. Usuń hosta", "4. Połącz z hostem", "5. Podaj nową ścieżkę do config", "0. Wyjście"]
    selected = 0
    file_path = get_config_path()

    while True:
        stdscr.clear()
        stdscr.addstr(0, 2, "=== Menedżer Konfiguracji SSH ===", curses.A_BOLD)
        stdscr.addstr(1, 2, f"Aktualny plik: {file_path}", curses.A_DIM)
        stdscr.addstr(2, 2, "Wybierz opcję:", curses.A_UNDERLINE)

        for idx, option in enumerate(options):
            if idx == selected:
                stdscr.addstr(idx + 4, 4, option, curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 4, 4, option)

        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(options) - 1:
            selected += 1
        elif key in [10, 13]:  # Enter
            if selected == 0:
                break

    stdscr.addstr(len(options) + 6, 2, "Naciśnij dowolny klawisz, aby wyjść...")
    stdscr.getch()


def run():
    curses.wrapper(menu)


if __name__ == "__main__":
    run()
