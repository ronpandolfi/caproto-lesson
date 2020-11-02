import time
import argparse
import itertools
import numpy as np
from caproto.server import pvproperty, PVGroup, template_arg_parser, run
import picamera
import pantilthat

SIZE_X = 320*2**3 # True resolution is: 4056
SIZE_Y = 240*2**3 #                     3040

class Camera(PVGroup):
    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)

        # Setup PanTiltHat
        self.pantilthat = pantilthat.PanTilt()

        # Setup camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = (SIZE_X, SIZE_Y)
        self.camera.framerate = 24
        time.sleep(2)  # give the camera time to startup

    size_x = pvproperty(value=SIZE_X)
    size_y = pvproperty(value=SIZE_Y)
    ArrayData = pvproperty(dtype=float, max_length=SIZE_X*SIZE_Y*3)
    Trigger = pvproperty(dtype=int)

    @Trigger.putter
    async def Trigger(self, instance, value):
        print(value)
        if value:
            output = np.empty((SIZE_X, SIZE_Y, 3), dtype=np.uint8)
            self.camera.capture(output, 'rgb')
            await self.ArrayData.write(np.sum(output, axis=2).ravel())

    Pan = pvproperty(dtype=float)

    @Pan.getter
    async def Pan(self, instance):
        return self.pantilthat.get_pan()

    @Pan.putter
    async def Pan(self, instance, value):
        self.pantilthat.pan(value)

    Tilt = pvproperty(dtype=float)

    @Tilt.getter
    async def Tilt(self, instance):
        return self.pantilthat.get_tilt()

    @Tilt.putter
    async def Tilt(self, instance, value):
        self.pantilthat.tilt(value)


if __name__ == "__main__":
    parser, split_args = template_arg_parser(default_prefix='Camera:', desc='Raspberry Pi HQ Camera with tilt-pan control')

    args = parser.parse_args()
    ioc_options, run_options = split_args(args)
    ioc = Camera(**ioc_options)
    run(ioc.pvdb, **run_options)

