import os
import subprocess
import platform
import curses


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


def update_entry(file_path, old_host, new_host_name):
    lines = []
    with open(file_path, "r") as file:
        for line in file:
            if line.strip().startswith("Host ") and old_host in line:
                lines.append(line)
                lines.append(f"    HostName {new_host_name}\n")
            else:
                lines.append(line)

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
    """Uruchamia połączenie SSH z danym hostem"""
    ssh_command = f"ssh {host}"

    if platform.system() == "Windows":
        subprocess.run(["cmd.exe", "/c", ssh_command])
    else:
        subprocess.run(["/bin/bash", "-c", ssh_command])


def change_config_path():
    """Pozwala użytkownikowi zmienić ścieżkę do pliku konfiguracyjnego SSH."""
    new_path = input("Podaj nową ścieżkę do pliku SSH config: ").strip()

    if os.path.isfile(new_path):
        return new_path  # Zwracamy nową ścieżkę
    else:
        print("Błąd: Plik nie istnieje. Spróbuj ponownie.")
        return None  # Jeśli plik nie istnieje, zwracamy None


def get_user_input(stdscr, prompt, default=""):
    """Pobiera wejście od użytkownika w trybie curses"""
    stdscr.addstr(prompt)
    stdscr.addstr(f" ({default}): ", curses.A_DIM)
    stdscr.refresh()

    curses.echo()
    input_str = stdscr.getstr().decode("utf-8").strip()
    curses.noecho()

    return input_str if input_str else default
