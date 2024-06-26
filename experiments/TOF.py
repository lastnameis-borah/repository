from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64
from artiq.coredevice.core import Core

class TimeOfFlight(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core
        self.blue:TTLOut=self.get_device("ttl4")
        self.red:TTLOut=self.get_device("ttl6")
        self.camera:TTLOut=self.get_device("ttl8")
        self.setattr_device("zotino0")

        self.setattr_argument("Repetation", NumberValue())
        self.setattr_argument("Second_slice_duration", NumberValue())
        self.setattr_argument("Voltage", NumberValue())
        

    @kernel
    def run(self):
        self.core.reset()

        self.core.break_realtime()

        self.blue.output()
        self.red.output()
        self.camera.output()

        delay(100*us)

        for i in range(int64(self.Repetation)):
            with parallel:
                self.blue.pulse(2000*ms)
                self.red.pulse(2000*ms)
                self.zotino0.write_dac(0, self.Voltage)
                self.zotino0.load()

            delay(self.Second_slice_duration *ms)

            with parallel:
                self.blue.pulse(30 * ms)
                self.red.pulse(30 * ms)

            with parallel:
                self.blue.pulse(30 * ms)
                self.red.pulse(30 * ms)
                self.camera.pulse(30 * ms)

            delay(1000*ms)

        print("Loading test is done")
