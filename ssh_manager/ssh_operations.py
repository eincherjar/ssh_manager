import os
import subprocess
import platform


def get_config_path():
    return os.path.expanduser("~/.ssh/config")


def read_hosts(file_path):
    """Wczytuje listę hostów z pliku konfiguracyjnego SSH."""
    hosts = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.lower().startswith("host "):
                    host_name = line.split(maxsplit=1)[1]  # Pobiera nazwę hosta
                    hosts.append({"Host": host_name})  # Przechowuje tylko nazwę hosta
    except FileNotFoundError:
        print("Plik konfiguracji SSH nie istnieje.")
    except Exception as e:
        print(f"Błąd podczas odczytu pliku: {e}")

    return hosts


def add_entry(file_path, host, host_name):
    with open(file_path, "a") as file:
        file.write(f"\nHost {host}\n")
        file.write(f"    HostName {host_name}\n")


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
