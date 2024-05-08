from artiq.experiment import *
from artiq.coredevice.sampler import Sampler


class SuServo1(EnvExperiment):
    def build(self):

        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.sampler:Sampler = self.get_device("sampler0")

    @kernel
    def run(self): 

        self.core.reset()
        self.core.break_realtime()

        self.zotino0.init()
        self.sampler.init()

        samples = [0.0]*8

        delay(500*us)
        
        # with parallel:
        #     with sequential:
        self.zotino0.write_dac(0, 8.0)
        # self.zotino0.write_dac(1, 8.0)
        self.zotino0.load()

            # with sequential:
        for i in range(1):
            self.sampler.sample(samples)


        print(samples)

        print("SuServo Test Complete")
