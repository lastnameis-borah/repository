from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class testt_AD9912(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.RMOT_Ref = self.get_device("urukul0_ch2")
        self.RMOT_AOM=self.get_device("urukul0_ch3")

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.RMOT_Ref.cpld.init()
        self.RMOT_Ref.init()
        self.RMOT_AOM.cpld.init()
        self.RMOT_AOM.init()

        self.RMOT_Ref.sw.on()
        self.RMOT_AOM.sw.on()
        self.RMOT_Ref.set(frequency=80*MHz)
        self.RMOT_AOM.set(frequency=80 * MHz)

        # for i in range(1):
            # self.RMOT_Ref.set_att(10.0)
            # delay(500*ms)
            # self.RMOT_Ref.set_att(31.9)
            # delay(500*ms)
        for i in range(10):
            red_amp = 1.0
            self.RMOT_AOM.set_att(red_amp)
            # delay(500*ms)
            amp_com = 31.0
            steps_com = 10
            t_com = 10/steps_com
            amp_steps = (amp_com-red_amp)/steps_com
            for i in range(int64(steps_com)):
                amp = red_amp + ((i+1)*amp_steps)
                self.RMOT_AOM.set_att(amp)
                delay(t_com*ms)
                # print(amp)
            delay(50*ms)
