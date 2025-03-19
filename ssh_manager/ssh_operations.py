import os
import subprocess
import platform
import curses
import shutil


def get_config_path():
    return os.path.expanduser("~/.ssh/config")


def read_hosts(file_path):
    """Wczytuje listę hostów z pliku konfiguracyjnego SSH wraz z dodatkowymi parametrami."""
    hosts = []
    current_host = {}

    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()

                if line.lower().startswith("host "):  # Nowy host
                    if current_host:  # Jeśli istnieje poprzedni host, dodajemy go do listy
                        hosts.append(current_host)
                    current_host = {"Host": line.split(maxsplit=1)[1]}  # Resetujemy dla nowego hosta
                elif current_host:  # Pobieramy dodatkowe parametry
                    if line.lower().startswith("hostname "):
                        current_host["HostName"] = line.split(maxsplit=1)[1]
                    elif line.lower().startswith("user "):
                        current_host["User"] = line.split(maxsplit=1)[1]
                    elif line.lower().startswith("port "):
                        current_host["Port"] = line.split(maxsplit=1)[1]
                    elif line.lower().startswith("identityfile "):
                        current_host["IdentityFile"] = line.split(maxsplit=1)[1]

            if current_host:  # Dodaj ostatni host
                hosts.append(current_host)

    except FileNotFoundError:
        print("Plik konfiguracji SSH nie istnieje.")
    except Exception as e:
        print(f"Błąd podczas odczytu pliku: {e}")

    return hosts


def add_entry(file_path, host, host_name, user=None, port=None, identity_file=None):
    with open(file_path, "a") as file:
        file.write(f"\nHost {host}\n")
        file.write(f"    HostName {host_name}\n")
        if user:
            file.write(f"    User {user}\n")
        if port:
            file.write(f"    Port {port}\n")
        if identity_file:
            file.write(f"    IdentityFile {identity_file}\n")


def update_entry(file_path, old_host, new_host=None, new_host_name=None, new_user=None, new_port=None, new_identity_file=None):
    lines = []
    inside_target_host = False
    updated_host_block = []

    with open(file_path, "r") as file:
        for line in file:
            stripped_line = line.strip()

            # Jeśli napotkaliśmy Host, sprawdzamy, czy to ten, który chcemy zaktualizować
            if stripped_line.startswith("Host ") and old_host in stripped_line:
                if inside_target_host and updated_host_block:
                    lines.extend(updated_host_block)
                inside_target_host = True
                updated_host_block = [f"Host {new_host if new_host else old_host}\n"]
                continue

            if inside_target_host:
                # Zaktualizuj lub usuń odpowiednie wpisy
                if stripped_line.startswith("HostName "):
                    updated_host_block.append(f"    HostName {new_host_name}\n" if new_host_name else "")
                elif stripped_line.startswith("User "):
                    updated_host_block.append(f"    User {new_user}\n" if new_user else "")
                elif stripped_line.startswith("Port "):
                    updated_host_block.append(f"    Port {new_port}\n" if new_port else "")
                elif stripped_line.startswith("IdentityFile "):
                    # Jeśli new_identity_file jest pustym ciągiem, to usuwamy tę linię
                    if new_identity_file:
                        updated_host_block.append(f"    IdentityFile {new_identity_file}\n")
                    else:
                        # Jeśli new_identity_file jest pusty, nie dodajemy tej linii
                        continue
                elif stripped_line == "":
                    # Zakończenie edycji sekcji danego hosta
                    if new_host_name and not any("HostName " in l for l in updated_host_block):
                        updated_host_block.append(f"    HostName {new_host_name}\n")
                    if new_user and not any("User " in l for l in updated_host_block):
                        updated_host_block.append(f"    User {new_user}\n")
                    if new_port and not any("Port " in l for l in updated_host_block):
                        updated_host_block.append(f"    Port {new_port}\n")
                    if new_identity_file and not any("IdentityFile " in l for l in updated_host_block):
                        updated_host_block.append(f"    IdentityFile {new_identity_file}\n")
                    updated_host_block.append("\n")
                    lines.extend(updated_host_block)
                    inside_target_host = False
                else:
                    updated_host_block.append(line)
            else:
                lines.append(line)

    # Jeżeli plik kończył się na hostcie, a nie było pustej linii
    if inside_target_host and updated_host_block:
        if new_host_name and not any("HostName " in l for l in updated_host_block):
            updated_host_block.append(f"    HostName {new_host_name}\n")
        if new_user and not any("User " in l for l in updated_host_block):
            updated_host_block.append(f"    User {new_user}\n")
        if new_port and not any("Port " in l for l in updated_host_block):
            updated_host_block.append(f"    Port {new_port}\n")
        if new_identity_file and not any("IdentityFile " in l for l in updated_host_block):
            updated_host_block.append(f"    IdentityFile {new_identity_file}\n")
        updated_host_block.append("\n")
        lines.extend(updated_host_block)

    with open(file_path, "w") as file:
        file.writelines(lines)


def remove_entry(file_path, host_to_remove):
    lines = []
    inside_host = False

    with open(file_path, "r") as file:
        for line in file:
            if line.strip().startswith("Host ") and host_to_remove in line:
                inside_host = True
                continue
            if inside_host and line.startswith("    "):
                continue
            inside_host = False
            lines.append(line)

    with open(file_path, "w") as file:
        file.writelines(lines)


def connect_via_ssh(host):
    """
    Łączy się przez SSH z wybranym hostem, używając danych z wczytanego słownika.
    Wykorzystuje narzędzie ssh dostępne w systemie.
    """
    try:
        print(f"Łączenie z {host['Host']} ({host['HostName']})...")

        # Uruchomienie SSH jako nowy proces
        subprocess.run(f"ssh {host['Host']}", check=True)

    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas łączenia z {host['Host']}: {e}")
    except Exception as e:
        print(f"Błąd: {e}")


def get_user_input(stdscr, prompt, default=""):
    """Pozwala edytować istniejącą wartość, usunąć ją lub pozostawić bez zmian"""
    stdscr.addstr("\n" + prompt + ": ")  # Wyświetlamy labelkę
    stdscr.refresh()

    input_str = list(default)  # Domyślny tekst jako lista znaków (można edytować)
    cursor_x = len(input_str)  # Pozycja kursora

    while True:
        stdscr.move(stdscr.getyx()[0], len(prompt) + 2)  # Przesuwamy kursor za labelkę
        stdscr.clrtoeol()  # Czyścimy tylko wartość, nie labelkę
        stdscr.addstr("".join(input_str))  # Rysujemy wpisywany tekst
        stdscr.move(stdscr.getyx()[0], len(prompt) + 2 + cursor_x)  # Ustawiamy kursor w odpowiednim miejscu
        stdscr.refresh()

        key = stdscr.getch()

        if key in [10, 13]:  # ENTER = akceptacja wartości
            input_val = "".join(input_str).strip()  # Zwracamy wartość z usuniętymi spacjami
            if input_val == "":  # Jeśli pole jest puste, zwracamy pusty ciąg
                return ""
            return input_val  # Jeśli użytkownik wprowadził coś, zwracamy nową wartość
        elif key in [curses.KEY_BACKSPACE, 127, 8]:  # BACKSPACE
            if cursor_x > 0:
                cursor_x -= 1
                input_str.pop(cursor_x)
        elif 32 <= key <= 126:  # Normalne znaki ASCII
            input_str.insert(cursor_x, chr(key))
            cursor_x += 1


def clear_terminal():
    """Czyści ekran terminala po rozłączeniu z SSH."""
    os.system("cls" if os.name == "nt" else "clear")


def get_input(stdscr, prompt):
    stdscr.addstr(prompt)
    stdscr.refresh()

    curses.echo()  # Włącz echo – system sam wyświetli znaki
    user_input = stdscr.getstr().decode("utf-8").strip()  # Pobierz cały wiersz

    if user_input == "":
        return None

    return user_input
