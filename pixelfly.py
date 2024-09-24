# from artiq.experiment import *
# from artiq.coredevice.ttl import TTLOut

# class pixelfly(EnvExperiment):
#     def build(self):
#         self.setattr_device("core")
#         self.camera:TTLOut=self.get_device("ttl12")

#     @kernel
#     def run(self):
#         self.core.reset()
#         self.core.break_realtime()

#         delay(500*ms)

#         # for i in range(10):
#         #     self.camera.pulse(10*ms)
#         #     delay(500*ms)


        # print("Done!")








from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class rf_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")

        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")


    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()


        
        self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
        self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.17)

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)

        delay(500*ms)

        for i in range(int64(100)):

            with parallel:
                self.BMOT_AOM.sw.on()
                self.ZeemanSlower.sw.on()
            delay(1*ms)
            with parallel:
                self.BMOT_AOM.sw.off()
                self.ZeemanSlower.sw.off()
            
            delay(5*ms)


        print("Test Complete!")