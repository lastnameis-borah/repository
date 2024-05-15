from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64, int32
from artiq.coredevice.core import Core

class blueMOT(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core
        self.BMOT = self.get_device("urukul1_ch0")
        self.BMOT_Shutter:TTLOut=self.get_device("ttl4")
        self.ZeemanSlower = self.get_device("urukul1_ch1")
        self.Camera:TTLOut = self.get_device("ttl8")
        self.MagField = self.get_device("zotino0")

        self.setattr_argument("Cycles", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=500))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Camera.output()
        self.MagField.init()
        self.BMOT.cpld.init()
        self.BMOT.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()

        # Set the channel ON
        self.BMOT.sw.on()
        self.ZeemanSlower.sw.on()

        self.BMOT.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        
        for i in range(int64(self.Cycles)):
            #Slice 1: Loading
            self.BMOT_Shutter.on()
            self.BMOT.set(frequency=90*MHz, amplitude=0.09)

            with parallel:
                self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

                with sequential:
                    self.MagField.write_dac(0, 0.51)   #0.52 = 3.5A, 1.97 = 2A, 1.76 = 2.2A, 1.04 = 1A
                    self.MagField.load()

            #Slice 1 duration
            delay(self.Loading_Time*ms)

            #Slice 2: Detection
            # with parallel:
            #     self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.00)

            #     # with sequential:
            #     #     self.MagField.write_dac(0, 0.52)   #0.52 = 3.5A, 1.97 = 2A, 1.76 = 2.2A, 1.04 = 1A
            #     #     self.MagField.load()

            #     self.Camera.pulse(5*ms)

            # self.BMOT_Shutter.off()
            # # We need shutter as the 0th order is still going to the chamber
            # delay(1000*ms)

            

            

        print("We got BMOT!!")
