from artiq.experiment import *

class SwitchingBoard(EnvExperiment):
    def build(self):

        self.setattr_device("core")
        self.setattr_device("zotino0")

        self.setattr_argument("Gate_Voltage", NumberValue()) 

    @kernel
    def run(self): 
    
        self.core.reset()
        self.core.break_realtime()

        self.zotino0.init()

        delay(200*us)

        self.zotino0.write_dac(0, self.Gate_Voltage)
        self.zotino0.load()

        print("Gate Voltage is set")