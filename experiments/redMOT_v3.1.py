from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class redMOT_v3_1(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.Pixelfly:TTLOut=self.get_device("ttl15")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.Probe_TTL:TTLOut=self.get_device("ttl8")
        self.Broadband_On:TTLOut=self.get_device("ttl5")
        self.Broadband_Off:TTLOut=self.get_device("ttl7")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        self.Repump707:TTLOut=self.get_device("ttl4")
        self.Repump679:TTLOut=self.get_device("ttl9")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Single_Freq=self.get_device("urukul1_ch2")
        self.Probe=self.get_device("urukul1_ch3")
        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")
        self.Flush:TTLOut=self.get_device("ttl13")

        self.Ref = self.get_device("urukul0_ch3")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Probe_ON", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=2000))
        self.setattr_argument("Transfer_Time", NumberValue(default=15))
        self.setattr_argument("Holding_Time", NumberValue(default=10))
        self.setattr_argument("Compression_Time", NumberValue(default=10))
        self.setattr_argument("Single_Freq_Time", NumberValue(default=20))
        self.setattr_argument("Time_of_Flight", NumberValue(default=0))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Pixelfly.output()
        self.Camera.output()
        self.BMOT_TTL.output()
        self.Probe_TTL.output()
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
        self.Flush.output()

        self.Ref.cpld.init()
        self.Ref.init()

        # Set the RF channels ON
        self.BMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()
        self.Probe.sw.on()

        # Set the RF attenuation
        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Single_Freq.set_att(0.0)

        self.Ref.set(frequency=80 * MHz)
        self.Ref.set_att(10.0)

        for j in range(int64(self.Cycle)):
            # **************************** Slice 1: Loading ****************************
            delay(0.5*ms)
            # blue_amp = 0.08
            self.BMOT_AOM.set(frequency=90 * MHz, amplitude=0.08)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
            self.Probe.set(frequency=65 * MHz, amplitude=0.02)
            self.Single_Freq.set(frequency=80 * MHz, amplitude=0.35)
            
            voltage_1 = 1.07
            voltage_2 = 0.54
            self.MOT_Coil_1.write_dac(0, voltage_1)
            self.MOT_Coil_2.write_dac(1, voltage_2)

            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()
                self.BMOT_TTL.on()
                self.Probe_TTL.off()
                self.Broadband_On.pulse(10*ms)
                self.Single_Freq.sw.off()
                self.Zeeman_Slower_TTL.on()
                self.Repump707.on()
                self.Repump679.on()
                # self.Flush.off()

            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Transfer ****************************
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.00)
            self.Zeeman_Slower_TTL.off()
            # self.Flush.on()
            delay(4.0*ms)

            # voltage_1_Tr = 3.77
            # voltage_2_Tr = 2.0
            # self.MOT_Coil_1.write_dac(0, voltage_1_Tr)
            # self.MOT_Coil_2.write_dac(1, voltage_2_Tr)

            # steps_tr = self.Transfer_Time
            # t_tr = self.Transfer_Time/steps_tr
            # volt_1_steps = (voltage_1_Tr - voltage_1)/steps_tr
            # volt_2_steps = (voltage_2_Tr - voltage_2)/steps_tr

            # with parallel:
            #     for i in range(int64(steps_tr)):
            #         voltage_1 = voltage_1 + volt_1_steps
            #         voltage_2 = voltage_2 + volt_2_steps
            #         self.MOT_Coil_1.write_dac(0, voltage_1)
            #         self.MOT_Coil_2.write_dac(1, voltage_2)
            #         with parallel:
            #             self.MOT_Coil_1.load()
            #             self.MOT_Coil_2.load()
            #         delay(t_tr*ms)
            
            #     for i in range(int64(steps_tr)):
            #         amp_steps = 0.08/steps_tr
            #         amp = 0.08 - ((i+1) * amp_steps)
            #         self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
            #         delay(t_tr*ms)
            #         if i == int64(steps_tr) - 4:
            #             with parallel:
            #                 self.BMOT_TTL.off()
            #                 self.Repump707.off()
            #                 self.Repump679.off()

            steps_tr = self.Transfer_Time
            t_tr = self.Transfer_Time/steps_tr
            amp_steps = (0.08 - 0.003)/steps_tr
            blue_freq = 90.0
            blue_freq_tr = 90.2
            freq_steps = (blue_freq_tr - blue_freq)/steps_tr

            # Ramping the amplitude of the blue MOT beam
            for i in range(int64(steps_tr)):
                amp = 0.08 - ((i+1) * amp_steps)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
                delay(t_tr*ms)

            # Ramping the frequency and amplitude of the blue MOT beam
            # for i in range(int64(steps_tr)):
            #     amp = 0.08 - ((i+1) * amp_steps)
            #     freq = blue_freq + ((i+1) * freq_steps)
            #     self.BMOT_AOM.set(frequency=freq*MHz, amplitude=amp)
            #     delay(t_tr*ms)
            
            delay(200*ms)

            with parallel:
                self.BMOT_TTL.off()
                self.Repump707.off()
                self.Repump679.off()

            delay(4*ms)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.08)

            voltage_1_Tr = 4.012
            voltage_2_Tr = 4.027
            self.MOT_Coil_1.write_dac(0, voltage_1_Tr)
            self.MOT_Coil_2.write_dac(1, voltage_2_Tr)
            self.MOT_Coil_1.load()
            self.MOT_Coil_2.load()

            # **************************** Slice 3: Broadband RedMOT ****************************
            delay(self.Holding_Time*ms)

            # **************************** Slice 4: Compression ****************************
            with parallel:
                self.Broadband_Off.pulse(10*ms)
                self.Single_Freq.sw.on()

            voltage_1_com = 2.54
            voltage_2_com = 2.28
            red_amp = 0.35
            amp_com = 0.02
            red_freq = 80.0
            red_freq_com = 80.3
            steps_com = self.Compression_Time
            t_com = self.Compression_Time/steps_com
            volt_1_steps = (voltage_1_Tr - voltage_1_com)/steps_com
            volt_2_steps = (voltage_2_Tr - voltage_2_com)/steps_com
            amp_steps = (red_amp-amp_com)/steps_com
            freq_steps = (red_freq_com - red_freq)/steps_com

            with parallel:
                for i in range(int64(steps_com)):
                    voltage_1 = voltage_1 - volt_1_steps
                    voltage_2 = voltage_2 - volt_2_steps
                    self.MOT_Coil_1.write_dac(0, voltage_1)
                    self.MOT_Coil_2.write_dac(1, voltage_2)
                    with parallel:
                        self.MOT_Coil_1.load()
                        self.MOT_Coil_2.load()
                    delay(t_com*ms)

                for i in range(int64(steps_com)):
                    amp = red_amp - ((i+1) * amp_steps)
                    freq = red_freq + ((i+1) * freq_steps)
                    self.Single_Freq.set(frequency=freq*MHz, amplitude=amp)
                    delay(t_com*ms)

            # **************************** Slice 5: Single Frequency ****************************
            self.Single_Freq.set(frequency=80.3*MHz, amplitude=amp_com)
            delay(self.Single_Freq_Time*ms)
            self.Single_Freq.sw.off()
            
            # **************************** Slice 5: Detection : MOT as Probe*****************************
            if self.Probe_ON == 0:
                with parallel:
                    self.Probe_TTL.off()
                    self.BMOT_TTL.on()
                delay(3.8*ms)

                self.MOT_Coil_1.write_dac(0, 4.055)
                self.MOT_Coil_2.write_dac(1, 4.083)
                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()

                delay(self.Time_of_Flight*ms)

                with parallel:
                    self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.08)
                    self.Pixelfly.pulse(5.0*ms)
                    self.Camera.pulse(3.0*ms)

                if j==int64(self.Cycle)-1:
                    print("RedMOT detected with MOT beam as Probe!!")

            # **************************** Slice 5: Detection - Seperate Probe**************************
            if self.Probe_ON == 1:
                self.MOT_Coil_1.write_dac(0, 4.08)
                self.MOT_Coil_2.write_dac(1, 4.11)
                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()

                delay(self.Time_of_Flight*ms)

                self.Probe_TTL.on()
                self.BMOT_AOM.set(frequency=10*MHz, amplitude=0.08)
                delay(2.8*ms)

                with parallel:
                    self.Camera.on()
                    self.Pixelfly.on()
                    self.Probe.set(frequency=65*MHz, amplitude=0.02)
                    self.Ref.sw.on()
                # delay(1000000*ms)
                delay(0.5 *ms)
                
                with parallel:
                    self.Pixelfly.off()
                    self.Camera.off()
                    self.Ref.sw.off()
                    self.Probe_TTL.off()
                    self.Probe.set(frequency=65*MHz, amplitude=0.00)

                if j==int64(self.Cycle)-1:
                    print("RedMOT detected with Probe beam!!")
            
            # **************************** Slice 4 ****************************
            # delay(100.0*ms)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.08)
            self.Probe.set(frequency= 65*MHz, amplitude=0.02)
            self.Broadband_On.pulse(10*ms)
            # self.BMOT_TTL.on()
            delay(1000*ms)