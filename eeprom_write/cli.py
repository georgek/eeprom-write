import click
import serial


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
        raise click.BadParameter(
            "Please give padding in padded hex, e.g. '00'"
        )

    return padding


@click.command()
@click.argument("data", type=click.File("rb"))
@click.option(
    "-d",
    "--device",
    type=click.Path(exists=True),
    default="/dev/ttyUSB0",
    show_default=True,
)
@click.option("-b", "--baud", type=int, default=57600, show_default=True)
@click.option(
    "-p",
    "--pad-byte",
    type=str,
    default="00",
    callback=validate_hex_padding,
    show_default=True,
)
@click.version_option()
def cli(data, device, baud, pad_byte):
    """
    Write to the Arduino EEPROM programmer
    """
    data_bytes = data.read(2048)
    info(f"Writing {len(data_bytes)} bytes ")

    if len(data_bytes) < 2048:
        important(f"Padding to 2048 bytes with 0x{pad_byte.hex()}")
    elif data.read():
        important("Input truncated!")
    info("")

    data_bytes += bytes(2048 - len(data_bytes))

    with serial.Serial(device, baud, parity="N", timeout=1) as ser:
        # wait for the Arduino to initialise and echo the start value
        info("Initialising Arduino...")
        INIT_DATA = b"\x4f"
        while True:
            click.echo(".", nl=False)
            ser.write(INIT_DATA)
            if ser.read(1) == INIT_DATA:
                break
        info("\nDone.\n")

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
            for i, data_byte in enumerate(bar):
                data_byte = data_byte.to_bytes(1, "big")
                incoming = ser.read(1)
                if incoming != data_byte:
                    error(f"Wrong byte at {i} (expect {data_byte}, got {incoming})")
                    return 2

    success("\nDone.")
