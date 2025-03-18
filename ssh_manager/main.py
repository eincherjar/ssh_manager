import os
import platform
import curses
from ssh_manager.ssh_operations import get_config_path, read_hosts, add_entry, update_entry, remove_entry, connect_via_ssh, change_config_path

config_path = get_config_path()


def draw_menu(stdscr):
    curses.curs_set(0)
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr("  === Menedżer Konfiguracji SSH ===\n", curses.A_BOLD)
        stdscr.addstr(f"  Aktualny plik: {config_path} \n", curses.A_DIM)

        # 🔥 Dodajemy listę hostów przed menu
        hosts = read_hosts(config_path)
        if hosts:
            stdscr.addstr("\n  >>> Lista hostów <<<\n", curses.A_UNDERLINE)
            for idx, host in enumerate(hosts, start=1):
                stdscr.addstr(f"    {idx}. {host['Host']}\n")

        stdscr.addstr("\n  Wybierz opcję:\n\n")
        menu_options = ["Dodaj nowy host", "Edytuj hosta", "Usuń hosta", "Połącz z hostem", "Podaj nową ścieżkę do config", "Wyjście"]

        for idx, option in enumerate(menu_options):
            if idx == current_row:
                stdscr.addstr(f"  > {idx + 1}. {option}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"    {idx + 1}. {option}\n")

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1:
            current_row += 1
        elif key in [10, 13]:  # Enter
            if current_row == 0:
                add_host_ui(stdscr)
            elif current_row == 1:
                edit_host_ui(stdscr)
            elif current_row == 2:
                remove_host_ui(stdscr)
            elif current_row == 3:
                connect_host_ui(stdscr)
            elif current_row == 4:
                global config_path  # Deklarujemy globalną zmienną na początku
                new_path = change_config_path()
                if new_path:
                    config_path = new_path  # Teraz można ją bezpiecznie przypisać
            elif current_row == 5:
                break


def add_host_ui(stdscr):
    stdscr.clear()
    stdscr.addstr("Dodawanie nowego hosta:\n")
    stdscr.addstr("Podaj nazwę hosta: ")
    stdscr.refresh()
    curses.echo()
    host = stdscr.getstr().decode("utf-8")

    stdscr.addstr("Podaj adres hosta (HostName): ")
    stdscr.refresh()
    host_name = stdscr.getstr().decode("utf-8")

    add_entry(config_path, host, host_name)
    stdscr.addstr("\nHost został dodany! Wciśnij dowolny klawisz, aby wrócić.\n")
    stdscr.refresh()
    stdscr.getch()


def edit_host_ui(stdscr):
    stdscr.clear()
    hosts = read_hosts(config_path)
    if not hosts:
        stdscr.addstr("Brak hostów w pliku config.\nWciśnij dowolny klawisz.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr("Edytuj hosta:\n")
    for idx, host in enumerate(hosts):
        stdscr.addstr(f"  {idx + 1}. {host['Host']}\n")

    stdscr.addstr("\nWybierz numer hosta: ")
    stdscr.refresh()
    curses.echo()
    try:
        choice = int(stdscr.getstr().decode("utf-8")) - 1
        if 0 <= choice < len(hosts):
            selected_host = hosts[choice]
            stdscr.addstr(f"\nNowy adres dla {selected_host['Host']}: ")
            stdscr.refresh()
            new_hostname = stdscr.getstr().decode("utf-8")
            update_entry(config_path, selected_host["Host"], new_hostname)
            stdscr.addstr("\nHost został zaktualizowany! Wciśnij dowolny klawisz.")
        else:
            stdscr.addstr("\nNieprawidłowy wybór!")
    except ValueError:
        stdscr.addstr("\nBłąd: musisz podać numer.")

    stdscr.refresh()
    stdscr.getch()


def remove_host_ui(stdscr):
    stdscr.clear()
    hosts = read_hosts(config_path)
    if not hosts:
        stdscr.addstr("Brak hostów w pliku config.\nWciśnij dowolny klawisz.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr("Usuń hosta:\n")
    for idx, host in enumerate(hosts):
        stdscr.addstr(f"  {idx + 1}. {host['Host']}\n")

    stdscr.addstr("\nWybierz numer hosta do usunięcia: ")
    stdscr.refresh()
    curses.echo()
    try:
        choice = int(stdscr.getstr().decode("utf-8")) - 1
        if 0 <= choice < len(hosts):
            remove_entry(config_path, hosts[choice]["Host"])
            stdscr.addstr("\nHost został usunięty! Wciśnij dowolny klawisz.")
        else:
            stdscr.addstr("\nNieprawidłowy wybór!")
    except ValueError:
        stdscr.addstr("\nBłąd: musisz podać numer.")

    stdscr.refresh()
    stdscr.getch()


def connect_host_ui(stdscr):
    stdscr.clear()
    hosts = read_hosts(config_path)
    if not hosts:
        stdscr.addstr("Brak hostów w pliku config.\nWciśnij dowolny klawisz.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr("Połącz z hostem:\n")
    for idx, host in enumerate(hosts):
        stdscr.addstr(f"  {idx + 1}. {host['Host']}\n")

    stdscr.addstr("\nWybierz numer hosta: ")
    stdscr.refresh()
    curses.echo()
    try:
        choice = int(stdscr.getstr().decode("utf-8")) - 1
        if 0 <= choice < len(hosts):
            stdscr.addstr(f"\nŁączenie z {hosts[choice]['Host']}...\n")
            stdscr.refresh()
            connect_via_ssh(hosts[choice]["Host"])
        else:
            stdscr.addstr("\nNieprawidłowy wybór!")
    except ValueError:
        stdscr.addstr("\nBłąd: musisz podać numer.")

    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(draw_menu)


def run():
    import curses

    curses.wrapper(draw_menu)
