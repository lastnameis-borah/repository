from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64
from artiq.coredevice.core import Core

class MOTLoading(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core
        self.BMOT:TTLOut=self.get_device("ttl4")
        self.camera:TTLOut=self.get_device("ttl8")
        self.setattr_device("zotino0")

        self.setattr_argument("Repetation", NumberValue())
        self.setattr_argument("Loading_duration", NumberValue())
        

    @kernel
    def run(self):
        self.core.reset()

        self.core.break_realtime()

        self.zotino0.init()
        self.blue.output()
        self.camera.output()

        delay(100*us)

        self.zotino0.write_dac(0, 0.52)   #0.52 = 3.5A, 1.97 = 2A, 1.76 = 2.2A, 1.04 = 1A
        self.zotino0.load()

        for i in range(int64(self.Repetation)):
            with parallel:
                self.BMOT.pulse(self.Loading_duration * ms)

            with parallel:
                self.BMOT.pulse(30 * ms)
                self.camera.pulse(30 * ms)

            delay(1000*ms)

        print("Loading test is done")
