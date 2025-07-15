from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class blueMOT_probe_v1(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Pixelfly:TTLOut=self.get_device("ttl11")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Probe=self.get_device("urukul1_ch3")
        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.Probe_TTL:TTLOut=self.get_device("ttl8")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        self.Repump707:TTLOut=self.get_device("ttl4")
        self.Repump679:TTLOut=self.get_device("ttl9")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=500))
        self.setattr_argument("Time_of_Flight", NumberValue(default=10))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Camera.output()
        self.MOT_Coil_1.init()
        self.MOT_Coil_2.init()
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.Probe_TTL.output()
        self.Probe.cpld.init()
        self.Probe.init()


        self.BMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()
        self.Probe.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            self.BMOT_TTL.on()
            self.Zeeman_Slower_TTL.on()
            self.Repump707.on()
            self.Repump679.on()

            self.MOT_Coil_1.write_dac(0, 1.03)
            self.MOT_Coil_2.write_dac(1, 0.5)

            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()
            
            self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.08)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

            # Loading duration
            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Holding ****************************
            with parallel:
                self.BMOT_TTL.off()
                self.Repump707.off()
                self.Repump679.off()
                self.Zeeman_Slower_TTL.off()
            # delay(3.8*ms)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.00)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.0)

            # **************************** Slice 3: Detection ****************************
            self.MOT_Coil_1.write_dac(0, 4.05)
            self.MOT_Coil_2.write_dac(1, 4.08)

            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()


            delay(self.Time_of_Flight * ms)

            # self.Probe_TTL.on()
            # delay(3.0 *ms)
            self.Probe_TTL.on()
            delay(3.0 *ms)

            with parallel:
                self.Pixelfly.on()
                self.Camera.on()
            self.Probe.set(frequency= 65 * MHz, amplitude=0.02)
            
            delay(1.0*ms)

            # with parallel:
            #     self.Pixelfly.off()
            #     self.Camera.off()
            #     self.Probe_TTL.off()
            # self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
            
            # delay(100*ms)
            # self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.08)
            
            # # **************************** Slice 4 ****************************
            
            # delay(1000*ms)


        print("We got BlueMOT!")