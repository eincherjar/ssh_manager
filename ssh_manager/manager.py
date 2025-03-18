import re
import os
import platform
import getpass
import subprocess


# Funkcja do uzyskania ścieżki do pliku konfiguracyjnego
def get_config_path():
    if platform.system() == "Windows":
        # Uzyskaj nazwę użytkownika
        user_name = getpass.getuser()
        # Proponowana domyślna ścieżka
        default_path = f"C:/Users/{user_name}/.ssh/config"
        # Sprawdź, czy plik istnieje w domyślnej lokalizacji
        if os.path.exists(default_path):
            return default_path
        else:
            print(f"Plik {default_path} nie istnieje.")
            # Zapytaj o lokalizację pliku
            file_path = input("Podaj ścieżkę do pliku konfiguracyjnego: ")
            return file_path
    else:
        return os.path.expanduser("~/.ssh/config")


# Funkcja do dodawania nowego wpisu do pliku konfiguracyjnego
def add_entry(file_path):
    print("\nDodawanie nowego hosta (wpisz 0, aby anulować)\n")

    host = input("Podaj nazwę Host: ")
    if host == "0":
        return  # Powrót do menu

    host_name = input("Podaj HostName: ")
    if host_name == "0":
        return

    user = input("Podaj User (opcjonalne): ")
    if user == "0":
        return

    port = input("Podaj Port (opcjonalne): ")
    if port == "0":
        return

    identity_file = input("Podaj IdentityFile (opcjonalne): ")
    if identity_file == "0":
        return

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

    # Przeładuj widok i wyświetl listę hostów
    load_and_display_hosts(file_path)


# Funkcja do edytowania wpisu do pliku konfiguracyjnego
def edit_entry(file_path):
    hosts_data = []
    with open(file_path, "r") as file:
        current_host = []
        for line in file:
            if line.strip():
                if line.strip().startswith("Host "):
                    if current_host:
                        hosts_data.append(current_host)
                    current_host = [line]
                else:
                    current_host.append(line)
        if current_host:
            hosts_data.append(current_host)

    print("\nDostępne hosty do edycji:")
    for idx, host_lines in enumerate(hosts_data, start=1):
        print(f"{idx}. {host_lines[0].strip()}")

    print("0. Powrót do menu")

    try:
        choice = input("Wybierz numer hosta do edycji (lub 0, aby wrócić): ")
        if choice == "0":
            return  # Powrót do menu

        choice = int(choice)
        if 1 <= choice <= len(hosts_data):
            selected_host = hosts_data[choice - 1]
            print("\nAktualne dane hosta:")

            # Parsowanie danych hosta do edycji
            host_dict = {}
            for line in selected_host:
                key_value = line.strip().split(maxsplit=1)
                if len(key_value) == 2:
                    key, value = key_value
                    host_dict[key] = value

            # Pobieranie nowych wartości (lub pozostawienie starych)
            print("Pozostaw puste, aby nie zmieniać danej wartości.")
            new_host = input(f"Host ({host_dict.get('Host', '')}): ").strip() or host_dict.get("Host", "")
            new_host_name = input(f"HostName ({host_dict.get('HostName', '')}): ").strip() or host_dict.get("HostName", "")
            new_user = input(f"User ({host_dict.get('User', '')}): ").strip() or host_dict.get("User", "")
            new_port = input(f"Port ({host_dict.get('Port', '')}): ").strip() or host_dict.get("Port", "")
            new_identity_file = input(f"IdentityFile ({host_dict.get('IdentityFile', '')}): ").strip() or host_dict.get("IdentityFile", "")

            # Aktualizacja danych hosta
            updated_host = [f"Host {new_host}\n", f"  HostName {new_host_name}\n"]
            if new_user:
                updated_host.append(f"  User {new_user}\n")
            if new_port:
                updated_host.append(f"  Port {new_port}\n")
            if new_identity_file:
                updated_host.append(f"  IdentityFile {new_identity_file}\n")

            # Podmiana w liście hostów
            hosts_data[choice - 1] = updated_host

            # Zapis do pliku
            with open(file_path, "w") as file:
                for idx, host_lines in enumerate(hosts_data):
                    file.writelines(host_lines)
                    if idx < len(hosts_data) - 1:
                        file.write("\n\n")  # Zachowanie formatowania

            print("Host został zaktualizowany.")

        else:
            print("Nieprawidłowy wybór.")
    except ValueError:
        print("Wprowadź numer hosta.")

    load_and_display_hosts(file_path)


# Funkcja do usuwania wpisu hosta
def remove_entry(file_path):
    hosts_data = []
    with open(file_path, "r") as file:
        current_host = []
        for line in file:
            if line.strip():
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

    print("0. Powrót do menu")

    try:
        choice = input("\nWybierz numer hosta do usunięcia (lub 0, aby wrócić): ")
        if choice == "0":
            return  # Powrót do menu

        choice = int(choice)  # Konwersja na liczbę
        if 1 <= choice <= len(hosts_data):
            del hosts_data[choice - 1]
            with open(file_path, "w") as file:
                for idx, host_lines in enumerate(hosts_data):
                    file.writelines(host_lines)
                    if idx < len(hosts_data) - 1:  # Dodaj dwie linie odstępu po każdym wpisie, oprócz ostatniego
                        file.write("\n\n")
            print("Host został usunięty.")
        else:
            print("Nieprawidłowy wybór.")
    except ValueError:
        print("Wprowadź numer hosta.")

    load_and_display_hosts(file_path)


def connect_via_ssh(file_path):
    hosts_data = []
    with open(file_path, "r") as file:
        current_host = []
        for line in file:
            if line.strip():
                if line.strip().startswith("Host "):
                    if current_host:
                        hosts_data.append(current_host)
                    current_host = [line]
                else:
                    current_host.append(line)
        if current_host:
            hosts_data.append(current_host)

    print("\nDostępne hosty do połączenia:")
    for idx, host_lines in enumerate(hosts_data, start=1):
        print(f"{idx}. {host_lines[0].strip()}")

    print("0. Powrót do menu")

    try:
        choice = input("\nWybierz numer hosta do połączenia (lub 0, aby wrócić): ")
        if choice == "0":
            return  # Powrót do menu

        choice = int(choice)
        if 1 <= choice <= len(hosts_data):
            selected_host = hosts_data[choice - 1]
            host_dict = {}

            for line in selected_host:
                key_value = line.strip().split(maxsplit=1)
                if len(key_value) == 2:
                    key, value = key_value
                    host_dict[key] = value

            ssh_command = f"ssh {host_dict.get('Host')}"
            print(f"\nŁączenie z {host_dict.get('Host')}...")

            # Uruchomienie SSH
            subprocess.run(ssh_command, shell=True)

        else:
            print("Nieprawidłowy wybór.")
    except ValueError:
        print("Wprowadź numer hosta.")


# Funkcja do załadowania i wyświetlenia hostów
def load_and_display_hosts(file_path):
    # Słownik do przechowywania danych Hostów
    hosts_data = []

    print("\n")
    # Otwórz plik i przetwórz jego zawartość
    with open(file_path, "r") as file:
        current_host = {}
        for line in file:
            # Ignoruj puste linie
            if line.strip():
                # Wyszukaj Host
                host_match = re.match(r"^\s*Host\s+(.*)$", line)
                if host_match:
                    if current_host:
                        hosts_data.append(current_host)
                    current_host = {"Host": host_match.group(1)}
                # Wyszukaj HostName, User, Port i IdentityFile
                for key in ["HostName", "User", "Port", "IdentityFile"]:
                    match = re.match(rf"^\s*{key}\s+(.*)$", line)
                    if match:
                        current_host[key] = match.group(1)
        if current_host:
            hosts_data.append(current_host)

    # Znajdź maksymalne szerokości kolumn
    max_widths = {"Nr": len("Nr"), "Host": len("Host"), "HostName": len("HostName"), "User": len("User"), "Port": len("Port"), "IdentityFile": len("IdentityFile")}
    for host in hosts_data:
        max_widths["Nr"] = max(max_widths["Nr"], len(str(len(hosts_data))))
        max_widths["Host"] = max(max_widths["Host"], len(host["Host"]))
        max_widths["HostName"] = max(max_widths["HostName"], len(host.get("HostName", "")))
        max_widths["User"] = max(max_widths["User"], len(host.get("User", "")))
        max_widths["Port"] = max(max_widths["Port"], len(host.get("Port", "")))
        max_widths["IdentityFile"] = max(max_widths["IdentityFile"], len(host.get("IdentityFile", "")))

    # Dodaj odstępy po 2 spacje z lewej i prawej strony
    for key in max_widths:
        max_widths[key] += 4

    # Wyświetl dane Hostów w formie tabeli z numerem porządkowym
    headers = ["Nr", "Host", "HostName", "User", "Port", "IdentityFile"]
    print(
        f"+{'-' * max_widths['Nr']}+{'-' * max_widths['Host']}+{'-' * max_widths['HostName']}+{'-' * max_widths['User']}+{'-' * max_widths['Port']}+{'-' * max_widths['IdentityFile']}+"
    )
    print(
        f"| {'Nr'.ljust(max_widths['Nr'] - 2)} | {'Host'.ljust(max_widths['Host'] - 2)} | {'HostName'.ljust(max_widths['HostName'] - 2)} | {'User'.ljust(max_widths['User'] - 2)} | {'Port'.ljust(max_widths['Port'] - 2)} | {'IdentityFile'.ljust(max_widths['IdentityFile'] - 2)} |"
    )
    print(
        f"+{'=' * max_widths['Nr']}+{'=' * max_widths['Host']}+{'=' * max_widths['HostName']}+{'=' * max_widths['User']}+{'=' * max_widths['Port']}+{'=' * max_widths['IdentityFile']}+"
    )
    for idx, host in enumerate(hosts_data, start=1):
        if "Host" in host and "HostName" in host:
            print(
                f"| {str(idx).ljust(max_widths['Nr'] - 2)} | {host['Host'].ljust(max_widths['Host'] - 2)} | {host['HostName'].ljust(max_widths['HostName'] - 2)} | {host.get('User', '').ljust(max_widths['User'] - 2)} | {host.get('Port', '').ljust(max_widths['Port'] - 2)} | {host.get('IdentityFile', '').ljust(max_widths['IdentityFile'] - 2)} |"
            )
            print(
                f"+{'-' * max_widths['Nr']}+{'-' * max_widths['Host']}+{'-' * max_widths['HostName']}+{'-' * max_widths['User']}+{'-' * max_widths['Port']}+{'-' * max_widths['IdentityFile']}+"
            )


# Główna funkcja programu
def main():
    file_path = get_config_path()
    load_and_display_hosts(file_path)

    while True:
        print("\nOpcje:")
        print("1. Utwórz nowe")
        print("2. Edytuj hosta")
        print("3. Usuń hosta")
        print("4. Podaj ścieżkę do innego pliku config")
        print("0. Zakończ")
        choice = input("Wybierz opcję:  ")

        if choice == "1":
            add_entry(file_path)
        elif choice == "2":
            edit_entry(file_path)
        elif choice == "3":
            remove_entry(file_path)
        elif choice == "4":
            file_path = input("Podaj ścieżkę do pliku konfiguracyjnego (lub 0, aby wrócić): ")
            if file_path == "0":
                continue  # Powrót do menu
            load_and_display_hosts(file_path)
        elif choice == "5":
            connect_via_ssh(file_path)
        elif choice == "0":
            break
        else:
            print("Nieprawidłowy wybór, spróbuj ponownie.")
