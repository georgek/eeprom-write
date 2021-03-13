#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="eepromino",
    author="George Kettleborough",
    author_email="kettleg@gmail.com",
    url="https://github.com/georgek/eepromino",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    install_requires=["click>=7", "pyserial>=3", "hexdump"],
    extras_require={"testing": ["pytest"]},
    entry_points={"console_scripts": ["eepromino = eepromino.cli:cli"]},
)
