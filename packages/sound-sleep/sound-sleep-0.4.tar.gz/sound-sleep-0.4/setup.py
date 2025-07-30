# sleep/setup.py
from setuptools import setup, find_packages

setup(
    name="sound-sleep",
    version="0.4",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy"
    ],
)