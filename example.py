from mmWave.sensor import Sensor
from mmWave.IWR6843AOP import IWR6843AOP
from mmWave.constants import EXAMPLE_CONFIG
from asyncio import get_event_loop, sleep

sensor1 = IWR6843AOP("1", verbose=False)

config_connected = sensor1.connect_config('/dev/tty.SLAB_USBtoUART4', 115200)
if not config_connected:
    print("Config connection failed.")
    exit()
data_connected = sensor1.connect_data('/dev/tty.SLAB_USBtoUART', 921600)

if not sensor1.send_config(EXAMPLE_CONFIG, max_retries=1):
    print("Sending config failed")
    exit()

sensor1.configure_filtering(.1)

async def print_data(sens: Sensor):
    await sleep(2)
    while True:
        print((await sens.get_data()).get())

event_loop = get_event_loop()

event_loop.create_task(sensor1.start_sensor()) # type: ignore
event_loop.create_task(print_data(sensor1))
event_loop.run_forever()