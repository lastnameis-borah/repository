from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut

class MagneticTrapLifetime(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Repump707:TTLOut=self.get_device("ttl4") 
        self.BMOT:TTLOut=self.get_device("ttl6")
        self.Camera:TTLOut=self.get_device("ttl10")

        self.setattr_argument("Cycles", NumberValue(default = 1))
        self.setattr_argument("Loading_Time", NumberValue(default = 2000, unit = "ms"))
        self.setattr_argument("Holding_Time", NumberValue(default = 500, unit = "ms"))
        self.setattr_argument("Detection_Time", NumberValue(default = 30, unit = "ms"))

    @kernel
    def run(self):
        self.core.reset()

        self.core.break_realtime()

        delay(1000*us)

        for i in range(self.Cycles):

            with parallel:
                self.BMOT.on()
                self.Repump707.off()
                self.Camera.off()
            
            delay(self.Loading_Time*ms)

            delay(self.Holding_Time*ms)

            with parallel:
                self.BMOT.on()
                self.Repump707.on()

            delay(3*ms)

            self.Camera.pulse(self.Detection_Time*ms)

            with parallel:
                self.BMOT.off()
                self.Repump707.off()
                self.Camera.off()

            delay(1000*ms)

        print("Experiment Complete")