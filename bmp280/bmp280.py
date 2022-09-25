from machine import Pin, SPI
from ustruct import unpack
from utime import sleep, sleep_ms

from .bmp280_configuration import BMP280Configuration


class BMP280:

    def __init__(self, spi, cs, configuration=BMP280Configuration()):
        self._cs = cs
        self._spi = spi
        self._read_compensation_parameters()
        self.configuration = configuration

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, configuration):
        self._configuration = configuration
        self.reset()
        self.write_ctrl_meas()
        self.write_config()

    def _write(self, register, txdata):
        buffer = bytearray(len(txdata) + 1)
        buffer[0] = register & 0x7f  # Set the first bit to 0 so the BMP280 knows it's a write operation

        for index, byte in enumerate(txdata):
            buffer[index + 1] = byte

        self._cs.value(0)
        self._spi.write(buffer)
        self._cs.value(1)

    def _read(self, register, rxdata):
        self._cs.value(0)
        self._spi.readinto(rxdata, register)
        self._cs.value(1)

    def _unpack(self, format_str, *args):
        return unpack(format_str, bytes(args))[0]

    def _unpack_unsigned_short(self, *args):
        return self._unpack('>H', *args)

    def _unpack_signed_short(self, *args):
        return self._unpack('>h', *args)

    def _read_compensation_parameters(self):
        rxdata = bytearray(25)
        self._read(0x88, rxdata)

        self._dig_T1 = self._unpack_unsigned_short(rxdata[2], rxdata[1])
        self._dig_T2 = self._unpack_signed_short(rxdata[4], rxdata[3])
        self._dig_T3 = self._unpack_signed_short(rxdata[6], rxdata[5])

        self._dig_P1 = self._unpack_unsigned_short(rxdata[8], rxdata[7])
        self._dig_P2 = self._unpack_signed_short(rxdata[10], rxdata[9])
        self._dig_P3 = self._unpack_signed_short(rxdata[12], rxdata[11])
        self._dig_P4 = self._unpack_signed_short(rxdata[14], rxdata[13])
        self._dig_P5 = self._unpack_signed_short(rxdata[16], rxdata[15])
        self._dig_P6 = self._unpack_signed_short(rxdata[18], rxdata[17])
        self._dig_P7 = self._unpack_signed_short(rxdata[20], rxdata[19])
        self._dig_P8 = self._unpack_signed_short(rxdata[22], rxdata[21])
        self._dig_P9 = self._unpack_signed_short(rxdata[24], rxdata[23])

    def read_chip_id(self):
        rxdata = bytearray(2)
        self._read(0xd0, rxdata)
        return hex(rxdata[1])

    def reset(self):
        txdata = bytearray(1)
        txdata[0] = 0xb6
        self._write(0xe0, txdata)

    def read_status(self):
        rxdata = bytearray(2)
        self._read(0xf3, rxdata)
        return hex(rxdata[1])

    def write_config(self):
        self._write(0xf5, self._configuration.config)
        sleep_ms(40)  # Wait briefly so the changes can be applied

    def read_config(self):
        rxdata = bytearray(2)
        self._read(0xf5, rxdata)
        return hex(rxdata[1])

    def write_ctrl_meas(self):
        self._write(0xf4, self._configuration.ctrl_meas)
        sleep_ms(5)  # Wait briefly so the changes can be applied

    def read_ctrl_meas(self):
        rxdata = bytearray(2)
        self._read(0xf4, rxdata)
        return hex(rxdata[1])

    def read_measurements(self):
        if self._configuration.power_mode == BMP280Configuration.POWER_MODE_FORCED:
            self.write_ctrl_meas()

        rxdata = bytearray(7)
        self._read(0xf7, rxdata)

        p_adc = rxdata[1] << 12 | rxdata[2] << 4 | rxdata[3] >> 4
        t_adc = rxdata[4] << 12 | rxdata[5] << 4 | rxdata[6] >> 4

        temperature = self._calculate_temperature(t_adc)
        pressure = self._calculate_pressure(p_adc, temperature[1])

        return {
            't': temperature[0],
            't_adc': t_adc,
            'p': pressure,
            'p_adc': p_adc
        }

    def _calculate_pressure(self, adc_p, t_fine):
        var1 = (t_fine / 2) - 64000
        var2 = var1 * var1 * self._dig_P6 / 32768
        var2 = var2 + var1 * self._dig_P5 * 2
        var2 = (var2 / 4) + (self._dig_P4 * 65536)
        var1 = (self._dig_P3 * var1 * var1 / 524288 + self._dig_P2 * var1) / 524288
        var1 = (1 + var1 / 32768) * self._dig_P1

        if var1 == 0:
            return 0

        p = 1048576 - adc_p
        p = (p - (var2 / 4096)) * 6250 / var1
        var1 = self._dig_P9 * p * p / 2147483648
        var2 = p * self._dig_P8 / 32768
        p = p + (var1 + var2 + self._dig_P7) / 16

        return p / 100

    def _calculate_temperature(self, adc_t):
        var1 = (adc_t / 16384 - self._dig_T1 / 1024) * self._dig_T2
        var2 = ((adc_t / 131072 - self._dig_T1 / 8192) * (adc_t / 131072 - self._dig_T1 / 8192)) * self._dig_T3
        t_fine = var1 + var2
        t = (var1 + var2) / 5120

        return t, t_fine
