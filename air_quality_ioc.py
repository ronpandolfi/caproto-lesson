import argparse
import itertools
from caproto.server import pvproperty, PVGroup, template_arg_parser, run
import board
import adafruit_bme680
import busio

i2c = busio.I2C(board.SCL, board.SDA)
sense = adafruit_bme680.Adafruit_BME680_I2C(i2c)

REFRESH_PERIOD = 1


class Sensor(pvproperty):
    def __init__(self, measure_func, *args, **kwargs):
        super(Sensor, self).__init__(*args, **kwargs)
        self.measure_func = measure_func
        self.startup(self.measure)

    async def measure(self, group, instance, async_lib):
        while True:
            await instance.write(value=self.measure_func())
            await async_lib.library.sleep(REFRESH_PERIOD)


class Sense(PVGroup):
    def __init__(self, *args, **kwargs):
        super(Sense, self).__init__(*args, **kwargs)

    Gas = Sensor(lambda : sense.gas, value=0, dtype=float, read_only=True)


if __name__ == "__main__":
    parser, split_args = template_arg_parser(default_prefix='Sense:', desc='Raspberry Pi BME680 Air Quality')

    args = parser.parse_args()
    ioc_options, run_options = split_args(args)
    ioc = Sense(**ioc_options)
    run(ioc.pvdb, **run_options)

