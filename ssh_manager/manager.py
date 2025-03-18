import os
import platform
import getpass
import re


# Funkcja do uzyskania ścieżki do pliku konfiguracyjnego
def get_config_path():
    if platform.system() == "Windows":
        user_name = getpass.getuser()
        default_path = f"C:/Users/{user_name}/.ssh/config"
        if os.path.exists(default_path):
            return default_path
        else:
            print(f"Plik {default_path} nie istnieje.")
            return input("Podaj ścieżkę do pliku konfiguracyjnego: ")
    else:
        return os.path.expanduser("~/.ssh/config")


# Funkcja do dodawania nowego hosta
def add_entry(file_path):
    print("\nDodawanie nowego hosta (wpisz 0, aby anulować)\n")

    host = input("Podaj nazwę Host: ")
    if host == "0":
        return

    host_name = input("Podaj HostName: ")
    if host_name == "0":
        return

    user = input("Podaj User (opcjonalne): ")
    port = input("Podaj Port (opcjonalne): ")
    identity_file = input("Podaj IdentityFile (opcjonalne): ")

    entry = f"\n\nHost {host}\n  HostName {host_name}\n"
    if user:
        entry += f"  User {user}\n"
    if port:
        entry += f"  Port {port}\n"
    if identity_file:
        entry += f"  IdentityFile {identity_file}\n"

    with open(file_path, "a") as file:
        file.write(entry)

    print("Wpis został dodany.")
    load_and_display_hosts(file_path)


# Funkcja do wyświetlania listy hostów
def load_and_display_hosts(file_path):
    hosts_data = []
    with open(file_path, "r") as file:
        current_host = {}
        for line in file:
            if line.strip():
                if line.strip().startswith("Host "):
                    if current_host:
                        hosts_data.append(current_host)
                    current_host = {"Host": line.strip().split(" ", 1)[1]}
                else:
                    key_value = line.strip().split(maxsplit=1)
                    if len(key_value) == 2:
                        current_host[key_value[0]] = key_value[1]
        if current_host:
            hosts_data.append(current_host)

    print("\nLista hostów:\n")
    for idx, host in enumerate(hosts_data, start=1):
        print(f"{idx}. {host['Host']} - {host.get('HostName', '')}")


# Funkcja do usuwania wpisu hosta
def remove_entry(file_path):
    hosts_data = []
    with open(file_path, "r") as file:
        current_host = []
        for line in file:
            if line.strip().startswith("Host "):
                if current_host:
                    hosts_data.append(current_host)
                current_host = [line]
            else:
                current_host.append(line)
        if current_host:
            hosts_data.append(current_host)

    print("\nDostępne hosty do usunięcia:")
    for idx, host_lines in enumerate(hosts_data, start=1):
        print(f"{idx}. {host_lines[0].strip()}")

    choice = input("\nWybierz numer hosta do usunięcia (lub 0, aby wrócić): ")
    if choice == "0":
        return

    choice = int(choice)
    if 1 <= choice <= len(hosts_data):
        del hosts_data[choice - 1]
        with open(file_path, "w") as file:
            for host in hosts_data:
                file.writelines(host)
                file.write("\n\n")

        print("Host został usunięty.")
    else:
        print("Nieprawidłowy wybór.")

    load_and_display_hosts(file_path)


# Główna funkcja programu
def main():
    file_path = get_config_path()
    load_and_display_hosts(file_path)

    while True:
        print("\nOpcje:")
        print("1. Utwórz nowe")
        print("2. Usuń hosta")
        print("0. Zakończ")
        choice = input("Wybierz opcję:  ")

        if choice == "1":
            add_entry(file_path)
        elif choice == "2":
            remove_entry(file_path)
        elif choice == "0":
            break
        else:
            print("Nieprawidłowy wybór, spróbuj ponownie.")
