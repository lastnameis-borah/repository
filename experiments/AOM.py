from artiq.experiment import *
from artiq.coredevice.core import Core

class AOM(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core
        self.ad9910_0=self.get_device("urukul1_ch0")
        self.ad9910_1=self.get_device("urukul1_ch1")
        self.ad9910_2=self.get_device("urukul1_ch2")

        self.setattr_argument("BMOT_Frequency", NumberValue())
        self.setattr_argument("BMOT_Amplitude", NumberValue()) 
        self.setattr_argument("BMOT_Attenuation", NumberValue())

        self.setattr_argument("Zeeman_Frequency", NumberValue())
        self.setattr_argument("Zeeman_Amplitude", NumberValue()) 
        self.setattr_argument("Zeeman_Attenuation", NumberValue())

        self.setattr_argument("Probe_Frequency", NumberValue())
        self.setattr_argument("Probe_Amplitude", NumberValue()) 
        self.setattr_argument("Probe_Attenuation", NumberValue())

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.ad9910_0.cpld.init()
        self.ad9910_0.init()

        self.ad9910_1.cpld.init()
        self.ad9910_1.init()

        self.ad9910_2.cpld.init()
        self.ad9910_2.init()

        self.ad9910_0.sw.on()
        self.ad9910_1.sw.on()
        self.ad9910_2.sw.on()

        self.ad9910_0.set_att(self.BMOT_Attenuation)
        self.ad9910_1.set_att(self.Zeeman_Attenuation)
        self.ad9910_2.set_att(self.Probe_Attenuation)

        
        # with parallel:
        #     with sequential:
                    
        self.ad9910_0.set(frequency= self.BMOT_Frequency * MHz, amplitude=self.BMOT_Amplitude)
            # with sequential:
                
        self.ad9910_1.set(frequency=self.Zeeman_Frequency * MHz, amplitude=self.Zeeman_Amplitude)
        
        # with sequential:
            
        self.ad9910_2.set(frequency=self.Probe_Frequency * MHz, amplitude=self.Probe_Amplitude)

        print("Parameters are set")