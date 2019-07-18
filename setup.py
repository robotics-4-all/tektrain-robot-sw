from setuptools import setup, find_packages

REQUIRES = []
NAME = "pidevices"
VERSION = "0.0.1"

DEPENDENCIES = ['pyalsaaudio', 'scipy', 'numpy']

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),

    # Install required packages
    install_requires=REQUIRES,

    # Metadata
    author=" ",
    author_email=" ",
    description="Drivers for sensors and actuators for the raspberry pi board.",
    url=" ", 
)
