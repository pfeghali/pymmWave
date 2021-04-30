pymmWave
====================================
.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

pymmWave is an asynchronous TI mmWave library to expedite mmWave development.

A motivating example:

First get the serial ports which your sensor is using.

.. code-block:: console

    $ ls /dev/tty.*
    ... /dev/tty.SLAB_USBtoUART4     /dev/tty.SLAB_USBtoUART


Insert the serial ports to the config and data arguments, and thats it!

The connection may timeout on connect_config or connect_data. The function also may timeout on a read or write after supposedly connecting to the device. If this occurs, verify your serial port configuration, as they may need to be swapped. On Windows, this can be viewed on device manager. This currently may fail on WSL due to their serial support, but this may change.

.. code-block::
   :linenos:

    from pymmWave.utils import load_cfg_file
    from pymmWave.sensor import Sensor
    from pymmWave.IWR6843AOP import IWR6843AOP
    from asyncio import get_event_loop, sleep

    sensor1 = IWR6843AOP("1", verbose=False)
    file = load_cfg_file("./example_configs/20fpsspeedy.cfg")

    # Your CONFIG serial port name
    config_connected = sensor1.connect_config('/dev/tty.SLAB_USBtoUART4', 115200)
    if not config_connected:
        print("Config connection failed.")
        exit()

    # Your DATA serial port name
    data_connected = sensor1.connect_data('/dev/tty.SLAB_USBtoUART', 921600)
    if not data_connected:
        print("Data connection failed.")
        exit()

    if not sensor1.send_config(file, max_retries=1):
        print("Sending configuration failed")
        exit()

    # Sets up doppler filtering to remove static noise
    sensor1.configure_filtering(.05)

    # Basic class to print data from the sensor
    async def print_data(sens: Sensor):
        await sleep(2)
        while True:
            print(await sens.get_data()) # get_data() -> DopplerPointCloud.

    event_loop = get_event_loop()

    event_loop.create_task(sensor1.start_sensor())
    event_loop.create_task(print_data(sensor1))
    event_loop.run_forever()

This simple working example demonstrates how with simple asynchronous integration, realtime applications can integrate with TI mmWave sensors easily.

This library was designed to work with the commercial off-the-shelf (COTS) TI IWR6843AOPEVM. While TI does provide a web interface to this product, there were no straightforward Python implementations available.

The goal of this library is such that if you purchase this EVM, within minutes of unboxing, it should be hackable in Python. This library is designed to scale with your use case. In future versions, it will support various algorithms reliant on the abstract implementations presented.

It should be noted that this package requires python >3.9. This is solely due to type hinting. It should be simple to clone the github, and modify the package to support `typing` classes. We expect this can be accomplished with Python >3.7, though there are no plans to modify the library to support this use-case.

Version 1.1.0 brings a number of simple algorithms. This now supports generic algorithms, and presents some simple, non-optimized algorithms. These algorithms allow for pose estimation, mocking an IMU, and a simple point cloud mean.


Install
========

.. code-block::

    pip install numpy scipy pyserial

    pip install pymmwave


Roadmap
========

Currently, this is a simple library providing low-overhead integration with COTS TI mmWave sensors.

The goal is to provide a set of useful RADAR optimized algorithms to expedite research and development. These applications will rely on the abstract Sensor implementations listed below, such that they can be used by developers writing custom RADAR sensor implementations.

We currently do not modify the firmware of the TI RADAR sensors and have no intention to provide support for this. While this tool can be easily modified for custom firmware, that is not the intention of this tool.

We are aware that the COTS firmware can return more data than simply point cloud data, and we intend to support this use case in the future.

Contributors
=============
Thanks to the University of California, Santa Barbara, and AeroVironment for providing the backing for this tools creation.

Notably, Jackie Burd, Tiffany Cowan, Peter Feghali, Yogananda Isukapalli, Cher Lin, Swetha Pillai, Scott Rasmussen, and Phil Tokumaru.

IWR6843AOPEVM Implementation
============================
.. automodule:: pymmWave.IWR6843AOP
    :members:

Abstract Sensor Class
=====================
.. automodule:: pymmWave.sensor
    :members:

Algorithms
==================
.. automodule:: pymmWave.algos
    :members:

Logging
==================
.. automodule:: pymmWave.logging
    :members:

Data Model
==================
.. automodule:: pymmWave.data_model
    :members:

Utilities
==================
.. automodule:: pymmWave.utils
    :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
