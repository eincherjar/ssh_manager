from setuptools import setup, find_packages

setup(
    name="ssh-manager",
    version="0.1.0",
    author="Marcin Barszcz",
    author_email="marcinbarszcz123@gmail.com",
    description="Menedżer konfiguracji SSH w terminalu",
    packages=find_packages(),
    install_requires=["windows-curses; platform_system=='Windows'"],
    entry_points={"console_scripts": ["ssh-manager=ssh_manager.main:run"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
