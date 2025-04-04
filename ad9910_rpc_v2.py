from artiq.experiment import *
from artiq.coredevice.ad9910 import AD9910
from artiq.coredevice.urukul import CPLD
from artiq.experiment import EnvExperiment
from artiq.experiment import NumberValue
from numpy import int64
import numpy as np

class red_mod_rpc2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ad9910_0: AD9910 = self.get_device("urukul1_ch2") 
    
        self.setattr_argument("Cycles", NumberValue(default=5))
        self.setattr_argument("Attenuation", NumberValue(default=1.0, unit="dB"))
        # self.setattr_argument("Frequency", NumberValue(default=10, unit="MHz"))
        self.setattr_argument("Amplitude", NumberValue(default=1.0, unit="V"))
        self.setattr_argument("Phase", NumberValue(default=0))

        # self.setattr_argument("Phase", NumberValue(default=0.0))

    @rpc
    def freq_steps(self) -> int64:
        # self.freq_start
        self.freq_start = 80 * MHz
        # global self.freq_end
        self.freq_end= 81 * MHz
        self.steps = (self.freq_end - self.freq_start) / self.Cycles
        return int64(self.steps)

    @kernel
    def run(self):
        # self.core.reset()
        self.core.break_realtime()

        self.ad9910_0.cpld.init()
        self.ad9910_0.init()

        self.ad9910_0.sw.on()
        
        self.ad9910_0.set_att(self.Attenuation)

        freq1 = 80
        freq2 = 81
        # print(freq1, freq2)

        for i in range(int64(self.Cycles)):
            self.ad9910_0.set(frequency=freq1 * MHz, amplitude=self.Amplitude, phase=self.Phase)
            delay(self.freq_steps()*ms)
            freq1+=self.freq_steps()
            print((self.ad9910_0.get_frequency()) * 1e-6)

        # for i in range(int64(self.Cycles))

        print("AD9910 test is done")