from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64, int32, float64

class red_mod_rpc(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Single_Freq=self.get_device("urukul1_ch2")

        self.setattr_argument("Cycles", NumberValue(default=1))
        self.setattr_argument("Start_Freq", NumberValue(default=80.0, unit="MHz", ndecimals=3))
        self.setattr_argument("End_Freq", NumberValue(default=81.0, unit="MHz", ndecimals=3))
        self.setattr_argument("Modulation_Freq", NumberValue(default=0.025, unit="MHz", ndecimals=3))

    @rpc
    def set_modulation(self):
        self.start_freq = self.Start_Freq # MHz
        self.stop_freq = self.End_Freq # MHz
        self.modulation_freq = self.Modulation_Freq # 25 kHz in Hz
        self.freq_step = (self.stop_freq - self.start_freq) / (self.modulation_freq)  # MHz
        self.time_step = (1 / self.modulation_freq) * 1e6 # microseconds
        return int64(self.freq_step), int64(self.time_step)

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.Single_Freq.cpld.init()
        self.Single_Freq.init()
        self.Single_Freq.sw.on()
        delay(500*ms)

        freq = self.Start_Freq
        print(self.set_modulation())
        # time_step = self.set_modulation[1]
        # freq_step = self.set_modulation[0]

        # for i in range(40):
        #     self.Single_Freq.set(frequency=freq*MHz, amplitude=0.5, phase=0.0)
        #     delay(time_step*us)
        #     freq += freq_step
        # print(self.Single_Freq.get_frequency() * 1e-6, "MHz")