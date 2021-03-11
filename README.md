# Arduino EEPROM Programmer

This is a utility to turn your Ben Eater style Arduino EEPROM programmer into a
general-purpose EEPROM programmer.

Unlike the original design you only have to program your Arduino once and then you can
read and write any data to the EEPROM via the serial interface. This is especially
useful if you plan to build a 6502 computer and use your EEPROM to hold your programs.

## Installation

Recommended (using [pipx](https://github.com/pipxproject/pipx)):

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

You need this on your Arduino: <https://github.com/georgek/arduino>

Ben Eater's video on how to make the EEPROM programmer on a breadboard:
<https://www.youtube.com/watch?v=K88pgWhEb1M>
