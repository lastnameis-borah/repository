from artiq.experiment import *
# from ndscan.experiment import Fragment

class printing(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ad9910_0 = self.get_device("urukul1_ch3")

    @kernel
    def run(self):
        print("AD9910 Register")