#!/usr/bin/env python

from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="eepromino",
    author="George Kettleborough",
    author_email="kettleg@gmail.com",
    url="https://github.com/georgek/eepromino",
    packages=find_packages(exclude=["tests"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=["click>=7", "pyserial>=3", "hexdump"],
    extras_require={"testing": ["pytest"]},
    entry_points={"console_scripts": ["eepromino = eepromino.cli:cli"]},
)
