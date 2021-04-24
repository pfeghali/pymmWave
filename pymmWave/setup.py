# setup.py
from setuptools import setup #type: ignore
from codecs import open
from os import path

__author__ = 'pfeghali'

long_description: str
with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
   name="mmWave",
   version='0.1.2',
   py_modules=['mmWave'],
   description="A TI mmWave RADAR EVM integration library.",
   long_description=long_description,
   long_description_content_type="text/markdown",
   url='',
   author_email='peterfeghali@ucsb.edu',
   include_package_data=True,
#    install_requires=["numpy", "pyserial", "scipy"]
)