from artiq.experiment import *

class ZotinoRamping(EnvExperiment):
    def build(self):

        self.setattr_device("core")
        self.setattr_device("zotino0")

        # self.setattr_argument("voltage", NumberValue())
        # self.setattr_argument("ramp_time", NumberValue(unit="ms"))

    @kernel
    def run(self): 
    
        self.core.reset()
        self.core.break_realtime()

        # delay(50000*ms)

        self.zotino0.init()
        delay(5000*ms)
        

        steps = 50
        voltage = 5.0
        ramp_time = 1000  #ms
        
        t = ramp_time/(steps-1)
        volt_steps = voltage/steps


        # Ramp Up

        for i in range(steps):
            volt = volt_steps * (i+1)
            self.zotino0.write_dac(0, volt)
            self.zotino0.load()
            delay(t*ms)
            
            print(volt)

        # Time between ramps
            
        # delay(4*ms)


        # Ramp Down

        # for i in range(steps):
        #     volt = voltage - (volt_steps * (i+1))
        #     self.zotino0.write_dac(0, volt)
        #     self.zotino0.load()
        #     delay(t*ms)
        #     i += 1
        
        print("Zotino Ramping Complete")