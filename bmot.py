from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class bmot_probe_v2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl15")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Broadband_On:TTLOut=self.get_device("ttl5")
        self.Broadband_Off:TTLOut=self.get_device("ttl7")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Probe=self.get_device("urukul1_ch2")
        self.Single_Freq=self.get_device("urukul1_ch3")
        self.MOT_Coils=self.get_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=550))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Camera.output()
        self.BMOT_TTL.output()
        self.RMOT_TTL.output()
        self.MOT_Coils.init()
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.Probe.cpld.init()
        self.Probe.init()
        self.Single_Freq.cpld.init()
        self.Single_Freq.init()

        # Set the channel ON
        self.BMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()
        self.Probe.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Probe.set(frequency= 65 * MHz, amplitude=0.0)

        for i in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.09)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

            self.MOT_Coils.write_dac(0, 0.52)
            self.MOT_Coils.load()

            delay(self.Loading_Time*ms)

            # **************************** Slice 2: ****************************

            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.0)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.0)

            self.MOT_Coils.write_dac(0,4.13) 
            self.MOT_Coils.load()

            # **************************** Slice 5: Detection ****************************
            with parallel:
                self.Probe.set(frequency= 65*MHz, amplitude=0.17)
                self.Camera.pulse(1*ms)
            self.Probe.set(frequency= 65*MHz, amplitude=0.00)

            self.MOT_Coils.write_dac(0, 0.52)
            self.MOT_Coils.load()
            
            # **************************** Slice 7 ****************************
            delay(1000*ms)

        print("bmot exp complete!!")