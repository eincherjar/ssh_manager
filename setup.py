from setuptools import setup, find_packages

setup(
    name="ssh-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={"console_scripts": ["ssh-manager=ssh_manager.__main__:main"]},
)
