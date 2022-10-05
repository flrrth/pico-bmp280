# https://github.com/flrrth/pico-bmp280

from .bmp280 import BMP280, BMP280Configuration


class BMP280I2C(BMP280):
    """The I2C implementation for the BMP280."""

    def __init__(self, address, i2c, configuration=BMP280Configuration()):
        self._address = address
        self._i2c = i2c
        super().__init__(configuration)
        self._read_compensation_parameters()
        
    def _write(self, register, txdata):
        self._i2c.writeto_mem(self._address, register, txdata)
        
    def _read(self, register, nbytes):        
        return self._i2c.readfrom_mem(self._address, register, nbytes)
