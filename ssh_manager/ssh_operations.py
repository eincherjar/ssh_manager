import os
import re
import subprocess


def get_config_path():
    """Zwraca ścieżkę do pliku konfiguracyjnego SSH"""
    default_path = os.path.expanduser("~/.ssh/config")
    if os.path.exists(default_path):
        return default_path
    else:
        return input("Podaj ścieżkę do pliku SSH config: ")


def read_hosts(file_path):
    """Wczytuje listę hostów z pliku config"""
    hosts = []
    with open(file_path, "r") as file:
        current_host = {}
        for line in file:
            if line.strip():
                match = re.match(r"^\s*(\w+)\s+(.*)$", line)
                if match:
                    key, value = match.groups()
                    if key == "Host":
                        if current_host:
                            hosts.append(current_host)
                        current_host = {"Host": value}
                    else:
                        current_host[key] = value
        if current_host:
            hosts.append(current_host)
    return hosts


def add_entry(file_path, host, host_name, user="", port="", identity_file=""):
    """Dodaje nowy wpis do pliku config"""
    entry = f"\n\nHost {host}\n  HostName {host_name}\n"
    if user:
        entry += f"  User {user}\n"
    if port:
        entry += f"  Port {port}\n"
    if identity_file:
        entry += f"  IdentityFile {identity_file}\n"

    with open(file_path, "a") as file:
        file.write(entry)


def update_entry(file_path, old_host, new_host, new_host_name, new_user, new_port, new_identity_file):
    """Edytuje istniejący wpis w pliku config"""
    hosts = read_hosts(file_path)

    for host in hosts:
        if host["Host"] == old_host:
            host["Host"] = new_host
            host["HostName"] = new_host_name
            if new_user:
                host["User"] = new_user
            if new_port:
                host["Port"] = new_port
            if new_identity_file:
                host["IdentityFile"] = new_identity_file

    with open(file_path, "w") as file:
        for host in hosts:
            file.write(f"\n\nHost {host['Host']}\n  HostName {host['HostName']}\n")
            if "User" in host:
                file.write(f"  User {host['User']}\n")
            if "Port" in host:
                file.write(f"  Port {host['Port']}\n")
            if "IdentityFile" in host:
                file.write(f"  IdentityFile {host['IdentityFile']}\n")


def remove_entry(file_path, host_name):
    """Usuwa wpis hosta z pliku config"""
    hosts = read_hosts(file_path)
    hosts = [host for host in hosts if host["Host"] != host_name]

    with open(file_path, "w") as file:
        for host in hosts:
            file.write(f"\n\nHost {host['Host']}\n  HostName {host['HostName']}\n")
            if "User" in host:
                file.write(f"  User {host['User']}\n")
            if "Port" in host:
                file.write(f"  Port {host['Port']}\n")
            if "IdentityFile" in host:
                file.write(f"  IdentityFile {host['IdentityFile']}\n")


def connect_via_ssh(host):
    """Łączy się z hostem przez SSH"""
    ssh_command = f"ssh {host}"
    print(f"Łączenie z {host}...")
    subprocess.run(ssh_command, shell=True)
