import os
import platform
import curses
from tabulate import tabulate
from ssh_manager.ssh_operations import get_config_path, read_hosts, add_entry, update_entry, remove_entry, connect_via_ssh, change_config_path, input_with_default

config_path = get_config_path()


def draw_menu(stdscr):
    global config_path
    curses.curs_set(0)
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr("  === Menedżer Konfiguracji SSH ===\n", curses.A_BOLD)
        stdscr.addstr(f"  Aktualny plik: {config_path} \n", curses.A_DIM)

        hosts = read_hosts(config_path)

        if hosts:
            stdscr.addstr("\n  >>> Lista hostów <<<\n", curses.A_UNDERLINE)

            # Nagłówki tabeli
            columns = ["ID", "Host", "HostName", "User", "Port", "IdentityFile"]
            padding = 2  # Padding 2 spacje
            min_width = 6  # Minimalna szerokość kolumn

            # Obliczanie szerokości kolumn
            col_widths = {col: max(len(col), min_width) for col in columns}  # Start od nagłówków

            for idx, host in enumerate(hosts, start=1):
                col_widths["ID"] = max(col_widths["ID"], len(str(idx)))
                col_widths["Host"] = max(col_widths["Host"], len(host.get("Host", "-")))
                col_widths["HostName"] = max(col_widths["HostName"], len(host.get("HostName", "-")))
                col_widths["User"] = max(col_widths["User"], len(host.get("User", "-")))
                col_widths["Port"] = max(col_widths["Port"], len(host.get("Port", "-")))
                col_widths["IdentityFile"] = max(col_widths["IdentityFile"], len(host.get("IdentityFile", "-")))

            # Dodanie paddingu do szerokości kolumn
            for col in col_widths:
                col_widths[col] += padding * 2

            # Formatowanie wiersza nagłówków
            header = "|".join(f" {col:^{col_widths[col] - 2}} " for col in columns)
            stdscr.addstr(f"  {header}\n", curses.A_BOLD)

            # Separator
            separator = "+".join("-" * col_widths[col] for col in columns)
            stdscr.addstr(f"  {separator}\n")

            # Wiersze tabeli
            for idx, host in enumerate(hosts, start=1):
                row = "|".join(f" {str(host.get(col, '-') if col != 'ID' else idx):<{col_widths[col] - 2}} " for col in columns)
                stdscr.addstr(f"  {row}\n")

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
                new_path = change_config_path()
                if new_path:
                    config_path = new_path
            elif current_row == 5:
                break


def add_host_ui(stdscr):
    stdscr.clear()
    stdscr.addstr("Dodawanie nowego hosta (ESC, aby wrócić):\n", curses.A_BOLD)

    curses.echo()  # Włącz echo do wprowadzania tekstu

    # Pobieranie wartości
    stdscr.addstr("Podaj nazwę hosta: ")
    host = stdscr.getstr().decode("utf-8").strip()
    if host.lower() == "esc":
        return

    stdscr.addstr("Podaj adres hosta (HostName): ")
    host_name = stdscr.getstr().decode("utf-8").strip()
    if host_name.lower() == "esc":
        return

    stdscr.addstr("Podaj użytkownika (Enter = pomiń): ")
    user = stdscr.getstr().decode("utf-8").strip() or None
    if user and user.lower() == "esc":
        return

    stdscr.addstr("Podaj port (Enter = pomiń): ")
    port = stdscr.getstr().decode("utf-8").strip()
    port = port if port.isdigit() else None
    if port and port.lower() == "esc":
        return

    stdscr.addstr("Podaj ścieżkę do klucza (Enter = pomiń, domyślny: ~/.ssh/id_rsa.pub): ")
    identity_file = stdscr.getstr().decode("utf-8").strip()
    if identity_file.lower() == "esc":
        return
    identity_file = identity_file or None  # Jeśli puste, nie dodajemy tego pola

    # Dodanie wpisu i powrót do menu
    add_entry(config_path, host, host_name, user, port, identity_file)


def edit_host_ui(stdscr):
    stdscr.clear()
    hosts = read_hosts(config_path)
    if not hosts:
        stdscr.addstr("Brak hostów w pliku config.\nWciśnij ESC, aby wrócić.")
        stdscr.refresh()
        while stdscr.getch() != 27:  # Czekamy na ESC
            pass
        return

    current_row = 0
    while True:
        stdscr.clear()
        stdscr.addstr("Edytuj hosta:\n", curses.A_BOLD)

        # Tworzenie tabeli
        headers = ["ID", "Host", "HostName", "User", "Port", "IdentityFile"]
        table_data = [[idx + 1, h["Host"], h.get("HostName", ""), h.get("User", ""), h.get("Port", ""), h.get("IdentityFile", "")] for idx, h in enumerate(hosts)]
        table_str = tabulate(table_data, headers, tablefmt="grid")

        for idx, line in enumerate(table_str.split("\n")):
            if idx == current_row + 3:  # Pomijamy nagłówki tabeli
                stdscr.addstr(f"> {line}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"  {line}\n")

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(hosts) - 1:
            current_row += 1
        elif key == 10:  # ENTER - wybór hosta do edycji
            break
        elif key == 27:  # ESC - powrót do menu
            return

    selected_host = hosts[current_row]

    # Edycja danych hosta
    stdscr.clear()
    stdscr.addstr(f"Edytujesz host: {selected_host['Host']}\n\n", curses.A_BOLD)

    new_hostname = input_with_default("Nowy HostName", selected_host.get("HostName", ""))
    new_user = input_with_default("Nowy User", selected_host.get("User", ""))
    new_port = input_with_default("Nowy Port", selected_host.get("Port", ""))
    new_identity_file = input_with_default("Nowa ścieżka do klucza", selected_host.get("IdentityFile", ""))

    update_entry(config_path, selected_host["Host"], new_hostname, new_user, new_port, new_identity_file)

    return  # Automatyczny powrót do menu po edycji


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
