from ustruct import unpack
from utime import sleep_ms

from .bmp280_configuration import BMP280Configuration


class BMP280:
    
    def __init__(self, configuration):
        self.configuration = configuration

    def _unpack(self, format_str, *args):
        return unpack(format_str, bytes(args))[0]

    def _unpack_unsigned_short(self, *args):
        return self._unpack('>H', *args)

    def _unpack_signed_short(self, *args):
        return self._unpack('>h', *args)
    
    def _unpack_compensation_parameters(self, rxdata):
        self._dig_T1 = self._unpack_unsigned_short(rxdata[1], rxdata[0])
        self._dig_T2 = self._unpack_signed_short(rxdata[3], rxdata[2])
        self._dig_T3 = self._unpack_signed_short(rxdata[5], rxdata[4])

        self._dig_P1 = self._unpack_unsigned_short(rxdata[7], rxdata[6])
        self._dig_P2 = self._unpack_signed_short(rxdata[9], rxdata[8])
        self._dig_P3 = self._unpack_signed_short(rxdata[11], rxdata[10])
        self._dig_P4 = self._unpack_signed_short(rxdata[13], rxdata[12])
        self._dig_P5 = self._unpack_signed_short(rxdata[15], rxdata[14])
        self._dig_P6 = self._unpack_signed_short(rxdata[17], rxdata[16])
        self._dig_P7 = self._unpack_signed_short(rxdata[19], rxdata[18])
        self._dig_P8 = self._unpack_signed_short(rxdata[21], rxdata[20])
        self._dig_P9 = self._unpack_signed_short(rxdata[23], rxdata[22])
        
    def _read_compensation_parameters(self):
        rxdata = self._read(0x88, 24)
        self._unpack_compensation_parameters(rxdata)
    
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

    @property
    def configuration(self):
        return self._configuration
    
    @configuration.setter
    def configuration(self, configuration):
        self._configuration = configuration
        self.reset()
        self._write_ctrl_meas()
        self._write_config()
        
    def reset(self):
        txdata = bytearray(1)
        txdata[0] = 0xb6
        self._write(0xe0, txdata)

    @property
    def chip_id(self):        
        rxdata = self._read(0xd0, 1)
        return hex(rxdata[0])
    
    @property
    def status(self):
        rxdata = self._read(0xf3, 1)
        return hex(rxdata[0])
    
    @property
    def config(self):
        rxdata = self._read(0xf5, 1)
        return hex(rxdata[0])
    
    def _write_config(self):
        self._write(0xf5, self._configuration.config)
        sleep_ms(40)  # Wait briefly so the changes can be applied
    
    @property
    def ctrl_meas(self):
        rxdata = self._read(0xf4, 1)
        return hex(rxdata[0])
    
    def _write_ctrl_meas(self):
        self._write(0xf4, self._configuration.ctrl_meas)
        sleep_ms(5)  # Wait briefly so the changes can be applied
    
    @property
    def measurements(self):
        if self._configuration.power_mode == BMP280Configuration.POWER_MODE_FORCED:
            self._write_ctrl_meas()

        rxdata = self._read(0xf7, 6)

        p_adc = rxdata[0] << 12 | rxdata[1] << 4 | rxdata[2] >> 4
        t_adc = rxdata[3] << 12 | rxdata[4] << 4 | rxdata[5] >> 4

        temperature = self._calculate_temperature(t_adc)
        pressure = self._calculate_pressure(p_adc, temperature[1])

        return {
            't': temperature[0],
            't_adc': t_adc,
            'p': pressure,
            'p_adc': p_adc
        }
