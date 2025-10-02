from pybricks.hubs import EssentialHub
from pybricks.parameters import Axis, Button, Direction, Port, Stop
from pybricks.pupdevices import Motor, Remote
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch
from urandom import randint

from config import CHANNEL, REMOTE_NAME

# Set up hub and motors.
hub = EssentialHub(observe_channels=[CHANNEL])
left = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right = Motor(Port.B, Direction.CLOCKWISE)

# Set up drivebase.
robot = DriveBase(left, right, 42, 80)
robot.settings(turn_rate=600)
robot.settings(turn_acceleration=5000)

# If you have only one remote you can omit the name here.
remote = Remote(REMOTE_NAME, timeout=None)

# Reponse timers.
banana = StopWatch()
lava = StopWatch()
boost = StopWatch()

# Initialize variables.
speed = 400


while True:
    # Left wheel
    if Button.LEFT_PLUS in remote.buttons.pressed():
        left.run(speed)
    elif Button.LEFT_MINUS in remote.buttons.pressed():
        left.run(-speed)
    else:
        left.stop()
    # Right wheel
    if Button.RIGHT_PLUS in remote.buttons.pressed():
        right.run(speed)
    elif Button.RIGHT_MINUS in remote.buttons.pressed():
        right.run(-speed)
    else:
        right.stop()
    # state
    if hub.ble.observe(CHANNEL) == 'R' and lava.time() > 3000:
        for count in range(10):
            robot.turn(randint(-40, 40))
        lava.reset()
    if hub.ble.observe(CHANNEL) == 'B':
        boost.reset()
    speed = 750 if boost.time() < 5000 else 400
    # actions
    if hub.ble.observe(CHANNEL) == 'Y' and banana.time() > 1000:
        robot.turn(randint(200, 400))
        banana.reset()
