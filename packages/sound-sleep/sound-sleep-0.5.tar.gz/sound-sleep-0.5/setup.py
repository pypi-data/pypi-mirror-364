# sleep/setup.py
from setuptools import setup, find_packages

setup(
    name="sound-sleep",
    version="0.5",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy"
    ],
    author="Trym Drag-Erlandsen and Therese Barøy Ræder",
    description="Sleep analysis features extractor",
)