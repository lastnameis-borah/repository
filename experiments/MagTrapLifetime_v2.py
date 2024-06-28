from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class MagneticTrapLifetime_v2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Repump707:TTLOut=self.get_device("ttl4") 
        self.BMOT:TTLOut=self.get_device("ttl6")
        self.Flush:TTLOut=self.get_device("ttl8")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.BMOT_AOM=self.get_device("urukul1_ch0")
        self.MOT_Coils=self.get_device("zotino0")

        self.setattr_argument("Cycles", NumberValue(default = 1))
        self.setattr_argument("Loading_Time", NumberValue(default = 3000))
        self.setattr_argument("Holding_Time", NumberValue(default = 10))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        
        # Initialize the modules
        self.Camera.output()
        self.BMOT.output()
        self.Repump707.output()
        self.Flush.output()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.MOT_Coils.init()
        
        # Set the channel ON
        self.ZeemanSlower.sw.on()
        self.BMOT_AOM.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)

        delay(1000*ms)

        for i in range(int64(self.Cycles)):
            # Slice 1
            with parallel:
                self.BMOT.on()
                self.Flush.off()
                self.Repump707.off()
                self.Camera.off()

            self.BMOT_AOM.set(frequency= 90 * MHz, amplitude=0.05)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.35)
            
            # self.MOT_Coils.write_dac(0, 1.0)
            # self.MOT_Coils.load()

            delay(self.Loading_Time* ms)

            # Slice 2
            with parallel:
                self.BMOT.off()
                self.Flush.on()

            delay(self.Holding_Time * ms)

            #Slice 3
            with parallel:
                self.BMOT.on()
                self.Repump707.on()

            delay(3*ms)

            #Slice 4
            self.Camera.pulse(30*ms)

            with parallel:
                self.BMOT.on()
                self.Repump707.on()
                self.Flush.off()

            #Slice 5
            delay(500 * ms)

        print("Trap Lifetime Experiment Complete!")