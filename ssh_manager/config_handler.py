import os
import platform
import getpass


def get_config_path():
    if platform.system() == "Windows":
        user_name = getpass.getuser()
        default_path = f"C:/Users/{user_name}/.ssh/config"
    else:
        default_path = os.path.expanduser("~/.ssh/config")

    return default_path if os.path.exists(default_path) else input("Podaj ścieżkę do pliku config: ")
