from setuptools import setup

setup(
    name="ssh-manager",
    version="1.0.0",
    py_modules=["ssh_manager"],
    entry_points={"console_scripts": ["ssh-manager=ssh_manager:main"]},
)
