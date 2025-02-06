from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class redMOT_v4_1_MOT(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.Pixelfly:TTLOut=self.get_device("ttl11")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        self.Repump707:TTLOut=self.get_device("ttl4")
        self.Repump679:TTLOut=self.get_device("ttl9")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.RMOT_AOM=self.get_device("urukul0_ch0")
        self.Probe=self.get_device("urukul1_ch3")
        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")

        self.Ref = self.get_device("urukul0_ch3")
        self.TTL = self.get_device("ttl14")

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
        self.Pixelfly.output()
        self.Camera.output()
        self.BMOT_TTL.output()
        self.RMOT_TTL.output()
        self.Zeeman_Slower_TTL.output()
        self.Repump707.output()
        self.MOT_Coil_1.init()
        self.MOT_Coil_2.init()
        self.BMOT_AOM.cpld.init()
        self.BMOT_AOM.init()
        self.RMOT_AOM.cpld.init()
        self.RMOT_AOM.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.Probe.cpld.init()
        self.Probe.init()

        self.Ref.cpld.init()
        self.TTL.output()
        self.Ref.init()

        # Set the RF channels ON
        self.BMOT_AOM.sw.on()
        self.RMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()
        self.Probe.sw.on()

        # Set the RF attenuation
        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.RMOT_AOM.set(frequency= 80 * MHz)

        self.Ref.set(frequency=80 * MHz)
        self.Ref.set_att(10.0)

        for i in range(int64(self.Cycle)):

            # **************************** Slice 1: Loading ****************************
            delay(500*ms)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
            red_att = 10.0
            self.RMOT_AOM.set_att(red_att)
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
                self.Zeeman_Slower_TTL.on()
                self.Repump707.on()
                self.Repump679.on()
                self.Ref.sw.on()

            delay(self.Loading_Time*ms)

            # **************************** Slice 2: Transfer ****************************

            voltage_1_Tr = 3.77
            voltage_2_Tr = 3.76
            steps_tr = self.Transfer_Time
            t_tr = self.Transfer_Time/steps_tr
            volt_1_steps = (voltage_1_Tr - voltage_1)/steps_tr
            volt_2_steps = (voltage_2_Tr - voltage_2)/steps_tr
            
            with parallel:
                for i in range(int64(steps_tr)):
                    voltage_1 = voltage_1 + volt_1_steps
                    voltage_2 = voltage_2 + volt_2_steps
                    self.MOT_Coil_1.write_dac(0, voltage_1)
                    self.MOT_Coil_2.write_dac(1, voltage_2)
                    with parallel:
                        self.MOT_Coil_1.load()
                        self.MOT_Coil_2.load()
                    delay(t_tr*ms)
            
                for i in range(int64(steps_tr)):
                    amp_steps = 0.07/steps_tr
                    amp = 0.07 - ((i+1) * amp_steps)
                    self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
                    delay(t_tr*ms)
                    if i == int64(steps_tr) - 4:
                        with parallel:
                            self.BMOT_TTL.off()
                            self.Zeeman_Slower_TTL.off()
                            self.Repump707.off()
                            self.Repump679.off()

            # voltage_1_Tr = 3.77
            # voltage_2_Tr = 3.76
            # steps_tr = self.Transfer_Time
            # t_tr = self.Transfer_Time/steps_tr
            
            # self.MOT_Coil_1.write_dac(0, voltage_1_Tr)
            # self.MOT_Coil_2.write_dac(1, voltage_2_Tr)
            # self.MOT_Coil_1.load()
            # self.MOT_Coil_2.load()
            
            # for i in range(int64(steps_tr)):
            #     amp_steps = 0.07/steps_tr
            #     amp = 0.07 - ((i+1) * amp_steps)
            #     self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
            #     delay(t_tr*ms)
            #     if i == int64(steps_tr) - 4:
            #         with parallel:
            #             self.BMOT_TTL.off()
            #             self.Zeeman_Slower_TTL.off()
            #             self.Repump707.off()
            #             self.Repump679.off()
            
            # **************************** Slice 3: Holding ****************************
            delay(self.Holding_Time*ms)

            # **************************** Slice 4: Compression ****************************
            voltage_1_com = 2.5 # 3.25 good
            voltage_2_com = 2.26
            att_com = 31.0
            steps_com = self.Compression_Time * 4
            t_com = self.Compression_Time/steps_com
            volt_1_steps = (voltage_1_Tr - voltage_1_com)/steps_com
            volt_2_steps = (voltage_2_Tr - voltage_2_com)/steps_com
            att_steps = (att_com - red_att)/steps_com
            
            with parallel:
                self.Ref.sw.off()
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
                    att = red_att + ((i+1)*att_steps)
                    self.RMOT_AOM.set_att(att)
                    delay(t_com*ms)

            # **************************** Slice 5: Single Frequency ****************************
            self.Ref.sw.on()
            delay(self.Single_Freq_Time*ms)
            self.Ref.sw.off()
            # **************************** Slice 6: Shutter delay ****************************
            
            with parallel:
                self.RMOT_TTL.off()
                # self.BMOT_TTL.on()
            delay(4.0*ms)

            # **************************** Slice 5: Detection : MOT as Probe****************************
            # self.MOT_Coil_1.write_dac(0, 2.5)
            # self.MOT_Coil_2.write_dac(1, 2.26)
            # with parallel:
            #     self.MOT_Coil_1.load()
            #     self.MOT_Coil_2.load()

            # # delay(self.Time_of_Flight*ms)

            # with parallel:
            #     self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
            #     self.Pixelfly.pulse(5.0*ms)
            #     self.Camera.pulse(3.0*ms)
            

            # **************************** Slice 5: Detection - Seperate Probe**************************
            self.MOT_Coil_1.write_dac(0, 4.055)
            self.MOT_Coil_2.write_dac(1, 4.083)
            with parallel:
                self.MOT_Coil_1.load()
                self.MOT_Coil_2.load()

            delay(self.Time_of_Flight*ms)

            with parallel:
                self.Camera.on()
                self.Pixelfly.on()
                self.Probe.set(frequency= 65 * MHz, amplitude=0.07)
            
            delay(0.75*ms)
            
            with parallel:
                self.Pixelfly.off()
                self.Camera.off()
            self.Probe.set(frequency= 65 * MHz, amplitude=0.00)

            delay(20.0*ms)
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
            
            # **************************** Slice 4 ****************************
            delay(500*ms)

        print("RedMOT exp complete!!")