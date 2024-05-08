from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64, int32
from artiq.coredevice.core import Core

class redMOT(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core
        self.camera:TTLOut=self.get_device("ttl8")
        self.red:TTLOut=self.get_device("ttl6")
        self.ad9910_0 = self.get_device("urukul1_ch0")
        self.ad9910_1=self.get_device("urukul1_ch1")
        self.setattr_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=550))
        self.setattr_argument("Transfer_Time", NumberValue(default=20))
        self.setattr_argument("Holding_Time", NumberValue(default=20))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.camera.output()
        self.red.output()
        self.zotino0.init()
        self.ad9910_0.cpld.init()
        self.ad9910_0.init()
        self.ad9910_1.cpld.init()
        self.ad9910_1.init()

        # Set the channel ON
        self.ad9910_0.sw.on()
        self.ad9910_1.sw.on()

        self.ad9910_0.set_att(0.0)
        self.ad9910_1.set_att(0.0)

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # Slice 1
            # with parallel:
                # BMOT
            self.ad9910_0.set(frequency=90*MHz, amplitude=0.09)

                # Zeeman Slower
            self.ad9910_1.set(frequency=180 * MHz, amplitude=0.35)

            with parallel:
                # Magnetic field (3.5v)
                with sequential:
                    self.zotino0.write_dac(0, 0.52)
                    self.zotino0.load()
                    
                    # Start the modulation of red
                self.red.on()

            # Slice 1 duration
            delay(self.Loading_Time*ms)

            # Slice 2: Transfer

            # with parallel:
                # Magnetic field (2.2A)
                # with sequential:
            self.zotino0.write_dac(0, 1.97) #3.04
            self.zotino0.load()

                # Zeeman Slower
                # with sequential:
            # self.ad9910_1.set_att(31.9)
            self.ad9910_1.set(frequency=180 * MHz, amplitude=0.0)

            # BMOT
            # with sequential:
            steps = self.Transfer_Time
            t = self.Transfer_Time/steps
            for i in range(int64(steps + 1.0)):
                amp_steps = 0.09/steps
                amp = 0.09 - (i * amp_steps)
                self.ad9910_0.set(frequency=90*MHz, amplitude=amp)
                delay(t*ms)


            # Slice 3
            delay(self.Holding_Time*ms)

            # Slice 4: Compentation for shutter delay
            self.red.off()
            delay(3*ms)

            # Slice 5: Detection
            with parallel:
                self.ad9910_0.set(frequency=90*MHz, amplitude=0.09)
                self.camera.pulse(5*ms)

            delay(50*ms)

            # Slice 6
            self.ad9910_1.set_att(0.0)
            self.ad9910_1.set(frequency=180 * MHz, amplitude=0.35)
            
            # Slice 6: Headroom for 2nd cycle
            delay(1000*ms)

        print("RedMOT exp complete!!")