from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class MagneticTrapLifetime_v2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Repump707:TTLOut=self.get_device("ttl4") 
        self.BMOT:TTLOut=self.get_device("ttl6")
        self.Flush:TTLOut=self.get_device("ttl13")
        self.Probe_TTL:TTLOut=self.get_device("ttl8")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.Pixelfly:TTLOut=self.get_device("ttl15")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.BMOT_AOM=self.get_device("urukul1_ch0")
        self.Probe=self.get_device("urukul1_ch3")
        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")

        self.setattr_argument("Cycles", NumberValue(default = 10))
        self.setattr_argument("Loading_Time", NumberValue(default = 1000))
        # self.setattr_argument("Holding_Time", NumberValue(default = 10))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        
        # Initialize the modules
        self.Camera.output()
        self.Pixelfly.output()
        self.BMOT.output()
        self.Repump707.output()
        # self.Flush.output()
        self.Zeeman_Slower_TTL.output()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.Probe.cpld.init()
        self.Probe.init()
        self.MOT_Coil_1.init()
        self.MOT_Coil_2.init()
        
        # Set the channel ON
        self.ZeemanSlower.sw.on()
        self.BMOT_AOM.sw.on()
        self.Probe.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)

        delay(500*ms)
        holding_time = 0

        for i in range(int64(self.Cycles)):
            # --------------------------------------Loading---------------------------------
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.08)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.35)

            self.MOT_Coil_1.write_dac(0, 0.976)
            self.MOT_Coil_2.write_dac(1, 0.53)

            with parallel:
                self.BMOT.on()
                self.Zeeman_Slower_TTL.on()
                # self.Flush.off()
                self.Repump707.off()
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()
            
            delay(self.Loading_Time* ms)

            # --------------------------------------Holding----------------------------------
            with parallel:
                self.Zeeman_Slower_TTL.off()
                self.BMOT.off()
                # self.Flush.on()
            
            delay(holding_time*ms)
            print("Holding Time: ", holding_time)
            holding_time += 500

            # --------------------------------------Detection--------------------------------
            self.Probe_TTL.on()
            self.Repump707.on()
            self.BMOT_AOM.set(frequency=10*MHz, amplitude=0.08)
            delay(4*ms)

            with parallel:
                self.Camera.on()
                self.Pixelfly.on()
                self.Probe.set(frequency=65*MHz, amplitude=0.02)
            
            delay(1.0 *ms)
            
            with parallel:
                self.Pixelfly.off()
                self.Camera.off()
                self.Probe_TTL.off()
                self.Probe.set(frequency=65*MHz, amplitude=0.00)

            # -------------------------------------Headroom----------------------------------
            delay(100*ms)
            with parallel:
                self.Repump707.off()
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.08)
                self.Probe.set(frequency= 65*MHz, amplitude=0.02)


        print("Trap Lifetime Experiment Complete!")