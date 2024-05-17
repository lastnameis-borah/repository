from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class MagneticTrapLoading(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Repump707:TTLOut=self.get_device("ttl4") 
        self.BMOT:TTLOut=self.get_device("ttl6")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.BMOT_AOM=self.get_device("urukul1_ch0")
        # self.MOT_Coils=self.get_device("zotino0")

        self.setattr_argument("Cycles", NumberValue(default = 1))
        self.setattr_argument("Loading_Time", NumberValue(default = 3000))
        self.setattr_argument("Holding_Time", NumberValue(default = 10))
        self.setattr_argument("Detection_Time", NumberValue(default = 30))
        self.setattr_argument("Shutter_Delay", NumberValue(default = 7))

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
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        # self.MOT_Coils.init()
        
        # Set the channel ON
        self.ZeemanSlower.sw.on()
        self.BMOT_AOM.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.BMOT_AOM.set(frequency= 90 * MHz, amplitude=0.09)
        
        # Set the magnetic field constant
        # self.MOT_Coils.write_dac(0, 0.52)
        # self.MOT_Coils.load()

        delay(1000*ms)

        for i in range(int64(self.Cycles)):
            # Slice 1
            with parallel:
                self.BMOT.on()
                self.Repump707.off()
                self.Camera.off()
            
            self.ZeemanSlower.set_att(0.0)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.35)

            delay(self.Loading_Time* ms)

            # Slice 2
            with parallel:
                self.BMOT.off()
            
            self.ZeemanSlower.set_att(31.9)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.0)

            delay(self.Holding_Time * ms)

            #Slice 3
            with parallel:
                self.BMOT.on()
                self.Repump707.on()

            delay(self.Shutter_Delay*ms)

            #Slice 4
            self.Camera.on()
            delay(self.Detection_Time*ms)
            with parallel:
                self.Camera.off()
                self.BMOT.off()
                self.Repump707.off()

            #Slice 5
            delay(500 * ms)

        print("Trap Loading Experiment Complete!")