from pymmWave.sensor import Sensor
from pymmWave.IWR6843AOP import IWR6843AOP
from asyncio import get_event_loop, sleep
from pymmWave.utils import load_cfg_file
from pymmWave.algos import SimpleMeanDistance, CloudEstimatedIMU, EstimatedRelativePosition
import numpy as np


sensor1 = IWR6843AOP("1", verbose=True)
file = load_cfg_file("./example_configs/20fpsspeedy.cfg")

config_connected = sensor1.connect_config('/dev/tty.SLAB_USBtoUART4', 115200)
if not config_connected:
    print("Config connection failed.")
    exit()
data_connected = sensor1.connect_data('/dev/tty.SLAB_USBtoUART', 921600)
if not data_connected:
    print("Data connection failed.")
    exit()

if not sensor1.send_config(file, max_retries=1):
    print("Sending config failed")
    exit()

sensor1.configure_filtering(.1)

async def print_data(sens: Sensor):
    await sleep(2)

    est_imu = CloudEstimatedIMU()
    pos_est = EstimatedRelativePosition()

    while True:
        dopplercloud_out = await sens.get_data()
        imu_estimate = est_imu.run(dopplercloud_out)
        if imu_estimate is not None:
            p = pos_est.run(imu_estimate)
            print("Estimated pose\t", p.get())

event_loop = get_event_loop()

event_loop.create_task(sensor1.start_sensor()) # type: ignore
event_loop.create_task(print_data(sensor1))
event_loop.run_forever()