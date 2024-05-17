from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class RFswitch(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.TTL1:TTLOut=self.get_device("ttl5") 
        self.TTL2:TTLOut=self.get_device("ttl7")
        # self.TTL3:TTLOut=self.get_device("ttl15")
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
        
        
        for i in range(5):
            with parallel:
                self.TTL1.pulse(10*ms)
                self.RF.sw.off()
                # self.TTL3.on()

            delay(1000*ms)

            with parallel:
                self.TTL2.pulse(10*ms)
                self.RF.sw.on()
                # self.TTL3.off() 

            delay(1000*ms)

        print("RF switch test is done")