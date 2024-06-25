from artiq.experiment import *

class pickoff_coil(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.MOT_Coils=self.get_device("zotino0")
        self.setattr_argument("Cycle", NumberValue(default=10))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        self.MOT_Coils.init()

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # delay(10*ms)
            self.MOT_Coils.write_dac(0, 0.53) #2.8 = 1.8
            self.MOT_Coils.load()

            delay(1000*ms)

            self.MOT_Coils.write_dac(0, 4.09) #5.5 = 0
            self.MOT_Coils.load()

            delay(1000*ms)

            #0.52=3.5A, 0.91=3.0A, 1.44=2.5A, 1.95=2.1A, 2.0=2.0A, 2.2=1.8A, 2.42=1.6A, 2.55=1.5A, 3.05=1.0A, 3.36=0.7A, 4.13=0.0A

        print("exp complete!!")