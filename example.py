from pymmWave.sensor import Sensor
from pymmWave.IWR6843AOP import IWR6843AOP
from asyncio import get_event_loop, sleep
from pymmWave.utils import load_cfg_file

sensor1 = IWR6843AOP("1", verbose=True)
file = load_cfg_file("./example_configs/20fpsspeedy.cfg")

config_connected = sensor1.connect_config('/dev/tty.SLAB_USBtoUART4', 115200)
if not config_connected:
    print("Config connection failed.")
    exit()
data_connected = sensor1.connect_data('/dev/tty.SLAB_USBtoUART', 921600)

if not sensor1.send_config(file, max_retries=1):
    print("Sending config failed")
    exit()

sensor1.configure_filtering(.1)

async def print_data(sens: Sensor):
    await sleep(2)
    while True:
        print(await sens.get_data())

event_loop = get_event_loop()

event_loop.create_task(sensor1.start_sensor()) # type: ignore
event_loop.create_task(print_data(sensor1))
event_loop.run_forever()