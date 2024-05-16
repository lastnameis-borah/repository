from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class RFswitch(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.TTL1:TTLOut=self.get_device("ttl12") 
        self.TTL2:TTLOut=self.get_device("ttl14")
        self.RF=self.get_device("urukul1_ch3")

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        
        # Initialize the modules
        self.TTL1.output()
        self.TTL2.output()
        self.RF.cpld.init()
        self.RF.init()

        self.RF.set_att(0.0)
        self.RF.set(frequency= 80 * MHz, amplitude=1.0)
        
        # Set the channel ON
        self.RF.sw.on()
        
        for i in range(1):
            self.TTL1.pulse(10*ms)

            delay(10*ms)

            self.TTL2.pulse(10*ms)

        print("RF switch test is done")