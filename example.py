from mmWave.sensor import Sensor
from mmWave.IWR6843AOP import IWR6843AOP
from mmWave.utils import load_cfg_file
import asyncio
file = load_cfg_file("./example_configs/20fpsspeedy.cfg")

sensor1 = IWR6843AOP("1", verbose=False)

sensor1.connect_config('/dev/tty.SLAB_USBtoUART4', 115200)
sensor1.connect_data('/dev/tty.SLAB_USBtoUART', 921600)

if not sensor1.send_config(file, max_retries=1):
    print("Sending config failed")
    exit()

sensor1.configure_filtering(.1)

async def print_data(sens: Sensor):
    await asyncio.sleep(2)
    while True:
        print((await sens.get_data()).get())


asyncio.get_event_loop().create_task(sensor1.start_sensor())
asyncio.get_event_loop().create_task(print_data(sensor1))

asyncio.get_event_loop().run_forever()