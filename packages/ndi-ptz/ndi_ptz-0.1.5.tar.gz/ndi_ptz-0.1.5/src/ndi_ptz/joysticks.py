from __future__ import annotations


class JoystickConfig:
    def __init__(
        self,
        left_x_axis,
        left_y_axis,
        right_x_axis,
        right_y_axis,
        a_button,
        l_stick,
        r_stick,
        l_bumper,
        r_bumper,
    ) -> None:
        self.left_x_axis = left_x_axis
        self.left_y_axis = left_y_axis
        self.right_x_axis = right_x_axis
        self.right_y_axis = right_y_axis
        self.a_button = a_button
        self.l_stick = l_stick
        self.r_stick = r_stick
        self.l_bumper = l_bumper
        self.r_bumper = r_bumper

    def wrap(self, joystick) -> JoystickWrapper:
        return JoystickWrapper(joystick, self)


class JoystickWrapper:
    def __init__(self, joystick, config: JoystickConfig) -> None:
        self.joystick = joystick
        self.config = config

    def left_x_axis(self) -> float:
        return self.joystick.get_axis(self.config.left_x_axis)

    def left_y_axis(self) -> float:
        return self.joystick.get_axis(self.config.left_y_axis)

    def right_x_axis(self) -> float:
        return self.joystick.get_axis(self.config.right_x_axis)

    def right_y_axis(self) -> float:
        return self.joystick.get_axis(self.config.right_y_axis)

    def a_button(self) -> bool:
        return self.joystick.get_button(self.config.a_button)

    def l_stick(self) -> bool:
        return self.joystick.get_button(self.config.l_stick)

    def r_stick(self) -> bool:
        return self.joystick.get_button(self.config.r_stick)

    def l_bumper(self) -> bool:
        return self.joystick.get_button(self.config.l_bumper)

    def r_bumper(self) -> bool:
        return self.joystick.get_button(self.config.r_bumper)

    def rumble(self, duration: int) -> bool:
        return self.joystick.rumble(
            low_frequency=0.5, high_frequency=0.5, duration=duration
        )

    def rumble_stop(self) -> None:
        return self.joystick.stop_rumble()

    def name(self) -> str:
        return self.joystick.get_name()

    def instance_id(self) -> int:
        return self.joystick.get_instance_id()

    def __enter__(self) -> None:
        self.joystick.init()

    def __exit__(self, _, __, ___) -> None:
        self.joystick.quit()


JOYSTICK_CONFIGURATIONS = {
    "Nintendo Switch Pro Controller": JoystickConfig(
        left_x_axis=0,
        left_y_axis=1,
        right_x_axis=2,
        right_y_axis=3,
        a_button=0,
        l_stick=7,
        r_stick=8,
        l_bumper=9,
        r_bumper=10,
    ),
    "Xbox 360 Controller": JoystickConfig(
        left_x_axis=0,
        left_y_axis=1,
        right_x_axis=3,
        right_y_axis=4,
        a_button=1,  # B Button
        l_stick=8,
        r_stick=9,
        l_bumper=4,
        r_bumper=5,
    ),
    "Xbox Series X Controller": JoystickConfig(
        left_x_axis=0,
        left_y_axis=1,
        right_x_axis=2,
        right_y_axis=3,
        a_button=1,  # B Button
        l_stick=7,
        r_stick=8,
        l_bumper=9,
        r_bumper=10,
    ),
    "Sony Interactive Entertainment Wireless Controller": JoystickConfig(
        left_x_axis=0,
        left_y_axis=1,
        right_x_axis=3,
        right_y_axis=4,
        a_button=1,  # O Button
        l_stick=11,
        r_stick=12,
        l_bumper=4,
        r_bumper=5,
    ),
    "PS4 Controller": JoystickConfig(
        left_x_axis=0,
        left_y_axis=1,
        right_x_axis=2,
        right_y_axis=3,
        a_button=1,  # O Button
        l_stick=7,
        r_stick=8,
        l_bumper=9,
        r_bumper=10,
    ),
}


def wrap(joystick) -> JoystickWrapper | None:
    if not joystick:
        return None

    name = joystick.get_name()
    config = JOYSTICK_CONFIGURATIONS.get(name)
    if not config:
        return None

    return JoystickWrapper(joystick, config)
