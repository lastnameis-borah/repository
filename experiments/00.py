from artiq.experiment import *
from artiq.coredevice.core import Core
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class Everything_ON(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core:Core

        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")

        self.BMOT=self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.RMOT=self.get_device("urukul1_ch2")
        self.Probe=self.get_device("urukul1_ch3")
        self.Clock=self.get_device("urukul0_ch0")

        self.Repump707:TTLOut=self.get_device("ttl4")
        self.Repump679:TTLOut=self.get_device("ttl9")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        
        self.setattr_argument("Cycle", NumberValue(default = 100))
        self.setattr_argument("High_Low", BooleanValue(default=False))
        self.setattr_argument("Idle_State", BooleanValue(default=False))
        self.setattr_argument("Coil_1_voltage", NumberValue(default = 0.976, unit="V"))
        self.setattr_argument("Coil_2_voltage", NumberValue(default = 0.53, unit="V"))

        self.setattr_argument("BMOT_Frequency", NumberValue(default = 90.0))
        self.setattr_argument("BMOT_Amplitude", NumberValue(default = 0.08))
        # self.setattr_argument("BMOT_Attenuation", NumberValue(default = 0.0))

        self.setattr_argument("Zeeman_Frequency", NumberValue(default = 180.0))
        self.setattr_argument("Zeeman_Amplitude", NumberValue(default = 0.35)) 
        # self.setattr_argument("Zeeman_Attenuation", NumberValue(default = 0.0))

        self.setattr_argument("RMOT_Frequency", NumberValue(default = 80.0))
        self.setattr_argument("RMOT_Amplitude", NumberValue(default = 0.35)) 
        # self.setattr_argument("RMOT_Attenuation", NumberValue(default = 0.0))

        self.setattr_argument("Probe_Frequency", NumberValue(default = 65.0))
        self.setattr_argument("Probe_Amplitude", NumberValue(default = 0.02)) 
        # self.setattr_argument("Probe_Attenuation", NumberValue(default = 0.0))

        self.setattr_argument("Clock_Frequency", NumberValue(default = 85.47))
        self.setattr_argument("Clock_Attenuation", NumberValue(default = 0.0))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.MOT_Coil_1.init()
        self.MOT_Coil_2.init()

        self.BMOT.cpld.init()
        self.BMOT.init()

        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()

        self.RMOT.cpld.init()
        self.RMOT.init()

        self.Probe.cpld.init()
        self.Probe.init()

        self.Clock.cpld.init()
        self.Clock.init()

        self.BMOT.sw.on()
        self.ZeemanSlower.sw.on()
        self.RMOT.sw.on()
        self.Probe.sw.on()
        self.Clock.sw.on()
        # self.Flush.sw.on()

        self.BMOT.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.RMOT.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Clock.set_att(self.Clock_Attenuation)
        # self.Flush.set_att(self.Flush_Attenuation)
        self.MOT_Coil_1.write_dac(0, self.Coil_1_voltage)
        self.MOT_Coil_2.write_dac(1, self.Coil_2_voltage)
        
        with parallel:
            self.MOT_Coil_1.load()
            self.MOT_Coil_2.load()
            self.Repump707.on()
            self.Repump679.on()
            self.BMOT_TTL.on()
            self.RMOT_TTL.on()
            self.Zeeman_Slower_TTL.on()

        self.BMOT.set(frequency= self.BMOT_Frequency * MHz, amplitude=self.BMOT_Amplitude)

        self.ZeemanSlower.set(frequency=self.Zeeman_Frequency * MHz, amplitude=self.Zeeman_Amplitude)

        self.RMOT.set(frequency=self.RMOT_Frequency * MHz, amplitude=self.RMOT_Amplitude)

        self.Probe.set(frequency=self.Probe_Frequency * MHz, amplitude=self.Probe_Amplitude)

        self.Clock.set(frequency=self.Clock_Frequency * MHz)

        delay(1000*ms)

        if self.High_Low == True:
            for i in range(int64(self.Cycle)):
                self.MOT_Coil_1.write_dac(0, 1.07)
                self.MOT_Coil_2.write_dac(1, 0.54)

                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()
                    self.ZeemanSlower.set(frequency=self.Zeeman_Frequency * MHz, amplitude=self.Zeeman_Amplitude)
                self.Clock.sw.on()
                delay(1500*ms)

                self.MOT_Coil_1.write_dac(0, 2.54)
                self.MOT_Coil_2.write_dac(1, 2.28)
                self.ZeemanSlower.set(frequency=self.Zeeman_Frequency * MHz, amplitude=0.0)

                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()
                self.Clock.sw.off()
                delay(1500*ms)

        if self.Idle_State == True:
            self.Clock.set_att(self.Clock_Attenuation)
            self.MOT_Coil_1.write_dac(0, 4.055)
            self.MOT_Coil_2.write_dac(1, 4.083)

            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()
        
        print("Parameters are set")