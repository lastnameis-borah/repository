from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class blueMOT_probe_v1(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl15")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Probe=self.get_device("urukul1_ch2")
        self.MOT_Coils=self.get_device("zotino0")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.Repump707:TTLOut=self.get_device("ttl4")
        self.Ref=self.get_device("urukul1_ch3")

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
        self.Probe.cpld.init()
        self.Probe.init()
        self.Ref.cpld.init()
        self.Ref.init()

        self.BMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()
        self.Probe.sw.on()
        self.Ref.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Ref.set_att(0.0)

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            self.Repump707.on()
            self.BMOT_TTL.on()

            self.MOT_Coils.write_dac(0, 1.0)
            self.MOT_Coils.load()
            
            self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.05)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
            self.Ref.set(frequency= 90 * MHz, amplitude=0.5)

            # Loading duration
            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Holding ****************************
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.00)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.00)
            self.Ref.set(frequency= 90 * MHz, amplitude=0.00)

            self.MOT_Coils.write_dac(0, 4.07)
            self.MOT_Coils.load()

            # with parallel:
            #     self.Repump707.off()
            #     self.BMOT_TTL.off()
            # delay(3*ms)

            # **************************** Slice 3: Detection ****************************
            with parallel:
                self.Probe.set(frequency= 65 * MHz, amplitude=0.17)
                self.Camera.pulse(1*ms)

            self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
            
            # **************************** Slice 4 ****************************
            delay(500*ms)

        print("We got BlueMOT!")