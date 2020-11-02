import argparse
import itertools
from caproto.server import pvproperty, PVGroup, template_arg_parser, run
from sense_hat import SenseHat

sense = SenseHat()

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

class Joystick(pvproperty):
    def __init__(self, *args, **kwargs):
        super(Joystick, self).__init__(*args, **kwargs)
        # sense.stick.direction_any=self.set_direction

class Sense(PVGroup):
    def __init__(self, *args, **kwargs):
        super(Sense, self).__init__(*args, **kwargs)
        self.scroll_speed = 0.1
        self.text_colour = [255, 255, 255]
        self.back_colour = [0, 0, 0]

    Temperature = Sensor(sense.get_temperature, value=0, dtype=float, read_only=True)
    Humidity = Sensor(sense.get_humidity, value=0, dtype=float, read_only=True)
    Pressure = Sensor(sense.get_pressure, value=0, dtype=float, read_only=True)
    OrientationPitch = Sensor(lambda : sense.get_orientation()['pitch'], value=0, dtype=float, read_only=True)
    OrientationRoll = Sensor(lambda : sense.get_orientation()['roll'], value=0, dtype=float, read_only=True)
    OrientationYaw = Sensor(lambda : sense.get_orientation()['yaw'], value=0, dtype=float, read_only=True)
    Compass = Sensor(sense.get_compass, value=0, dtype=float, read_only=True)

    Text = pvproperty(value='', dtype=str)

    @Text.startup
    async def Text(self, instance, async_lib):
        instance.loop = async_lib.library.get_event_loop()


    @Text.putter
    async def Text(self, instance, value):
        await instance.loop.run_in_executor(None, sense.show_message, value, self.scroll_speed, self.text_colour, self.back_colour)
        return value  # TODO: why is this value not set?


if __name__ == "__main__":
    parser, split_args = template_arg_parser(default_prefix='Sense:', desc='Raspberry Pi SenseHat')

    args = parser.parse_args()
    ioc_options, run_options = split_args(args)
    ioc = Sense(**ioc_options)
    run(ioc.pvdb, **run_options)

