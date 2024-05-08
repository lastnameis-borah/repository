from artiq.experiment import *
from artiq.coredevice.ttl import TTLInOut, TTLOut
from artiq.coredevice.core import Core

class ReadTTL(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core
        self.ttlout:TTLOut=self.get_device("ttl4") 
        self.ttlin:TTLInOut=self.get_device("ttl0") 


    @kernel
    def run(self):
        self.core.reset()

        self.core.break_realtime()

        self.ttlin.input()

        count = self.ttlin.count(self.ttlin.gate_rising(100*ms))

        print(count)

        print("TTL count test is done")