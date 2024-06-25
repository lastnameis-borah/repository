from artiq.experiment import *
from artiq.coredevice.core import Core
from artiq.coredevice.ttl import TTLOut

class probe(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core

        self.Probe=self.get_device("urukul1_ch2")

        self.setattr_argument("Probe_Amplitude", NumberValue(default = 0.17)) 

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.Probe.cpld.init()
        self.Probe.init()
        

        for i in range(1):
            self.Probe.sw.on()

            self.Probe.set_att(0.0)

            self.Probe.set(frequency=65 * MHz, amplitude=self.Probe_Amplitude)

            # delay(1*us)
            
            # self.Probe.sw.off()

            # delay(1*us)
        
        
        print("Parameters are set")