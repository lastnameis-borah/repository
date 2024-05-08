from artiq.experiment import *
from artiq.coredevice.sampler import Sampler


class SuServoVoltage(EnvExperiment):
    def build(self):

        self.setattr_device("core")
        self.setattr_device("zotino0")
        self.sampler:Sampler = self.get_device("sampler0")

        self.setattr_argument("sample_rate", NumberValue())
        self.setattr_argument("sample_number", NumberValue())

    @kernel
    def run(self): 

        self.core.reset()
        self.core.break_realtime()

        self.zotino0.init()
        self.sampler.init()
        
        num_samples = int32(self.sample_number)
        samples = [[0.0 for i in range(8)] for i in range(num_samples)]
        samples2 = [[0.0 for i in range(8)] for i in range(num_samples)]
        sampling_period = 1/self.sample_rate

        delay(500*us)
        
        with parallel:
            with sequential:
                self.zotino0.write_dac(0, 8.0)
                self.zotino0.load()
                
            with sequential:
                for j in range(num_samples):
                    self.sampler.sample(samples[j])
                    delay(sampling_period * s)


        single = [i[0] for i in samples]
        print(single)

        with parallel:
            with sequential:
                if single[1] > 7.5 and single[1] <= 8.0:
                    self.zotino0.write_dac(1, 5.0)
                    self.zotino0.load()

            with sequential:
                for j in range(num_samples):
                    self.sampler.sample(samples2[j])
                    delay(sampling_period * s)

        single2 = [i[1] for i in samples]
        print(single2)
        
        print("SuServo Test Complete")
