from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64
import logging, sys

class redMOT_v5(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Pixelfly:TTLOut=self.get_device("ttl11")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        self.Repump707:TTLOut=self.get_device("ttl4")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Single_Freq=self.get_device("urukul1_ch2")
        self.Probe=self.get_device("urukul1_ch3")
        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("RedMOT_ON", NumberValue(default=0))
        self.setattr_argument("Loading_Time", NumberValue(default=550))
        self.setattr_argument("Transfer_Time", NumberValue(default=5))
        self.setattr_argument("Holding_Time", NumberValue(default=5))
        self.setattr_argument("Compression_Time", NumberValue(default=8))
        self.setattr_argument("Single_Freq_Time", NumberValue(default=10))
        self.setattr_argument("Time_of_Flight", NumberValue(default=10))
        self.setattr_argument("Compression", NumberValue(default=0))
        self.setattr_argument("Single_Freq_ON", NumberValue(default=0))
        self.setattr_argument("RMOT_Probe_ON", NumberValue(default=0))

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
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        self.Probe.cpld.init()
        self.Probe.init()
        self.Single_Freq.cpld.init()
        self.Single_Freq.init()

        # Set the RF channels ON
        self.BMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()
        self.Single_Freq.sw.on()
        self.Probe.sw.on()

        # Set the RF attenuation
        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Probe.set_att(0.0)
        self.Single_Freq.set_att(0.0)

        for j in range(int64(self.Cycle)):
            ###########################################################################
            ###########################################################################

            ############################## BlueMOT Experiment ##########################

            ###########################################################################
            ###########################################################################

            if self.RedMOT_ON==0:
                # **************************** Slice 1: Loading ****************************
                self.BMOT_TTL.on()
                self.RMOT_TTL.on()
                self.Zeeman_Slower_TTL.on()
                self.Repump707.on()

                self.MOT_Coil_1.write_dac(0, 1.65)
                self.MOT_Coil_2.write_dac(1, 1.3)

                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()
                
                self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
                self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

                # Loading duration
                delay(self.Loading_Time*ms)


                # **************************** Slice 2: Holding ****************************
                self.BMOT_TTL.off()
                self.Repump707.off()
                self.Zeeman_Slower_TTL.off()
                # delay(3.5*ms)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.00)
                self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.0)

                # **************************** Slice 3: Detection ****************************
                self.MOT_Coil_1.write_dac(0, 4.07)
                self.MOT_Coil_2.write_dac(1, 4.06)

                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()

                delay(self.Time_of_Flight * ms)

                with parallel:
                    self.Pixelfly.on()
                    self.Camera.on()
                self.Probe.set(frequency= 65 * MHz, amplitude=0.17)

                delay(0.75*ms)

                with parallel:
                    self.Pixelfly.off()
                    self.Camera.off()

                self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
                
                delay(15*ms)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
                print("BMOT detected successfully!!")


            ###########################################################################
            ###########################################################################

            ############################## RedMOT Experiment ##########################

            ###########################################################################
            ###########################################################################


            if self.RedMOT_ON==1:
                # **************************** Slice 1: Loading ****************************
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
                self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
                red_amp = 0.13
                self.Single_Freq.set(frequency= 80 * MHz, amplitude=red_amp)
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

                delay(self.Loading_Time*ms)

                # **************************** Slice 2: Transfer ****************************

                voltage_1 = 3.77
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

                # **************************** Slice 4: Compression ****************************
                def Compression(self):
                # if self.Compression==1:
                    voltage_1_com = 2.5 # 3.25 good
                    voltage_2_com = 2.26
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
                    print("Compression complete!!")
                # elif self.Compression==0:
                #     pass
                # else:
                #     logging.error("Compression should be either 0 or 1")
                #     sys.exit(1)

                # **************************** Slice 5: Single Frequency ****************************
                if self.Compression==1 and self.Single_Freq_ON==1:
                    Compression()
                    delay(self.Single_Freq_Time*ms)
                    print("Single Frequency RMOT achieved!!")
                elif self.Compression==0 and self.Single_Freq_ON==1:
                    logging.error("Select Compression as 1 to enable Single Frequency")
                    sys.exit(1)
                elif self.Compression==0 and self.Single_Freq_ON==0:
                    pass
                elif self.Compression==1 and self.Single_Freq_ON==0:
                    Compression()
                else:
                    logging.error("Single Frequency should be either 0 or 1")
                    sys.exit(1)

                # **************************** Slice 6: Detection : MOT as Probe****************************
                if self.RMOT_Probe_ON==0:
                    with parallel:
                        self.RMOT_TTL.off()
                        self.BMOT_TTL.on()
                    delay(3.5*ms)

                    self.MOT_Coil_1.write_dac(0, 2.5)
                    self.MOT_Coil_2.write_dac(1, 2.26)

                    with parallel:
                        self.MOT_Coil_1.load()
                        self.MOT_Coil_2.load()

                    delay(self.Time_of_Flight*ms)

                    with parallel:
                        self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
                        self.Pixelfly.pulse(3.0*ms)
                        self.Camera.pulse(3.0*ms)
                        
                    delay(20.0*ms)
                    self.BMOT_TTL.off()

                    print("Detected with MOT as probe!!")

                # **************************** Slice 6: Detection - Seperate Probe**************************
                elif self.RMOT_Probe_ON==1:
                    self.RMOT_TTL.off()
                    delay(3.5*ms)

                    self.MOT_Coil_1.write_dac(0, 4.05)
                    self.MOT_Coil_2.write_dac(1, 4.08)

                    with parallel:
                        self.MOT_Coil_1.load()
                        self.MOT_Coil_2.load()

                    delay(self.Time_of_Flight*ms)
                    
                    self.Probe.set(frequency= 65 * MHz, amplitude=0.17)

                    with parallel:
                        self.Camera.on()
                        self.Pixelfly.on()
                    
                    delay(5*ms)
                    
                    with parallel:
                        self.Pixelfly.off()
                        self.Camera.off()
                    
                    self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
                    self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)

                    print("RMOT Detected with seperate probe!!")
                
                else:
                    logging.error("Select either, 0: MOT as Probe 1: Seperate Probe")
                    sys.exit(1)
            
            if j==int64(self.Cycle)-1 and self.RedMOT_ON==0:
                print(" We got BMOT!!")
            
            elif j==int64(self.Cycle)-1 and self.RedMOT_ON==1:
                print("We got RedMOT!!")
            
            else:
                # logging.error("Select either 0 or 1 for RedMOT_ON")
                # sys.exit(0)
                pass

            # **************************** Headroom ****************************
            delay(500*ms)