from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class comb(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.rf=self.get_device("urukul0_ch0")

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.rf.cpld.init()
        self.rf.init()
        # self.core.break_realtime()

        self.rf.sw.on()
        self.rf.set_att(16.0)
        self.rf.set(frequency=80*MHz)

        print("RF set")