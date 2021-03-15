import click
import serial
from hexdump import hexdump

READ_CMD_BYTE = b"\x3f"
WRITE_CMD_BYTE = b"\x4f"


class EepromWriteException(click.ClickException):
    exit_code = 1


class EepromVerifyException(click.ClickException):
    exit_code = 2


def error(message: str, *args, **kwargs) -> None:
    click.secho(message, fg="red", err=True, *args, **kwargs)


def important(message: str, *args, **kwargs) -> None:
    click.secho(message, fg="yellow", err=True, *args, **kwargs)


def success(message: str, *args, **kwargs) -> None:
    click.secho(message, fg="green", err=True, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    click.secho(message, fg="blue", err=True, *args, **kwargs)


def echo(message: str, *args, **kwargs) -> None:
    click.secho(message, err=True, *args, **kwargs)


def validate_hex_padding(ctx, params, value):
    try:
        padding = bytes.fromhex(value)
        if len(padding) != 1:
            raise click.BadParameter("Only one byte can be provided")
    except ValueError:
        raise click.BadParameter("Please give padding in padded hex, e.g. '00'")

    return padding


@click.group()
@click.option(
    "-d",
    "--device",
    type=click.Path(exists=True),
    default="/dev/ttyUSB0",
    show_default=True,
)
@click.option("-b", "--baud", type=int, default=57600, show_default=True)
@click.version_option()
@click.pass_context
def cli(ctx, device, baud):
    """
    Interface with the Arduino EEPROM programmer
    """
    ctx.ensure_object(dict)
    ctx.obj["device"] = device
    ctx.obj["baud"] = baud


@cli.command()
@click.pass_context
def read(ctx):
    """
    Read from the Arduino EEPROM programmer
    """
    device = ctx.obj["device"]
    baud = ctx.obj["baud"]

    with serial.Serial(device, baud, timeout=5) as ser:
        initialise_arduino(ser, READ_CMD_BYTE)
        data = read_eeprom(ser)
        click.echo(hexdump(data))


@cli.command()
@click.argument("data", type=click.File("rb"))
@click.option(
    "-p",
    "--pad-byte",
    type=str,
    default="00",
    callback=validate_hex_padding,
    show_default=True,
)
@click.pass_context
def write(ctx, data, pad_byte):
    """
    Write to the Arduino EEPROM programmer
    """
    device = ctx.obj["device"]
    baud = ctx.obj["baud"]

    data_bytes = data.read(2048)
    info(f"Writing {len(data_bytes)} bytes ")

    if len(data_bytes) < 2048:
        important(f"Padding to 2048 bytes with 0x{pad_byte.hex()}")
    elif data.read(1):
        important("Input truncated!")
    info("")

    data_bytes += pad_byte * (2048 - len(data_bytes))

    with serial.Serial(device, baud, timeout=1) as ser:
        initialise_arduino(ser, WRITE_CMD_BYTE)
        write_eeprom(ser, data_bytes)
        verify_eeprom(ser, data_bytes)

    success("\nDone.")


def initialise_arduino(ser, init_byte):
    """Wait for the Arduino to initialise and echo the command value

    The retrying is necessary because when the Arduino resets the serial interface takes
    a while before it's ready. All bytes written will be lost until it's ready.

    """
    info("Initialising Arduino", nl=False)
    old_timeout = ser.timeout
    ser.timeout = 1
    while True:
        ser.write(init_byte)
        if ser.read(1) == init_byte:
            break
        info(".", nl=False)
    info("\nDone.\n")
    ser.timeout = old_timeout


def write_eeprom(ser, data_bytes):
    """Write data_bytes to the interface"""
    important("Writing data to EEPROM...")
    with click.progressbar(data_bytes) as bar:
        for data_byte in bar:
            data_byte = data_byte.to_bytes(1, "big")
            ser.write(data_byte)
            incoming = ser.read(1)
            if incoming != data_byte:
                raise EepromWriteException(
                    f"Wrong byte (wanted {data_byte}, got {incoming})"
                )


def verify_eeprom(ser, data_bytes):
    """Verify incmoing data from the interface"""
    important("Verifying contents...")
    with click.progressbar(data_bytes) as bar:
        for i, data_byte in enumerate(bar):
            data_byte = data_byte.to_bytes(1, "big")
            incoming = ser.read(1)
            if incoming != data_byte:
                raise EepromVerifyException(
                    f"Wrong byte at {i} (expect {data_byte}, got {incoming})"
                )


def read_eeprom(ser):
    """Read all bytes from EEPROM"""
    important("Reading contents...")
    return ser.read(2048)
