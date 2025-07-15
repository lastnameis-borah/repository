from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64
import logging, sys

class redMOT_v5(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Pixelfly:TTLOut=self.get_device("ttl11")
        self.Andor:TTLOut=self.get_device("ttl10")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Zeeman_Slower_TTL:TTLOut=self.get_device("ttl12")
        self.Repump707:TTLOut=self.get_device("ttl4")
        self.Repump679:TTLOut=self.get_device("ttl9")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Single_Freq=self.get_device("urukul1_ch2")
        self.Probe=self.get_device("urukul1_ch3")
        self.MOT_Coil_1=self.get_device("zotino0")
        self.MOT_Coil_2=self.get_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("RedMOT_ON", NumberValue(default=0))

        self.setattr_argument("BMOT_Coil1_Voltage", NumberValue(default=1.03))
        self.setattr_argument("BMOT_Coil2_Voltage", NumberValue(default=0.56))
        self.setattr_argument("Loading_Time", NumberValue(default=1000))

        self.setattr_argument("BrRMOT_Coil1_Voltage", NumberValue(default=3.77))
        self.setattr_argument("BrRMOT_Coil2_Voltage", NumberValue(default=3.76))
        self.setattr_argument("Transfer_Time", NumberValue(default=15))
        self.setattr_argument("BrRMOT_Holding_Time", NumberValue(default=5))

        self.setattr_argument("Compression", NumberValue(default=0))
        self.setattr_argument("Com_Amplitude", NumberValue(default=0.03))
        self.setattr_argument("Com_Coil1_Voltage", NumberValue(default=2.5))
        self.setattr_argument("Com_Coil2_Voltage", NumberValue(default=2.26))
        self.setattr_argument("Compression_Time", NumberValue(default=5))

        self.setattr_argument("Single_Freq_ON", NumberValue(default=0))
        self.setattr_argument("Single_Freq_Time", NumberValue(default=20))

        self.setattr_argument("Time_of_Flight", NumberValue(default=0))

        self.setattr_argument("RMOT_Probe_ON", NumberValue(default=0))
        self.setattr_argument("Detection_Coil1_Voltage", NumberValue(default=4.07))
        self.setattr_argument("Detection_Coil2_Voltage", NumberValue(default=4.06))
        self.setattr_argument("Detection_Pulse", NumberValue(default=3.0))

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.Pixelfly.output()
        self.Andor.output()
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
                self.Repump679.on()

                self.MOT_Coil_1.write_dac(0, self.BMOT_Coil1_Voltage)
                self.MOT_Coil_2.write_dac(1, self.BMOT_Coil2_Voltage)

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
                self.Repump679.off()
                self.Zeeman_Slower_TTL.off()
                # delay(3.5*ms)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.00)
                self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.0)

                # **************************** Slice 3: Detection ****************************
                self.MOT_Coil_1.write_dac(0, self.Detection_Coil1_Voltage)
                self.MOT_Coil_2.write_dac(1, self.Detection_Coil2_Voltage)

                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()

                delay(self.Time_of_Flight * ms)

                with parallel:
                    self.Pixelfly.on()
                    self.Andor.on()
                self.Probe.set(frequency= 65 * MHz, amplitude=0.17)

                delay(self.Detection_Pulse*ms)

                with parallel:
                    self.Pixelfly.off()
                    self.Andor.off()

                self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
                
                delay(15*ms)
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
                
                if j==int64(self.Cycle)-1:
                    print("BMOT detected with probe beam!!")


            ###########################################################################
            ###########################################################################

            ######################### RedMOT Experiment ###############################

            ###########################################################################
            ###########################################################################


            elif self.RedMOT_ON==1:
                # **************************** Slice 1: Loading ****************************
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
                self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
                red_amp = 0.13
                self.Single_Freq.set(frequency= 80 * MHz, amplitude=red_amp)
                self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
                
                self.MOT_Coil_1.write_dac(0, self.BMOT_Coil1_Voltage)
                self.MOT_Coil_2.write_dac(1, self.BMOT_Coil2_Voltage)

                with parallel:
                    self.MOT_Coil_1.load()
                    self.MOT_Coil_2.load()

                    self.BMOT_TTL.on()
                    self.RMOT_TTL.on()
                    self.Zeeman_Slower_TTL.on()
                    self.Repump707.on()

                delay(self.Loading_Time*ms)

                # **************************** Slice 2: Transfer ****************************

                self.MOT_Coil_1.write_dac(0,self.BrRMOT_Coil1_Voltage)
                self.MOT_Coil_2.write_dac(1,self.BrRMOT_Coil2_Voltage)

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

                # **************************** Slice 3: BrRMOT Holding ****************************
                delay(self.BrRMOT_Holding_Time*ms)
                if j==int64(self.Cycle)-1:
                        print("Broadband RMOT achieved!!")

                # **************************** Slice 4: Compression ****************************
                if self.Compression==1:
                    # voltage_1_com = 2.5 # 3.25 good
                    # voltage_2_com = 2.26
                    amp_com = self.Com_Amplitude
                    steps_com = self.Compression_Time
                    t_com = self.Compression_Time/steps_com
                    volt_1_steps = (self.BrRMOT_Coil1_Voltage - self.Com_Coil1_Voltage)/steps_com
                    volt_2_steps = (self.BrRMOT_Coil2_Voltage - self.Com_Coil2_Voltage)/steps_com
                    amp_steps = (red_amp-amp_com)/steps_com

                    with parallel:
                        for i in range(int64(steps_com)):
                            voltage_1 = self.BrRMOT_Coil1_Voltage - volt_1_steps
                            voltage_2 = self.BrRMOT_Coil2_Voltage - volt_2_steps
                            self.MOT_Coil_1.write_dac(0, voltage_1)
                            self.MOT_Coil_2.write_dac(1, voltage_2)
                            with parallel:
                                self.MOT_Coil_1.load()
                                self.MOT_Coil_2.load()
                            delay(t_com*ms)

                        for i in range(int64(steps_com)):
                            amp = red_amp - ((i+1) * amp_steps)
                            self.Single_Freq.set(frequency= 80 * MHz, amplitude=amp)
                            delay(t_com*ms)
                    
                    if j==int64(self.Cycle)-1:
                        print("Compression complete!!")
                elif self.Compression==0:
                    pass
                else:
                    logging.error("Compression should be either 0 or 1")
                    sys.exit(1)

                # **************************** Slice 5: Single Frequency ****************************
                if self.Single_Freq_ON==1:
                    if self.Compression==1:
                        delay(self.Single_Freq_Time*ms)
                        if j==int64(self.Cycle)-1:
                            print("Single Frequency RMOT achieved!!")
                    elif self.Compression==0:
                        logging.error("Select Compression as 1 to enable Single Frequency")
                        sys.exit(1)
                elif self.Single_Freq_ON==0:
                    pass
                else:
                    logging.error("Single Frequency should be either 0 or 1")
                    sys.exit(1)

                # **************************** Slice 6: Detection : MOT as Probe****************************
                if self.RMOT_Probe_ON==0:
                    with parallel:
                        self.RMOT_TTL.off()
                        self.BMOT_TTL.on()
                    delay(3.5*ms)

                    self.MOT_Coil_1.write_dac(0, self.Detection_Coil1_Voltage)
                    self.MOT_Coil_2.write_dac(1, self.Detection_Coil2_Voltage)

                    with parallel:
                        self.MOT_Coil_1.load()
                        self.MOT_Coil_2.load()

                    delay(self.Time_of_Flight*ms)

                    with parallel:
                        self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)
                        self.Pixelfly.pulse(3*ms)
                        self.Andor.pulse(3*ms)
                        
                    delay(self.Detection_Pulse*ms)
                    self.BMOT_TTL.off()

                    if self.Compression==0 and self.Single_Freq_ON==0:
                        if j==int64(self.Cycle)-1:
                            print("Broadband RMOT detected with MOT beam as probe!!")
                    if self.Compression==1 and self.Single_Freq_ON==0:
                        if j==int64(self.Cycle)-1:
                            print("Compressed RMOT detected with MOT beam as probe!!")
                    if self.Compression==1 and self.Single_Freq_ON==1:
                        if j==int64(self.Cycle)-1:
                            print("Single Freq RMOT detected with MOT beam as probe!!")

                # **************************** Slice 6: Detection - Seperate Probe**************************
                elif self.RMOT_Probe_ON==1:
                    self.RMOT_TTL.off()
                    delay(3.5*ms)

                    self.MOT_Coil_1.write_dac(0, self.Detection_Coil1_Voltage)
                    self.MOT_Coil_2.write_dac(1, self.Detection_Coil2_Voltage)

                    with parallel:
                        self.MOT_Coil_1.load()
                        self.MOT_Coil_2.load()

                    delay(self.Time_of_Flight*ms)
                    

                    with parallel:
                        self.Andor.on()
                        self.Pixelfly.on()
                        self.Probe.set(frequency= 65 * MHz, amplitude=0.17)
                    
                    delay(self.Detection_Pulse*ms)
                    
                    with parallel:
                        self.Pixelfly.off()
                        self.Andor.off()
                    
                    self.Probe.set(frequency= 65 * MHz, amplitude=0.00)
                    self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.07)

                    if self.Compression==0 and self.Single_Freq_ON==0:
                        if j==int64(self.Cycle)-1:
                            print("Broadband RMOT detected with seperate probe beam!!")
                    if self.Compression==1 and self.Single_Freq_ON==0:
                        if j==int64(self.Cycle)-1:
                            print("Compressed RMOT detected with seperate probe beam!!")
                    if self.Compression==1 and self.Single_Freq_ON==1:
                        if j==int64(self.Cycle)-1:
                            print("Single Freq RMOT detected with seperate probe beam!!")
                
                else:
                    logging.error("Select either, 0: MOT as Probe 1: Seperate Probe")
                    sys.exit(1)
            
            else:
                logging.error("Select either 0 or 1 for RedMOT_ON")
                sys.exit(0)

            # **************************** Headroom ****************************
            delay(500*ms)