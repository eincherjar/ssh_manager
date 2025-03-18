import os


def get_config_path():
    return os.path.expanduser("~/.ssh/config")


def read_hosts(file_path):
    hosts = []
    try:
        with open(file_path, "r") as file:
            current_host = {}
            for line in file:
                line = line.strip()
                if line.startswith("Host "):
                    if current_host:
                        hosts.append(current_host)
                    current_host = {"Host": line.split(" ", 1)[1]}
                elif current_host:
                    key_value = line.split(" ", 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        current_host[key] = value
            if current_host:
                hosts.append(current_host)
    except FileNotFoundError:
        print("Plik konfiguracji SSH nie istnieje.")
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
