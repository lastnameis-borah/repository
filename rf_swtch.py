from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class RFswitch(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.TTL:TTLOut=self.get_device("ttl12") 
        self.RF=self.get_device("urukul1_ch3")

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        
        # Initialize the modules
        self.TTL.output()
        self.RF.cpld.init()
        self.RF.init()
        
        # Set the channel ON
        self.RF.sw.on()
        
        for i in range(5):
            self.RF.set_att(0.0)
            self.RF.set(frequency= 80 * MHz, amplitude=1.0)

            delay(1000*ms)

            self.TTL.pulse(1000*ms)