#setup.py
from setuptools import setup, find_packages

setup(
    name="PythonHarmlessReverseShell",
    version="0.1.2",
    description="A python/pip package for testing antivirus detection for reverse shells.",
    packages= find_packages(),
    install_requires=[],
    entry_points= {
        'console_scripts': [
            'reverse-shell-client=pythonharmlessreverseshell.main:reverse_shell_client',
        ],
    },
)