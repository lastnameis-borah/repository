from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class redMOT_v2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl15")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Broadband_On:TTLOut=self.get_device("ttl5")
        self.Broadband_Off:TTLOut=self.get_device("ttl7")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Probe=self.get_device("urukul1_ch2")
        self.Single_Freq=self.get_device("urukul1_ch3")
        self.MOT_Coils=self.get_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=550))
        self.setattr_argument("Transfer_Time", NumberValue(default=20))
        self.setattr_argument("Holding_Time", NumberValue(default=5))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Camera.output()
        self.BMOT_TTL.output()
        self.RMOT_TTL.output()
        self.MOT_Coils.init()
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.Probe.cpld.init()
        self.Probe.init()
        self.Single_Freq.cpld.init()
        self.Single_Freq.init()

        # Set the channel ON
        self.BMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()
        # self.Probe.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Single_Freq.set_att(0.0)
        self.Single_Freq.set(frequency= 80 * MHz, amplitude=1.0)

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            # BMOT
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.06)

            # Zeeman Slower
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

            # Probe
            self.Probe.set(frequency= 65 * MHz, amplitude=0.25)

            with parallel:
                with sequential:
                    voltage = 0.52
                    self.MOT_Coils.write_dac(0, voltage)
                    self.MOT_Coils.load()
                self.BMOT_TTL.on()
                self.RMOT_TTL.on()
                self.Broadband_On.pulse(10*ms)
                self.Single_Freq.sw.off()
            

            # Slice 1 duration
            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Transfer ****************************

            # with parallel:
                # Magnetic field (2.2A)
                # with sequential:
            voltage = 3.36
            self.MOT_Coils.write_dac(0,voltage) 
            self.MOT_Coils.load()
            #0.52=3.5A, 0.91=3.0A, 1.44=2.5A, 1.95=2.1A, 2.0=2.0A, 2.2=1.8A, 2.42=1.6A, 2.55=1.5A, 3.05=1.0A, 3.36=0.7A

                # Zeeman Slower
                # with sequential:
            # self.ZeemanSlower.set_att(31.9)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.0)

            # BMOT
            # with sequential:
            steps = self.Transfer_Time
            t = self.Transfer_Time/steps
            for i in range(int64(steps)):
                amp_steps = 0.09/steps
                amp = 0.09 - ((i+1) * amp_steps)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
                delay(t*ms)

            self.BMOT_TTL.off()

            # **************************** Slice 3: Holding ****************************
            delay(self.Holding_Time*ms)

            # **************************** Slice 4: Compression ****************************
            voltage_com = 2.55
            steps_com = 8
            t = 8/steps_com
            change = (voltage - voltage_com)/steps_com
            for i in range(int64(steps_com)):
                voltage = voltage - change
                self.MOT_Coils.write_dac(0, voltage_com)
                self.MOT_Coils.load()
                delay(t*ms)

            #0.52=3.5A, 0.91=3.0A, 1.44=2.5A, 1.95=2.1A, 2.0=2.0A, 2.2=1.8A, 2.42=1.6A, 2.55=1.5A, 3.05=1.0A, 3.36=0.7A

            # **************************** Slice 5: Single Frequency ****************************
            # with parallel:
            #     self.Broadband_Off.pulse(10*ms)
            #     self.Single_Freq.sw.on()

            # delay(10*ms)

            # **************************** Slice 6: Shutter delay ****************************
            with parallel:
                self.RMOT_TTL.off()
                # self.Single_Freq.sw.off()
                # self.Probe.sw.on()
                self.BMOT_TTL.on()
            delay(3*ms)

            # **************************** Slice 5: Detection ****************************
            with parallel:
                self.Camera.pulse(10*ms)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.09)
                # self.Probe.set(frequency= 65 * MHz, amplitude=0.25)
            # self.Probe.sw.off()
            
            # **************************** Slice 7 ****************************
            
            # with parallel:

                # self.Broadband_On.pulse(10*ms)
                # self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
            delay(1000*ms)

        print("RedMOT exp complete!!")