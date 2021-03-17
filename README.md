# Arduino EEPROM Programmer

This is a utility to turn your Ben Eater style Arduino EEPROM programmer into a
general-purpose EEPROM programmer.

Unlike the original design you only have to program your Arduino once and then you can
read and write any data to the EEPROM via the serial interface. This is especially
useful if you plan to build a 6502 computer and use your EEPROM to hold your programs.

## Prerequisites

### Hardware

You first need to build your EEPROM programmer circuit on a breadboard.

- Ben Eater's video: <https://www.youtube.com/watch?v=K88pgWhEb1M>
- Schematic here: <https://github.com/beneater/eeprom-programmer>

### Software

- Python >= 3.6,
- [pipx](https://github.com/pipxproject/pipx) (recommended),
- [platformio](https://platformio.org/)

## Installation

### Arduino

The easiest way to program your Arduino is with platformio. No need for the Arduino IDE
or manually install a toolchain.

Install it with pipx:

```sh
pipx install platformio
```

Once installed, plug your Arduino in and do:

```sh
cd arduiono
platformio run -e nano -t upload # for arduino nano
platformio run -e uni -t upload # for arduino uno
```

### PC

Install the Python utility on your PC to send data to the Arduino.

Install it with pipx:

```sh
pipx install eepromino
```

Alternatively:

```sh
pip install eepromino
```

## Usage

```sh
eepromino write mydata
```

Write from standard input:

```sh
cat /dev/urandom | eepromino write -
```

Read the EEPROM:

```sh
eepromino read
```

## Notes

This has only been tested on Linux and with my Arduino Nano.
