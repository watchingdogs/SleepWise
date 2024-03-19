from machine import Pin, SPI
from max7219 import Matrix8x8
import time
import ntptime
import cettime
import uasyncio as asyncio
import aiorepl

# This is your configuration. Set the (hour, minute) you want in your countdown.
displayorder = ((7,0), (21,45), (23,15))

spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
display = Matrix8x8(spi, Pin(15), 4)
display.brightness(1)
display.zero()
display.show()


def time_until(timetuple):
    desired_time_seconds = timetuple[0] * 3600 + timetuple[1] * 60
    current_time = cettime.cettime()
    current_time_seconds = time.mktime(current_time)

    midnight_seconds =  time.mktime(current_time[:3] + (0, 0, 0) + current_time[6:]) # hour, minute, second
    assumed_date = midnight_seconds + desired_time_seconds

    if current_time_seconds <= assumed_date: # today or tomorrow
        return assumed_date - current_time_seconds
    else:
        return assumed_date + 86400 - current_time_seconds


def show_remaining(display, time_seconds):
    # Character positions: -1, 7, 12, 17, 25; 12 is for :
    hours = '{:02d}'.format(int(time_seconds / 3600))
    minutes = '{:02d}'.format(int((time_seconds % 3600) / 60))

    display.zero()

    if hours == "00":
        if minutes[0] != "0":
            display.text(minutes[0], 17, 0, 1)
        display.text(minutes[1], 25, 0, 1)
    else:
        if hours[0] != "0":
            display.text(hours[0], -1, 0, 1)
        
        display.text(hours[1], 7, 0, 1)
        display.text(":", 12, 0, 1)
        display.text(minutes[0], 17, 0, 1)
        display.text(minutes[1], 25, 0, 1)

    display.show()

async def main(display, displayorder):
    await asyncio.sleep(5)
    while True:
        try:
            ntptime.settime()

            next_index = min(range(len(displayorder)), key=lambda i: time_until(displayorder[i]))
            remaining_seconds = time_until(displayorder[next_index])
            show_remaining(display, remaining_seconds)

            time_until_next_minute = 60-cettime.cettime()[5]
            await asyncio.sleep(time_until_next_minute)
        except Exception as e:
            print("An error occurred:", e)

loop = asyncio.get_event_loop()

loop.create_task(aiorepl.task())
loop.create_task(main(display, displayorder))

loop.run_forever()
