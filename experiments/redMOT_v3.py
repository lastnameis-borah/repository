from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class redMOT_v3(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        self.Repump707:TTLOut=self.get_device("ttl4")
        self.Broadband_On:TTLOut=self.get_device("ttl5")
        self.Broadband_Off:TTLOut=self.get_device("ttl7")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Single_Freq=self.get_device("urukul1_ch2")
        self.Probe=self.get_device("urukul1_ch3")
        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=550))
        self.setattr_argument("Transfer_Time", NumberValue(default=5))
        self.setattr_argument("Holding_Time", NumberValue(default=5))
        self.setattr_argument("Compression_Time", NumberValue(default=8))
        self.setattr_argument("Single_Freq_Time", NumberValue(default=10))
        self.setattr_argument("Time_of_Flight", NumberValue(default=10))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Camera.output()
        self.BMOT_TTL.output()
        self.RMOT_TTL.output()
        self.Zeeman_Slower_TTL.output()
        self.Repump707.output()
        self.MOT_Coil_1.init()
        self.MOT_Coil_2.init()
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
        self.Probe.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Single_Freq.set_att(0.0)

        delay(500*ms)

        for i in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
            self.Probe.set(frequency= 65 * MHz, amplitude=0.00)

            voltage_1 = 1.03
            voltage_2 = 0.56
            self.MOT_Coil_1.write_dac(0, voltage_1)
            self.MOT_Coil_2.write_dac(1, voltage_2)

            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()
                self.BMOT_TTL.on()
                self.RMOT_TTL.on()
                self.Repump707.on()
                self.Broadband_On.pulse(10*ms)
                self.Single_Freq.sw.off()

            # Slice 1 duration
            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Transfer ****************************

            voltage_1 = 3.74
            voltage_2 = 3.76
            self.MOT_Coil_1.write_dac(0,voltage_1)
            self.MOT_Coil_2.write_dac(1,voltage_2)

            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()
                self.Zeeman_Slower_TTL.off()
                self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.0)

            steps = self.Transfer_Time
            t = self.Transfer_Time/steps
            for i in range(int64(steps)):
                amp_steps = 0.07/steps
                amp = 0.07 - ((i+1) * amp_steps)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
                delay(t*ms)
                
            with parallel:
                self.BMOT_TTL.off()
                self.Repump707.off()

            # **************************** Slice 3: Holding ****************************
            delay(self.Holding_Time*ms)

            with parallel:
                self.Broadband_Off.pulse(10*ms)
                self.Single_Freq.sw.on()

            # **************************** Slice 4: Compression ****************************

            voltage_1_com = 2.5 # 3.25 good
            voltage_2_com = 2.26
            red_amp = 0.18
            amp_com = 0.03
            steps_com = self.Compression_Time
            t_com = self.Compression_Time/steps_com
            volt_1_steps = (voltage_1 - voltage_1_com)/steps_com
            volt_2_steps = (voltage_2 - voltage_2_com)/steps_com
            amp_steps = (red_amp-amp_com)/steps_com

            with parallel:
                for i in range(int64(steps_com)):
                    voltage_1 = voltage_1 - volt_1_steps
                    voltage_2 = voltage_2 - volt_2_steps
                    self.MOT_Coil_1.write_dac(0, voltage_1_com)
                    self.MOT_Coil_2.write_dac(1, voltage_2_com)
                    with parallel:
                        self.MOT_Coil_1.load()
                        self.MOT_Coil_2.load()
                    delay(t_com*ms)

                for i in range(int64(steps_com)):
                    amp = red_amp - ((i+1) * amp_steps)
                    self.Single_Freq.set(frequency= 80 * MHz, amplitude=amp)
                    delay(t_com*ms)

            # **************************** Slice 5: Single Frequency ****************************
            delay(self.Single_Freq_Time*ms)

            # **************************** Slice 6: Time of Flight ******************************
            # with parallel:
            #     with sequential:
            #         self.MOT_Coil_1.write_dac(0, 4.07) 
            #         self.MOT_Coil_1.load()
            #     self.RMOT_TTL.off()
            # delay(self.Time_of_Flight*ms)

            # **************************** Slice 6: Shutter delay ****************************
            with parallel:
                self.RMOT_TTL.off()
                self.Single_Freq.sw.off()
                self.BMOT_TTL.on()
            delay(3.5*ms)

            # **************************** Slice 5: Detection ****************************
            self.MOT_Coil_1.write_dac(0, 2.5)
            self.MOT_Coil_2.write_dac(1, 2.26)
            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()

            with parallel:
                self.Camera.pulse(3.0*ms)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
            
            # **************************** Slice 7 ****************************
            delay(20*ms)
            self.BMOT_TTL.off()
            # self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
            
            delay(500*ms)

        print("RedMOT exp complete!!")