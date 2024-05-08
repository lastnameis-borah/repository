from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut

class MagneticTrapLifetime(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttlIN1:TTLOut=self.get_device("ttl4") 
        self.ttlIN2:TTLOut=self.get_device("ttl5")

    @kernel
    def run(self):
        self.core.reset()

        self.core.break_realtime()

        delay(1000*us)

        for i in range(1):

            with parallel:

                with sequential:
                    pass

                with sequential:
                    pass
                
                with sequential:
                    self.ttlIN1.off()
                    delay(500 * ms)
                    delay(1 * ms)
                    self.ttlIN1.pulse(36 * ms)

                with sequential:
                    self.ttlIN2.pulse(500 * ms)
                    delay(1 * ms)
                    self.ttlIN2.pulse(36 * ms)


        # for i in range(10):

        #     with parallel:
        #         with sequential:
        #             self.ttlIN1.pulse(10 * ms)
        #             delay(10 * ms)

        #         with sequential:
        #             self.ttlIN2.pulse(10 * ms)
        #             delay(10 * ms)


        print("Experiment Complete")