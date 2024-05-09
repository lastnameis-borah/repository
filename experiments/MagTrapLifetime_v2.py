from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class MagneticTrapLifetime_v2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Repump707:TTLOut=self.get_device("ttl4") 
        self.BMOT:TTLOut=self.get_device("ttl6")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Flush=self.get_device("urukul1_ch3")
        self.MOT_Coils=self.get_device("zotino0")

        self.setattr_argument("Cycles", NumberValue(default = 1))
        self.setattr_argument("Loading_Time", NumberValue(default = 2000, unit = "ms"))
        self.setattr_argument("Holding_Time", NumberValue(default = 500, unit = "ms"))
        self.setattr_argument("Detection_Time", NumberValue(default = 30, unit = "ms"))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Camera.output()
        self.BMOT.output()
        self.Repump707.output()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.Flush.cpld.init()
        self.Flush.init()
        self.MOT_Coils.init()
        
        # Set the channel ON
        self.ZeemanSlower.sw.on()
        self.Flush.sw.on()
        
        # Set the magnetic field constant
        self.MOT_Coils.write_dac(0, 0.52)
        self.MOT_Coils.load()

        delay(100*us)

        for i in range(int64(self.Cycles)):
            # Slice 1
            self.ZeemanSlower.set_att(0.0)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.35)

            self.Flush.set_att(31.9)
            self.Flush.set(frequency=180*MHz, amplitude=0.0)

            self.BMOT.on()

            delay(self.Loading_Time * ms)

            # Slice 2
            self.ZeemanSlower.set_att(31.9)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.0)

            self.Flush.set_att(0.0)
            self.Flush.set(frequency=180*MHz, amplitude=0.9)

            self.BMOT.off()

            delay(self.Holding_Time * ms)

            #Slice 3
            with parallel:
                self.BMOT
                self.Repump707.on()

            delay(3*ms)

            #Slice 4
            self.Camera.on()
            delay(self.Detection_Time*ms)
            with parallel:
                self.Camera.off()
                self.BMOT.off()
                self.Repump707.off()

            #Slice 5
            delay(1000 * ms)

        print("Experiment Complete!")