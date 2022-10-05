# https://github.com/flrrth/pico-bmp280

from .bmp280 import BMP280, BMP280Configuration


class BMP280SPI(BMP280):
    """The SPI implementation for the BMP280."""

    def __init__(self, spi, cs, configuration=BMP280Configuration()):        
        self._cs = cs
        self._spi = spi
        super().__init__(configuration)
        self._read_compensation_parameters()

    def _write(self, register, txdata):
        buffer = bytearray(len(txdata) + 1)
        buffer[0] = register & 0x7f  # Set the first bit to 0 so the BMP280 knows it's a write operation

        for index, byte in enumerate(txdata):
            buffer[index + 1] = byte

        self._cs.value(0)
        self._spi.write(buffer)
        self._cs.value(1)
        
    def _read(self, register, nbytes):        
        rxdata = bytearray(1 + nbytes)
        self._cs.value(0)
        self._spi.readinto(rxdata, register)
        self._cs.value(1)
        return rxdata[1:]
