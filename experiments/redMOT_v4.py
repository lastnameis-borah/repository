from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class redMOT_v4(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Single_Freq=self.get_device("urukul1_ch2")
        self.Probe=self.get_device("urukul1_ch3")
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
        self.Single_Freq.sw.on()
        self.Probe.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Probe.set(frequency= 65 * MHz, amplitude=0.17)
        self.Single_Freq.set_att(0.0)

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            # BMOT
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.06)

            # Zeeman Slower
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

            # Single Frequency
            red_amp = 0.13
            self.Single_Freq.set(frequency= 80 * MHz, amplitude=red_amp)

            # Probe
            self.Probe.set(frequency= 65 * MHz, amplitude=0.00)

            with parallel:
                with sequential:
                    voltage = 1.0
                    self.MOT_Coils.write_dac(0, voltage)
                    self.MOT_Coils.load()
                self.BMOT_TTL.on()
                self.RMOT_TTL.on()

            # Slice 1 duration
            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Transfer ****************************

            # with parallel:
                # Magnetic field (2.2A)
                # with sequential:
            voltage = 2.75
            self.MOT_Coils.write_dac(0,voltage) 
            self.MOT_Coils.load()

                # Zeeman Slower
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.0)

            # BMOT
            # with sequential:
            steps = self.Transfer_Time
            t = self.Transfer_Time/steps
            for i in range(int64(steps)):
                amp_steps = 0.06/steps
                amp = 0.06 - ((i+1) * amp_steps)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
                delay(t*ms)

            self.BMOT_TTL.off()

            # **************************** Slice 3: Holding ****************************
            delay(self.Holding_Time*ms)

            # **************************** Slice 4: Compression ****************************
            # voltage_com = 2.75
            # amp_com = 0.13
            # steps_com = 8
            # t_com = 8/steps_com
            # volt_steps = (voltage - voltage_com)/steps_com
            # amp_steps = (red_amp-amp_com)/steps_com

            # with parallel:
            #     for i in range(int64(steps_com)):
            #         voltage = voltage - volt_steps
            #         self.MOT_Coils.write_dac(0, voltage_com)
            #         self.MOT_Coils.load()
            #         delay(t_com*ms)

            #     for i in range(int64(steps_com)):
            #         amp = 1.0 - ((i+1) * amp_steps)
            #         self.Single_Freq.set(frequency= 80 * MHz, amplitude=amp)
            #         delay(t_com*ms)
            #         print(amp)


            # # **************************** Slice 5: Single Frequency ****************************
            # delay(10*ms)

            # **************************** Slice 6: Shutter delay ****************************
            with parallel:
                self.RMOT_TTL.off()
                self.BMOT_TTL.on()
            delay(3.5*ms)

            # **************************** Slice 5: Detection ****************************
            with parallel:
                # self.Probe.sw.on()
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.06)
                self.Camera.pulse(10*ms)
            # self.Probe.sw.off()
            # self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.00)
            
            # **************************** Slice 7 ****************************
            delay(100*ms)

        print("RedMOT exp complete!!")