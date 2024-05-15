from artiq.experiment import *
from artiq.coredevice.core import Core
from artiq.coredevice.ttl import TTLOut

class AOM_and_TTL(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core

        self.MOT_Coils=self.get_device("zotino0")

        self.BMOT=self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Probe=self.get_device("urukul1_ch2")

        self.Repump707:TTLOut=self.get_device("ttl4")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.Flush_TTL:TTLOut=self.get_device("ttl8")
        

        self.setattr_argument("BMOT_Frequency", NumberValue())
        self.setattr_argument("BMOT_Amplitude", NumberValue(default = 0.09))
        self.setattr_argument("BMOT_Attenuation", NumberValue(default = 0.0))

        self.setattr_argument("Zeeman_Frequency", NumberValue())
        self.setattr_argument("Zeeman_Amplitude", NumberValue(default = 0.35)) 
        self.setattr_argument("Zeeman_Attenuation", NumberValue(default = 0.0))

        self.setattr_argument("Probe_Frequency", NumberValue())
        self.setattr_argument("Probe_Amplitude", NumberValue(default = 0.06)) 
        self.setattr_argument("Probe_Attenuation", NumberValue(default = 0.0))


    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.MOT_Coils.init()

        self.BMOT.cpld.init()
        self.BMOT.init()

        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()

        self.Probe.cpld.init()
        self.Probe.init()


        self.BMOT.sw.on()
        self.ZeemanSlower.sw.on()
        self.Probe.sw.on()
        # self.Flush.sw.on()

        self.BMOT.set_att(self.BMOT_Attenuation)
        self.ZeemanSlower.set_att(self.Zeeman_Attenuation)
        self.Probe.set_att(self.Probe_Attenuation)
        # self.Flush.set_att(self.Flush_Attenuation)

        
        with parallel:
            self.Repump707.on()
            self.BMOT_TTL.on()
            self.Flush_TTL.on()
            with sequential:
                self.MOT_Coils.write_dac(0, 0.51) #3.04
                self.MOT_Coils.load()
        
        # with parallel:
        #     with sequential:
        self.BMOT.set(frequency= self.BMOT_Frequency * MHz, amplitude=self.BMOT_Amplitude)
            # with sequential:
        self.ZeemanSlower.set(frequency=self.Zeeman_Frequency * MHz, amplitude=self.Zeeman_Amplitude)
        # with sequential:
        self.Probe.set(frequency=self.Probe_Frequency * MHz, amplitude=self.Probe_Amplitude)

        

        print("Parameters are set")