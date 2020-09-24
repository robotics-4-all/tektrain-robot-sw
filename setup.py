from setuptools import setup, find_packages, Extension

REQUIRES = []
NAME = "pidevices"
VERSION = "0.0.1"

DEPENDENCIES = ['pyalsaaudio==0.8.4', 'picamera==1.13', 
                'rpi-ws281x==4.2.2', 'pygame==1.9.6', 
                'evdev==1.2.0', 'omxplayer-wrapper==0.3.2',
                'RPi.GPIO==0.7.0', 'smbus2==0.2.3',
                'python-periphery==1.1.2', 'spidev==3.4','pigpio==1.44']

vl53l1x_path = 'pidevices/sensors/vl53l1x/'
extension = Extension(
    'vl53l1x_python',
    define_macros=[],
    extra_compile_args=['-std=c99'],
    include_dirs=[vl53l1x_path, 
                  vl53l1x_path + 'api/core',
                  vl53l1x_path + 'api/platform'],
    libraries=[],
    library_dirs=[],
    sources=[vl53l1x_path + 'api/core/vl53l1_api_calibration.c',
             vl53l1x_path + 'api/core/vl53l1_core.c',
             vl53l1x_path + 'api/core/vl53l1_core_support.c',
             vl53l1x_path + 'api/core/vl53l1_api_core.c',
             vl53l1x_path + 'api/core/vl53l1_api_preset_modes.c',
             vl53l1x_path + 'api/core/vl53l1_silicon_core.c',
             vl53l1x_path + 'api/core/vl53l1_register_funcs.c',
             vl53l1x_path + 'api/core/vl53l1_wait.c',
             vl53l1x_path + 'api/core/vl53l1_error_strings.c',
             vl53l1x_path + 'api/core/vl53l1_api_strings.c',
             vl53l1x_path + 'api/core/vl53l1_api.c',
             vl53l1x_path + 'api/platform/vl53l1_platform.c',
             vl53l1x_path + 'python_lib/vl53l1x_python.c'])

# Build vl531l
# Lib sdl install

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),

    # Install required packages
    install_requires=DEPENDENCIES,
    ext_modules=[extension],

    # Metadata
    author="Iasonas Paraskevopoulos",
    author_email="iaswnparaskev@gmail.com",
    description="Drivers for sensors and actuators for the raspberry pi board.",
    url=" ", 
)
