from pybricks.hubs import PrimeHub
from pybricks.pupdevices import ColorLightMatrix
from pybricks.parameters import Color, Port
from pybricks.tools import wait, run_task, multitask

from mario import Mario

from config import CHANNEL, MARIO_TYPE

hub = PrimeHub(broadcast_channel=CHANNEL)
light = ColorLightMatrix(Port.B)

mario = Mario(MARIO_TYPE)


async def main():

    color_last = Color.NONE
    count = 0

    while True:
        color_now = mario.color()
        hub.display.number(count)

        # No change, poll again
        if color_last == color_now:
            await wait(0)
            continue

        # Display and broadcast the detected color.
        letter = repr(color_now)[6]

        await hub.ble.broadcast(letter)
        await light.on(color_now)

        if color_last == Color.GREEN and color_now == Color.VIOLET:
            count -= 1
        if color_last == Color.VIOLET and color_now == Color.GREEN:
            count += 1

        color_last = color_now

        # For no color, go poll again right away
        if color_now in (Color.NONE, Color.GREEN, Color.VIOLET):
            continue

        # For any other color, broadcast the color for some time so the
        # cart is sure to receive it and not immediately get something else.
        await wait(1000)

run_task(multitask(mario.background_task(), main()))
