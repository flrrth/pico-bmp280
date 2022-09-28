# The datasheet can be found at
# https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp280/#documents

class BMP280Configuration:

    # See datasheet paragraph 3.3.1 Pressure measurement (page 12)
    PRESSURE_OVERSAMPLING_SKIPPED = 0
    PRESSURE_OVERSAMPLING_1X = 1
    PRESSURE_OVERSAMPLING_2X = 2
    PRESSURE_OVERSAMPLING_4X = 3
    PRESSURE_OVERSAMPLING_8X = 4
    PRESSURE_OVERSAMPLING_16X = 5

    # See datasheet paragraph 3.3.2 Temperature measurement (page 13)
    TEMPERATURE_OVERSAMPLING_SKIPPED = 0
    TEMPERATURE_OVERSAMPLING_1X = 1
    TEMPERATURE_OVERSAMPLING_2X = 2
    TEMPERATURE_OVERSAMPLING_4X = 3
    TEMPERATURE_OVERSAMPLING_8X = 4
    TEMPERATURE_OVERSAMPLING_16X = 5

    # See datasheet paragraph 3.3.3 IIR filter (page 13)
    FILTER_COEFFICIENT_OFF = 0
    FILTER_COEFFICIENT_2 = 1
    FILTER_COEFFICIENT_4 = 2
    FILTER_COEFFICIENT_8 = 3
    FILTER_COEFFICIENT_16 = 4

    # See datasheet paragraph 3.6 Power modes (page 15)
    POWER_MODE_SLEEP = 0
    POWER_MODE_FORCED = 1
    POWER_MODE_NORMAL = 3

    # See datasheet paragraph 3.6.3 Normal mode (page 16)
    STANDBY_TIME__5_MS = 0
    STANDBY_TIME_62_5_MS = 1
    STANDBY_TIME_125_MS = 2
    STANDBY_TIME_250_MS = 3
    STANDBY_TIME_500_MS = 4
    STANDBY_TIME_1000_MS = 5
    STANDBY_TIME_2000_MS = 6
    STANDBY_TIME_4000_MS = 7

    def __init__(self):
        # Configure the 'weather monitoring' use case (page 14, table 7) as default:
        self._pressure_oversampling: int = BMP280Configuration.PRESSURE_OVERSAMPLING_1X
        self._temperature_oversampling: int = BMP280Configuration.TEMPERATURE_OVERSAMPLING_1X
        self._filter_coefficient: int = BMP280Configuration.FILTER_COEFFICIENT_OFF
        self._power_mode: int = BMP280Configuration.POWER_MODE_FORCED
        self._standby_time: int = BMP280Configuration.STANDBY_TIME_1000_MS  # Has no effect in forced mode

    @property
    def ctrl_meas(self):
        array = bytearray(1)
        array[0] = self._temperature_oversampling << 5 | self._pressure_oversampling << 2 | self._power_mode
        return array

    @property
    def config(self):
        array = bytearray(1)
        array[0] = self._standby_time << 5 | self._filter_coefficient << 2
        return array

    @property
    def pressure_oversampling(self) -> int:
        return self._pressure_oversampling

    @pressure_oversampling.setter
    def pressure_oversampling(self, pressure_oversampling: int):
        self._pressure_oversampling = pressure_oversampling

    @property
    def temperature_oversampling(self) -> int:
        return self._temperature_oversampling

    @temperature_oversampling.setter
    def temperature_oversampling(self, temperature_oversampling: int):
        self._temperature_oversampling = temperature_oversampling

    @property
    def filter_coefficient(self) -> int:
        return self._filter_coefficient

    @filter_coefficient.setter
    def filter_coefficient(self, filter_coefficient: int):
        self._filter_coefficient = filter_coefficient

    @property
    def power_mode(self) -> int:
        return self._power_mode

    @power_mode.setter
    def power_mode(self, power_mode: int):
        self._power_mode = power_mode

    @property
    def standby_time(self) -> int:
        return self._standby_time

    @standby_time.setter
    def standby_time(self, standby_time: int):
        self._standby_time = standby_time
