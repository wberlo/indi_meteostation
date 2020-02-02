# indi_meteostation
ESP32 based weather station for INDI
My version of an INDI weather station based on the ESP32 wifi board
Sensors:
BME280 for temperature, pressure, humidity and dew point
mlx90614 IR sensor for cloud dettection
All communication is through I2C

The BME280 and mlx90614 library files are unaltered (except an address change in BME280) from their respective creators. I only include them here for completeness. For the newest versions, you will need to download the originals. Information in the headers of the files.

The file main_mini.py is for a miniature version of the weather station. This device will only have an mlx90614 ir temperature sensor for cloud sensing, and a bme280 environmental sensor for pressure, humidity, temperature, and dew point. The code is stripped of all styling, and is to be interpreted by the INDI driver for the Weather Watcher (indilib.org)
