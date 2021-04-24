pymmWave
====================================
.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

pymmWave is an asynchronous TI mmWave library to expedite mmWave development.

A motivating example:

.. code-block::
   :linenos:

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
            print(await sens.get_data())

    event_loop = get_event_loop()

    event_loop.create_task(sensor1.start_sensor())
    event_loop.create_task(print_data(sensor1))
    event_loop.run_forever()

This simple working example demonstrates how with simple asynchronous integration, realtime applications can integrate with mmWave sensors easily.

This library was designed to work with the commercial off-the-shelf (COTS) TI IWR6843AOPEVM. While TI does provide a web interface to this product, there were no straightforward Python implementations available.

The goal of this library is such that if you purchase this EVM, within minutes of unboxing, it should be hackable in Python.

Install
========

.. code-block::

    pip install numpy scipy pyserial

    pip install pymmwave


Roadmap
========

Currently, this is a simple library providing low-overhead integration with COTS sensors.

The goal is to provide a set of useful RADAR optimized algorithms to expedite research and development. These applications will rely on the abstract Sensor implementations listed below, such that they can be used by developers writing custom RADAR sensor implementations.

We currently do not modify the firmware of the TI RADAR sensors and have no intention to provide support for this. While this tool can be easily modified for custom firmware, that is not the intention.

Contributors
=============
Thanks to the University of California, Santa Barbara, and AeroVironment for providing the backing for this tools creation.

Notably, Jackie Burd, Tiffany Cowan, Peter Feghali, Yogananda Isukapalli, Cher Lin, Swetha Pillai, Scott Rasmussen, and Phil Tokumaru.

IWR6843AOPEVM Implementation
============================
.. automodule:: mmWave.IWR6843AOP
    :members:

Abstract Sensor Class
=====================
.. automodule:: mmWave.sensor
    :members:


Data Model
==================
.. automodule:: mmWave.data_model
    :members:

Utilities
==================
.. automodule:: mmWave.utils
    :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
