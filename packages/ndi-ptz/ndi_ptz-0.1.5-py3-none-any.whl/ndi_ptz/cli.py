from importlib.metadata import requires

import click
import time

from click import ClickException
from cyndilib import Finder, Receiver, RecvColorFormat, RecvBandwidth

from ndi_ptz.constants import NDI_R_STRING
from ndi_ptz.joysticks import JOYSTICK_CONFIGURATIONS, wrap
from ndi_ptz._pygame import silent_import_pygame


@click.group(
    epilog=NDI_R_STRING,
)
@click.version_option(
    package_name="ndi-ptz",
    prog_name="ndi-ptz",
    message=f"%(prog)s, version %(version)s\n\n{NDI_R_STRING}",
)
def cli():
    "A CLI to control NDI-capable PTZ cameras via a joystick."
    pass


@click.command()
@click.option(
    "--timeout",
    default=5,
    help="The number of seconds to wait for any NDI sources to be detected",
)
def list_sources(timeout: int):
    click.echo(f"Looking for NDI sources in the next {timeout} seconds", err=True)

    with Finder() as finder:
        if not finder.wait(timeout=timeout):
            raise ClickException(f"No sources detected after {timeout} seconds")

        for source in finder:
            click.echo(source.name)


@click.command()
@click.option(
    "--timeout",
    default=5,
    help="The number of seconds to wait for any joystick to be detected",
)
def list_joysticks(timeout: int):
    click.echo(f"Looking for joysticks in the next {timeout} seconds", err=True)

    pygame = silent_import_pygame()
    pygame.init()
    pygame.joystick.init()
    joysticks = []

    for _ in range(0, timeout):
        joysticks = [
            pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
        ]
        if joysticks:
            break

        time.sleep(1)

    if not joysticks:
        raise ClickException(f"No joysticks detected after {timeout} seconds")

    for joystick in joysticks:
        joystick_name = joystick.get_name()
        supported = joystick_name in JOYSTICK_CONFIGURATIONS.keys()
        unsupported = "" if supported else " (unsupported joystick)"
        click.echo(f"{joystick_name} ({joystick.get_instance_id()}){unsupported}")


@click.command()
@click.option(
    "-j", "--joystick-instance", default=0, help="The instance id of the joystick."
)
@click.option(
    "--joystick-timeout",
    default=5,
    help="The number of seconds to wait for the joystick to be detected.",
)
@click.option("-s", "--source-name", required=True, help="The name of the source.")
@click.option(
    "--source-timeout",
    default=5,
    help="The number of seconds to wait for any NDI sources to be detected.",
)
@click.option(
    "--connect-timeout",
    default=5,
    help="The number of seconds to wait for the connection to the NDI source to establish.",
)
@click.option(
    "-n",
    "--receiver-name",
    default="ndi_ptz",
    help="The name used to identify this program when opening the connection to the NDI source.",
)
@click.option(
    "--motion-threshold",
    default=0.1,
    help="The minimal amount of motion which the joystick must report before it is translated into a PTZ command.",
)
@click.option(
    "--speed-factor",
    default=0.1,
    help="Reduce the reported movement distance of the joystick by this factor before sending it as PTZ command.",
)
@click.option(
    "+r/-r",
    "--rumble/--no-rumble",
    default=True,
    help="Enable the rumble for feedback.",
)
def control(
    joystick_instance: int,
    joystick_timeout: int,
    source_name: str,
    source_timeout: int,
    connect_timeout: int,
    receiver_name: str,
    motion_threshold: float,
    speed_factor: float,
    rumble: bool,
):
    receiver = None
    do_rumble = rumble

    with Finder() as finder:
        if not finder.wait(timeout=source_timeout):
            raise ClickException("No sources detected")

        source = finder.get_source(source_name)

        if not source:
            raise ClickException(f"Source '{source_name}' not found")

        receiver = Receiver(
            color_format=RecvColorFormat.fastest,
            bandwidth=RecvBandwidth.metadata_only,
            recv_name=receiver_name,
        )
        receiver.set_source(source)

        for _ in range(0, connect_timeout * 10):
            time.sleep(0.1)
            if receiver.is_connected():
                break

        if not receiver.is_connected():
            raise ClickException(f"Can't connect to the NDI device '{source_name}'")

        if not receiver.is_ptz_supported():
            raise ClickException(
                f"The NDI source '{source}' does not indicate PTZ support"
            )

    ptz = receiver.ptz

    pygame = silent_import_pygame()
    pygame.init()
    pygame.joystick.init()

    pg_joysticks = []
    pg_joystick = None
    for _ in range(0, 10):
        pg_joysticks = [
            pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
        ]

        if not pg_joysticks:
            time.sleep(1)
            continue

        if joystick_instance > (len(pg_joysticks) - 1):
            continue

        pg_joystick = pg_joysticks[joystick_instance]

    if not pg_joysticks:
        raise ClickException(f"No joysticks detected after {joystick_timeout} seconds")

    if not pg_joystick:
        raise ClickException(
            f"Joystick {joystick_instance} was not detected after {joystick_timeout} seconds"
        )

    joystick = wrap(pg_joystick)
    if not joystick:
        raise ClickException(
            f"Joystick of type {pg_joystick.get_name()} is not yet supported"
        )

    with joystick:
        click.echo(
            f"Using joystick '{joystick.name()}' ({joystick.instance_id()}) "
            f"to control camera '{receiver.source_name}'"
        )
        if do_rumble:
            joystick.rumble(duration=250)

        autofocus_on = False
        home_on = False
        control_on = False

        click.echo("Use L_BUMP and R_BUMP to enable remote control.")
        click.echo("Use L_STICK for pan and tilt, R_STICK for zoom.")
        click.echo("Use BUTTON_A to trigger the autofocus.")
        while True:
            pygame.event.pump()

            rounding = 2
            p2 = round(joystick.left_x_axis() * -1, rounding)
            t2 = round(joystick.left_y_axis() * -1, rounding)
            z2 = round(joystick.right_y_axis() * -1, rounding)

            threshold = motion_threshold
            pan = p2 if p2 < threshold * -1 or threshold < p2 else 0.0
            tilt = t2 if t2 < threshold * -1 or threshold < t2 else 0.0
            zoom = z2 if z2 < threshold * -1 or threshold < z2 else 0.0

            take_control = joystick.l_bumper() and joystick.r_bumper()
            trigger_af = joystick.a_button()
            trigger_home = joystick.l_stick() or joystick.r_stick()

            if not take_control and control_on:
                ptz.pan_and_tilt(0.0, 0.0)
                ptz.zoom(0.0)
                control_on = False
                if do_rumble:
                    joystick.rumble(duration=150)
            elif take_control:
                if not control_on:
                    control_on = True
                    if do_rumble:
                        joystick.rumble(duration=50)

                if not trigger_home:
                    # click.echo(f"Motion p {pan} t {tilt} z {zoom} speed_factor {speed_factor}")
                    ptz.pan_and_tilt(pan * speed_factor, tilt * speed_factor)
                    ptz.zoom(zoom * speed_factor)

                if trigger_home and not home_on:
                    ptz.set_pan_and_tilt_values(0.0, 0.0)
                    ptz.set_zoom_level(0.0)
                    home_on = True
                    if do_rumble:
                        joystick.rumble(duration=0)
                elif not trigger_home and home_on:
                    home_on = False
                    if do_rumble:
                        joystick.rumble_stop()

                if trigger_af and not autofocus_on:
                    ptz.autofocus()
                    autofocus_on = True
                elif not trigger_af and autofocus_on:
                    autofocus_on = False

            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

    pygame.quit()
    receiver.disconnect()


@click.command(hidden=True, name="debug")
def debug_joystick():
    from pygame.locals import (
        JOYAXISMOTION,
        JOYBUTTONDOWN,
        JOYHATMOTION,
        JOYBALLMOTION,
        QUIT,
    )

    pygame = silent_import_pygame()
    pygame.init()
    pygame.joystick.init()

    joysticks = [
        pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())
    ]
    if not joysticks:
        raise ClickException("No joysticks found")

    while True:
        for event in pygame.event.get():
            if event.type == JOYBUTTONDOWN:
                print(f"Button: {event.button}")

            if event.type == JOYAXISMOTION:
                print(f"Axis: {event.axis}")

            if event.type == JOYHATMOTION:
                print(f"Hat: {event.value}")

            if event.type == JOYBALLMOTION:
                print(f"Hat: {event.value}")

            if event.type == QUIT:
                exit(0)


cli.add_command(control)
cli.add_command(list_joysticks)
cli.add_command(list_sources)
cli.add_command(debug_joystick)

if __name__ == "__main__":
    cli()
