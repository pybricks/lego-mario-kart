from pybricks.iodevices import LWP3Device
from pybricks.parameters import Color
from pybricks.tools import StopWatch, wait

from micropython import const
from ustruct import unpack

HUB_ID_MARIO = const(0x43)
HUB_ID_LUIGI = const(0x44)
HUB_ID_PEACH = const(0x45)  # Unconfirmed, untested

PORT_VALUE_MSG = const(0x45)
PORT_COLOR_SENSOR = const(0x01)
MODE_RGB = const(0x01)

RGB_MAX_V = const(220)


def rgb_to_hsv(r, g, b):

    if r > RGB_MAX_V:
        r = RGB_MAX_V
    if g > RGB_MAX_V:
        g = RGB_MAX_V
    if b > RGB_MAX_V:
        b = RGB_MAX_V

    rgb_max = max([r, g, b])
    rgb_min = min([r, g, b])
    chroma = rgb_max - rgb_min

    h = 0
    s = 0
    v = rgb_max * 100 // RGB_MAX_V

    if chroma > 0:

        if rgb_max == r:
            x = g
            y = b
            z = 0
        elif rgb_max == g:
            x = b
            y = r
            z = 120
        else:
            x = r
            y = g
            z = 240
        h = 60 * (x - y) // chroma + z
        if h < 0:
            h += 360
        s = 100 * chroma // rgb_max

    return h, s, v


def hsv_to_color(hsv):

    h, s, v = hsv

    if s < 15 or v < 30:
        return Color.NONE

    if h > 330 or h < 20:
        return Color.RED
    if h < 75:
        return Color.YELLOW
    if h < 190:
        return Color.GREEN
    if h < 250 and s > 60:
        return Color.BLUE
    if s < 50:
        return Color.VIOLET

    return Color.NONE


class Mario():
    """Class to connect to the Duplo train and send commands to it."""

    def __init__(self, hub_type, pair):
        print(f"Searching for the {hub_type} Hub. Make sure it is on and in pairing mode.")

        if hub_type == "MARIO":
            hub_id = HUB_ID_MARIO
        elif hub_type == "LUIGI":
            hub_id = HUB_ID_LUIGI
        elif hub_type == "PEACH":
            hub_id = HUB_ID_PEACH
        else:
            raise ValueError("Invalid Hub")

        self.device = LWP3Device(hub_id, name=None, timeout=None, num_notifications=2, pair=pair)

        # Subscribe to color sensor RGB
        self.device.write(bytes([0x0a, 0x00, 0x41, PORT_COLOR_SENSOR, MODE_RGB, 0x01, 0x00, 0x00, 0x00, 0x01]))

        self.hsv = (0, 0, 0)
        self.color_last = Color.NONE
        self.color_stable = Color.NONE
        self.color_count = 0
        self.timer = StopWatch()
        self.last_color_time = 0

        print("Connected!")

    def parse_input(self):

        # Go through all buffered LWP3 notifications
        while (data := self.device.read()) is not None:

            # Skip non-port data.
            if len(data) < 4 or data[2] != PORT_VALUE_MSG:
                continue

            # Skip data that that doesn't look like color sensor values.
            if data[3] != PORT_COLOR_SENSOR or len(data) != 7:
                continue

            # Convert instantaneous measurement to HSV
            r, g, b = unpack("<BBB", data[4:7])
            self.hsv = rgb_to_hsv(r, g, b)
            measured_color = hsv_to_color(self.hsv)

            # Keep track of color over time for better stability
            self.timer.reset()
            if measured_color == self.color_last:
                self.color_count += 1
            else:
                self.color_last = measured_color
                self.color_count = 0

            if self.color_count > 0:
                self.color_stable = self.color_last

    def color(self):
        # Counting successive matches increases confidence, but if measurements
        # are stationary we get no new data, which also means it is stable.
        if self.timer.time() > 100:
            self.color_stable = self.color_last
        return self.color_stable

    async def background_task(self):
        while True:
            self.parse_input()
            await wait(0)
