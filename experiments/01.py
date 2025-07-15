from artiq.experiment import *

class Idle_State(EnvExperiment):
    def build(self):
        self.setattr_device("core")

        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.MOT_Coil_1.init()
        self.MOT_Coil_2.init()

        delay(1000*ms)

        self.MOT_Coil_1.write_dac(0, 4.055)
        self.MOT_Coil_2.write_dac(1, 4.083)

        with parallel:
            self.MOT_Coil_1.load()
            self.MOT_Coil_2.load()

        print("Coils set to ZERO!")