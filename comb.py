from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class test_rf(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Single_Freq=self.get_device("urukul1_ch0")
        self.Probe=self.get_device("urukul0_ch0")

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.Single_Freq.cpld.init()
        self.Single_Freq.init()
        self.Probe.cpld.init()
        self.Probe.init()

        self.Single_Freq.sw.on()
        self.Single_Freq.set_att(0.0)
        self.Probe.set_att(10.0)
        self.Probe.set(frequency=80*MHz)


        for i in range(int64(20)):
            self.Single_Freq.set(frequency=80*MHz, amplitude=0.5)
            self.Probe.sw.on()
            delay(500*ms)
            self.Single_Freq.set(frequency=80*MHz, amplitude=0.0)
            self.Probe.sw.off()
            delay(500*ms)

        # self.Probe.sw.on()

        # delay(500*ms)

        # self.Probe.sw.off()

        print("RF set")