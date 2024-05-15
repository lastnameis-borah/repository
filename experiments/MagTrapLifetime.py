from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class MagneticTrapLifetime(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Repump707:TTLOut=self.get_device("ttl4") 
        self.BMOT:TTLOut=self.get_device("ttl6")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.MOT_Coils=self.get_device("zotino0")

        # self.setattr_argument("Cycles", NumberValue(default = 1))
        # self.setattr_argument("Loading_Time", NumberValue(default = 2000, unit = "ms"))
        # self.setattr_argument("Holding_Time", NumberValue(default = 500, unit = "ms"))
        # self.setattr_argument("Detection_Time", NumberValue(default = 30, unit = "ms"))

    @kernel
    def run(self):
        self.core.reset()

        self.MOT_Coils.init()
        
        # Set the magnetic field constant
        self.MOT_Coils.write_dac(0, 0.52)
        self.MOT_Coils.load()

        self.core.break_realtime()

        delay(100*us)

        for i in range(int64(1)):

            with parallel:
                self.BMOT.on()
                self.Repump707.off()
                self.Camera.off()
            
            delay(2000*ms)

            delay(500*ms)

            with parallel:
                self.BMOT.on()
                self.Repump707.on()

            delay(3*ms)

            self.Camera.pulse(30*ms)

            with parallel:
                self.BMOT.off()
                self.Repump707.off()

            delay(1000*ms)

        print("Trap Lifetime Experiment Complete")