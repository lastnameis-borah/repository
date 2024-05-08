from artiq.experiment import *

class ZotinoSinglePulse(EnvExperiment):
    def build(self):

        self.setattr_device("core")
        self.setattr_device("zotino0")

    @kernel
    def run(self): 
    
        self.core.reset()
        self.core.break_realtime()

        self.zotino0.init()

        voltage = 9.0                             #0-9
        voltage2 = 0.0

        delay(200*us)
        

        self.zotino0.write_dac(0, voltage)
        self.zotino0.load()


        delay(400*ms)


        self.zotino0.write_dac(0, voltage2)
        self.zotino0.load()
        
        print("Zotino Pulse Test Complete")