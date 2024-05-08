from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64, int32
from artiq.coredevice.core import Core

class TestTTL(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core
        self.ttl:TTLOut=self.get_device("ttl10") 

        self.setattr_argument("Number_of_pulse", NumberValue())
        self.setattr_argument("Pulse_width", NumberValue())
        self.setattr_argument("Time_between_pulse", NumberValue())


    @kernel
    def run(self):        
        self.core.reset()

        self.core.break_realtime()          # RTIO underflow error

        self.ttl.output()                   # set the TTL to output mode

        # for i in range(int64(self.Number_of_pulse)):
        #     self.ttl.pulse(self.Pulse_width * ms)
        #     delay(self.Time_between_pulse * ms)

        self.ttl.pulse(1*ms)

        print("TTL test is done")
