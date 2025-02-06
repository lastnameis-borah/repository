from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class blueMOT(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.MOT_Coils=self.get_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=500))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Camera.output()
        self.MOT_Coils.init()
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()

        self.BMOT_AOM.set_att(0.0)
        self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
        self.ZeemanSlower.set_att(0.0)
        self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            with parallel:
                with sequential:
                    self.MOT_Coils.write_dac(0, 1.0)
                    self.MOT_Coils.load()
                self.BMOT_AOM.sw.on()
                self.ZeemanSlower.sw.on()

            # Loading duration
            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Holding ****************************
            self.BMOT_AOM.sw.off()
            self.ZeemanSlower.sw.off()
            delay(3*ms)

            # **************************** Slice 3: Detection ****************************
            with parallel:
                self.BMOT_AOM.sw.on()
                self.Camera.pulse(10*ms)
            self.BMOT_AOM.sw.off()
            
            # **************************** Slice 4 ****************************
            delay(500*ms)

        print("We got BlueMOT!")