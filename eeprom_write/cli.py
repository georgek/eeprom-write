import click
import serial
import time

DEVICE = "/dev/ttyUSB0"
BAUD = 57600


def error(message: str) -> None:
    click.secho(message, fg="red", err=True)


def important(message: str) -> None:
    click.secho(message, fg="yellow", err=True)


def success(message: str) -> None:
    click.secho(message, fg="green", err=True)


def info(message: str) -> None:
    click.secho(message, fg="blue", err=True)


def echo(message: str) -> None:
    click.secho(message, err=True)


@click.command()
@click.argument("data", type=click.File("rb"))
@click.version_option()
def cli(data):
    """
    Write to the Arduino EEPROM programmer
    """
    data_bytes = data.read(2048)
    data_bytes += bytes(2048 - len(data_bytes))

    with serial.Serial(DEVICE, BAUD, parity="N", timeout=1) as ser:
        # wait for the Arduino to initialise and echo the start value
        info("Initialising Arduino...")
        INIT_DATA = b"\x4f"
        while True:
            ser.write(INIT_DATA)
            if ser.read(1) == INIT_DATA:
                break
        info("Done.")
        echo("")

        important("Writing EEPROM...")
        with click.progressbar(data_bytes) as bar:
            for data_byte in bar:
                data_byte = data_byte.to_bytes(1, "big")
                ser.write(data_byte)
                incoming = ser.read(1)
                if incoming != data_byte:
                    error(f"Wrong byte (wanted {data_byte}, got {incoming})")
                    return 1

        important("Verifying contents...")
        with click.progressbar(data_bytes) as bar:
            for data_byte in bar:
                data_byte = data_byte.to_bytes(1, "big")
                incoming = ser.read(1)
                if incoming != data_byte:
                    error(f"Wrong byte (wanted {data_byte}, got {incoming})")
                    # return 2

    success("Done.")
