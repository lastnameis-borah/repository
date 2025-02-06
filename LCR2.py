from artiq.experiment import *

class LCR2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.sampler = self.get_device("sampler0")
        self.LCR=self.get_device("zotino0")
        self.setattr_argument("Voltage", NumberValue(default=0))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.LCR.init()
        self.sampler.init()

        delay(1000*ms)

        self.LCR.write_dac(3, self.Voltage)

        self.LCR.load()
        print("Voltage set to", self.Voltage)