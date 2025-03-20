import os
import platform
import curses
from tabulate import tabulate
from ssh_manager.ssh_operations import get_config_path, read_hosts, add_entry, update_entry, remove_entry, connect_via_ssh, get_user_input, clear_terminal, get_input

config_path = get_config_path()


def draw_menu(stdscr):
    global config_path
    curses.curs_set(0)
    mode = "connect"  # Domyślnie tryb wyboru hosta
    selected_host_idx = 0
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr("  === Menedżer Konfiguracji SSH ===\n", curses.A_BOLD)
        stdscr.addstr(f"  Aktualny plik: {config_path} \n", curses.A_DIM)

        hosts = read_hosts(config_path)

        if mode == "connect":
            if not hosts:
                stdscr.addstr("\nBrak hostów w pliku config.\nWciśnij dowolny klawisz, aby dodać nowy host.", curses.A_BOLD)
                stdscr.refresh()
                stdscr.getch()
                mode = "menu"
                continue

            stdscr.addstr("\n  >>> Wybierz hosta do połączenia <<<\n", curses.A_UNDERLINE)

            # Tabela hostów
            columns = ["ID", "Host", "HostName", "User", "Port", "IdentityFile"]
            padding = 2
            min_width = 6

            col_widths = {col: max(len(col), min_width) + padding for col in columns}
            for idx, host in enumerate(hosts, start=1):
                col_widths["ID"] = max(col_widths["ID"], len(str(idx)) + padding)
                col_widths["Host"] = max(col_widths["Host"], len(host.get("Host", "-")) + padding)
                col_widths["HostName"] = max(col_widths["HostName"], len(host.get("HostName", "-")) + padding)
                col_widths["User"] = max(col_widths["User"], len(host.get("User", "-")) + padding)
                col_widths["Port"] = max(col_widths["Port"], len(host.get("Port", "-")) + padding)
                col_widths["IdentityFile"] = max(col_widths["IdentityFile"], len(host.get("IdentityFile", "-")) + padding)

            # Nagłówek tabeli
            header = "|".join(f" {col:^{col_widths[col] - 2}} " for col in columns)
            stdscr.addstr(f"  {header}\n", curses.A_BOLD)
            separator = "+".join("-" * col_widths[col] for col in columns)
            stdscr.addstr(f"  {separator}\n")

            # Wiersze hostów
            for idx, host in enumerate(hosts, start=1):
                row = "|".join(f" {str(host.get(col, '-') if col != 'ID' else idx):<{col_widths[col] - 2}} " for col in columns)
                if idx - 1 == selected_host_idx:
                    stdscr.addstr(f"  > {row} <\n", curses.A_REVERSE)
                else:
                    stdscr.addstr(f"    {row}\n")

            stdscr.addstr("\n[Strzałki: Wybór | Enter: Połącz | M: Menu | Q: Wyjście]\n", curses.A_DIM)

        elif mode == "menu":
            stdscr.addstr("\n  >>> MENU <<<\n", curses.A_UNDERLINE)
            menu_options = [
                "  Dodaj nowy host   ",
                "  Edytuj hosta      ",
                "  Usuń hosta        ",
                "  Powrót do listy hostów  ",  # Powrót do domyślnej tabeli
                "  Podaj nową ścieżkę do config  ",
                "  Wyjście           ",
            ]

            for idx, option in enumerate(menu_options):
                if idx == current_row:
                    stdscr.addstr(f"  > {option} <  \n", curses.A_REVERSE)
                else:
                    stdscr.addstr(f"    {option}    \n")

            stdscr.addstr("\n[Strzałki: Nawigacja | Enter: Wybór | Q: Wyjście]\n", curses.A_DIM)

        stdscr.refresh()
        key = stdscr.getch()

        if mode == "connect":
            if key == curses.KEY_UP and selected_host_idx > 0:
                selected_host_idx -= 1
            elif key == curses.KEY_DOWN and selected_host_idx < len(hosts) - 1:
                selected_host_idx += 1
            elif key in [10, 13]:  # Enter - Połączenie z hostem
                stdscr.clear()
                stdscr.addstr(f"\nŁączenie z {hosts[selected_host_idx]['Host']}...\n")
                stdscr.refresh()
                curses.endwin()  # Wyjście z trybu curses przed uruchomieniem SSH
                connect_via_ssh(hosts[selected_host_idx])
                return
            elif key in [ord("m"), ord("M")]:  # Przejście do menu
                mode = "menu"
            elif key in [ord("q"), ord("Q")]:  # Wyjście
                break

        elif mode == "menu":
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
                    mode = "connect"  # Powrót do listy hostów
                elif current_row == 4:
                    new_path = change_config_path_ui(stdscr)
                    if new_path:
                        config_path = new_path
                elif current_row == 5:
                    break
            elif key in [ord("q"), ord("Q")]:  # Wyjście
                break


def add_host_ui(stdscr):
    curses.curs_set(0)  # Ustawienie widoczności kursora
    stdscr.clear()
    stdscr.addstr("Dodawanie nowego hosta (ESC, aby wrócić):\n", curses.A_BOLD)

    host = get_user_input(stdscr, "Podaj nazwę hosta", "")
    if not host:  # Jeśli ESC, wracamy
        return

    host_name = get_user_input(stdscr, "Podaj adres hosta (HostName)", "")
    if not host_name:
        return

    user = get_user_input(stdscr, "Podaj użytkownika (Enter = pomiń)", "")

    port = get_user_input(stdscr, "Podaj port (Enter = pomiń)", "")
    if port and not port.isdigit():
        port = ""  # Walidacja portu - jeśli nie jest liczbą, pomijamy

    identity_file = get_user_input(stdscr, "Podaj ścieżkę do klucza (Enter = pomiń, domyślny: ~/.ssh/id_rsa.pub)", "")

    add_entry(config_path, host, host_name, user, port, identity_file)


def edit_host_ui(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    hosts = read_hosts(config_path)
    if not hosts:
        stdscr.addstr("Brak hostów w pliku config.\nWciśnij dowolny klawisz.")
        stdscr.refresh()
        stdscr.getch()
        return

    valid_rows = list(range(len(hosts)))
    selected_idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr("Edytuj host:\n", curses.A_BOLD)

        table_data = [
            [
                idx + 1,
                host.get("Host", ""),
                host.get("HostName", ""),
                host.get("User", ""),
                host.get("Port", ""),
                host.get("IdentityFile", ""),
            ]
            for idx, host in enumerate(hosts)
        ]

        headers = ["ID", "Host", "HostName", "User", "Port", "IdentityFile"]
        table_lines = tabulate(table_data, headers=headers, tablefmt="fancy_grid").split("\n")

        row_counter = -2
        for i, line in enumerate(table_lines):
            if "─" in line or "═" in line:
                stdscr.addstr(line + "\n", curses.A_DIM)
            else:
                row_counter += 1
                if row_counter == valid_rows[selected_idx]:
                    stdscr.addstr(line + "\n", curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.addstr(line + "\n")

        stdscr.addstr("\nStrzałki ↑ ↓ - Wybierz, ENTER - Edytuj, ESC - Powrót")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(valid_rows) - 1:
            selected_idx += 1
        elif key in [10, 13]:
            selected_host = hosts[valid_rows[selected_idx]]
            stdscr.clear()
            stdscr.addstr(f"Edytujesz host: {selected_host['Host']}\n\n", curses.A_BOLD)

            new_host = get_user_input(stdscr, "Nowy Host", selected_host["Host"])
            new_hostname = get_user_input(stdscr, "Nowy HostName", selected_host.get("HostName", ""))
            new_user = get_user_input(stdscr, "Nowy użytkownik", selected_host.get("User", ""))
            new_port = get_user_input(stdscr, "Nowy port", selected_host.get("Port", ""))
            new_identity_file = get_user_input(stdscr, "Nowa ścieżka IdentityFile", selected_host.get("IdentityFile", ""))

            update_entry(config_path, selected_host["Host"], new_host, new_hostname, new_user, new_port, new_identity_file)

            hosts = read_hosts(config_path)
            valid_rows = list(range(len(hosts)))
            selected_idx = min(selected_idx, len(valid_rows) - 1)
        elif key == 27:
            break


def remove_host_ui(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    hosts = read_hosts(config_path)
    if not hosts:
        stdscr.addstr("Brak hostów w pliku config.\nWciśnij dowolny klawisz.")
        stdscr.refresh()
        stdscr.getch()
        return

    valid_rows = list(range(len(hosts)))  # Lista rzeczywistych hostów (bez separatorów)
    selected_idx = 0  # Wybrany host (po indeksie w valid_rows)

    while True:
        stdscr.clear()
        stdscr.addstr("Usuń host:\n", curses.A_BOLD)

        # Tworzymy listę danych hostów
        table_data = [
            [
                idx + 1,  # ID zaczyna się od 1
                host.get("Host", ""),
                host.get("HostName", ""),
                host.get("User", ""),
                host.get("Port", ""),
                host.get("IdentityFile", ""),
            ]
            for idx, host in enumerate(hosts)
        ]

        headers = ["ID", "Host", "HostName", "User", "Port", "IdentityFile"]
        table_lines = tabulate(table_data, headers=headers, tablefmt="fancy_grid").split("\n")

        row_counter = -2  # Pomijamy 2 pierwsze wiersze (nagłówki)
        for i, line in enumerate(table_lines):
            if "─" in line or "═" in line:  # To separator, nie zaznaczamy
                stdscr.addstr(line + "\n", curses.A_DIM)
            else:
                row_counter += 1
                if row_counter == valid_rows[selected_idx]:  # Podświetlenie TYLKO hostów
                    stdscr.addstr(line + "\n", curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.addstr(line + "\n")

        stdscr.addstr("\nStrzałki ↑ ↓ - Wybierz, ENTER - Usuń, ESC - Powrót")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(valid_rows) - 1:
            selected_idx += 1
        elif key in [10, 13]:  # ENTER = usuń hosta
            remove_entry(config_path, hosts[valid_rows[selected_idx]]["Host"])
            hosts = read_hosts(config_path)  # Odświeżamy listę
            valid_rows = list(range(len(hosts)))  # Aktualizujemy indeksy
            selected_idx = min(selected_idx, len(valid_rows) - 1)
        elif key == 27:  # ESC - powrót do menu
            break


def connect_host_ui(stdscr):
    curses.curs_set(0)  # Ukrycie kursora
    hosts = read_hosts(config_path)  # Pobieramy dane hostów z pliku

    if not hosts:
        stdscr.addstr("Brak hostów w pliku config.\nWciśnij dowolny klawisz.")
        stdscr.refresh()
        stdscr.getch()
        return

    selected_idx = 0  # Domyślnie wybór na pierwszym hoście

    while True:
        stdscr.clear()
        stdscr.addstr("Połącz z hostem:\n", curses.A_BOLD)

        for idx, host in enumerate(hosts):
            if idx == selected_idx:
                stdscr.addstr(f" > {host['Host']} <\n", curses.A_REVERSE)  # Zaznaczony host
            else:
                stdscr.addstr(f"   {host['Host']}\n")

        stdscr.addstr("\n[Strzałki: Wybór | Enter: Połącz | Esc: Wyjście]")
        stdscr.refresh()

        key = stdscr.getch()  # Pobranie klawisza

        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1  # Przesunięcie w górę
        elif key == curses.KEY_DOWN and selected_idx < len(hosts) - 1:
            selected_idx += 1  # Przesunięcie w dół
        elif key == 10:  # Enter
            stdscr.clear()
            stdscr.addstr(f"\nŁączenie z {hosts[selected_idx]['Host']}...\n")
            stdscr.refresh()
            curses.endwin()  # Wyjście z trybu curses przed uruchomieniem SSH
            clear_terminal()
            connect_via_ssh(hosts[selected_idx])
            clear_terminal()
            return  # Powrót do głównej pętli `wrapper()`
        elif key == 27:  # Esc - Wyjście do głównego menu
            return


def change_config_path_ui(stdscr):
    curses.curs_set(1)  # Ustawienie widoczności kursora
    """Pozwala użytkownikowi zmienić ścieżkę do pliku konfiguracyjnego SSH w trybie curses."""
    curses.echo()  # Włączenie trybu echo, by widzieć wpisywany tekst
    stdscr.clear()
    stdscr.addstr("Podaj nową ścieżkę do pliku SSH config (Enter, aby zatwierdzić, ESC aby anulować):\n", curses.A_BOLD)

    new_path = ""

    while True:
        stdscr.clear()
        stdscr.addstr("Podaj nową ścieżkę do pliku SSH config (Enter, aby zatwierdzić, ESC aby anulować):\n", curses.A_BOLD)
        stdscr.addstr(f"> {new_path}")  # Wyświetlamy aktualny stan wpisywanego tekstu
        stdscr.refresh()

        key = stdscr.getch()

        if key == 27:  # ESC -> powrót do menu
            return None
        elif key in [10, 13]:  # Enter -> zakończ edycję
            break
        elif key in [127, 8]:  # Backspace (obsługuje różne systemy)
            new_path = new_path[:-1]  # Usuwamy ostatni znak
        elif 32 <= key <= 126:  # Obsługuje tylko czytelne znaki (spacja - ~)
            new_path += chr(key)

        curses.curs_set(0)  # Ustawienie widoczności kursora

    new_path = new_path.strip()

    if os.path.isfile(new_path):
        return new_path  # Nowa ścieżka jest poprawna
    else:
        stdscr.addstr("\nBłąd: Plik nie istnieje. Naciśnij dowolny klawisz, aby wrócić.", curses.A_BOLD)
        stdscr.refresh()
        stdscr.getch()
        return None  # Jeśli plik nie istnieje, wracamy do menu


if __name__ == "__main__":
    curses.wrapper(draw_menu)


def run():
    import curses

    curses.wrapper(draw_menu)
