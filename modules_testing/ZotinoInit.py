from artiq.experiment import *

class ZotinoInit(EnvExperiment):
    def build(self):

        self.setattr_device("core")
        self.setattr_device("zotino0")

    @kernel
    def run(self): 
    
        self.core.reset()
        self.core.break_realtime()

        self.zotino0.init()

        delay(1000*us)

        self.zotino0.write_dac(0, 0.0)
        self.zotino0.write_dac(1, 0.0)
        self.zotino0.write_dac(2, 0.0)
        self.zotino0.write_dac(3, 0.0)
        self.zotino0.write_dac(4, 0.0)
        self.zotino0.write_dac(5, 0.0)
        self.zotino0.write_dac(6, 0.0)
        self.zotino0.write_dac(7, 0.0)
        self.zotino0.write_dac(8, 0.0)
        self.zotino0.write_dac(9, 0.0)
        self.zotino0.load()


        print("Zotino set to zero")