from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64
# from repository.regression1 import Gate_Voltage

class Abhi_redMOT_Transfer_time(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.Camera:TTLOut=self.get_device("ttl10")
        self.BMOT_TTL:TTLOut=self.get_device("ttl6")
        self.RMOT_TTL:TTLOut=self.get_device("ttl8")
        self.Broadband_On:TTLOut=self.get_device("ttl5")
        self.Broadband_Off:TTLOut=self.get_device("ttl7")
        self.BMOT_AOM = self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.Single_Freq=self.get_device("urukul1_ch3")
        self.MOT_Coils=self.get_device("zotino0")

        self.setattr_argument("Cycle", NumberValue(default=1))
        self.setattr_argument("Loading_Time", NumberValue(default=550))
        self.setattr_argument("Transfer_Time", NumberValue(default=20))
        self.setattr_argument("Holding_Time", NumberValue(default=20))

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
        self.Single_Freq.cpld.init()
        self.Single_Freq.init()

        # Set the channel ON
        self.BMOT_AOM.sw.on()
        self.ZeemanSlower.sw.on()

        self.BMOT_AOM.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)
        self.Single_Freq.set_att(0.0)
        self.Single_Freq.set(frequency= 80 * MHz, amplitude=1.0)

        delay(1000*ms)
        self.core.break_realtime()

        for i in range(int64(self.Cycle)):
            # Slice 1
            # with parallel:
                # BMOT
            self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.09)

                # Zeeman Slower
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

            with parallel:
                # Magnetic field (3.0v)
                with sequential:
                    voltage = 0.52
                    self.MOT_Coils.write_dac(0, voltage)
                    self.MOT_Coils.load()
                
                # Start the modulation of red
                self.RMOT_TTL.on()
                self.BMOT_TTL.on()

            # Slice 1 duration
            delay(self.Loading_Time*ms)

            # Slice 2: Transfer

            # with parallel:
                # Magnetic field (2.2A)
                # with sequential:
            # print(f"{Gate_Voltage(2.1)[0][0]:.2f}")
            # voltage = 0.52
            # self.MOT_Coils.write_dac(0, voltage)
            # #1.23=2.7A, 1.55=2.4A, 1.95=2.1A, 2.0=2.0A, 2.26=1.8A, 2.42=1.6A, 2.55=1.5A, 2.85=1.2A, 3.05=1.0A, 3.18=0.9A, 3.36=0.7A, 3.5=0.6A
            # self.MOT_Coils.load()

                # Zeeman Slower
                # with sequential:
            # self.ZeemanSlower.set_att(31.9)
            self.ZeemanSlower.set(frequency=180*MHz, amplitude=0.0)

            # BMOT
            with parallel:
                with sequential:
                    steps = self.Transfer_Time
                    t = self.Transfer_Time/steps
                    for i in range(int64(steps + 1.0)):
                        amp_steps = 0.09/steps
                        amp = 0.09 - (i * amp_steps)
                        self.BMOT_AOM.set(frequency=90*MHz, amplitude=amp)
                        delay(t*ms)

                with sequential:
                    steps = self.Transfer_Time
                    t = self.Transfer_Time/steps
                    change = ((3.36 - voltage)/steps)
                    for i in range(int64(steps)):
                        voltage = voltage + change
                        self.MOT_Coils.write_dac(0, voltage)
                        self.MOT_Coils.load()
                        delay(t*ms)
                        # print(voltage)

            self.BMOT_TTL.off()

            # Slice 3
            delay(self.Holding_Time*ms)

            # Slice 4: Compentation for shutter delay
            self.RMOT_TTL.off()
            self.BMOT_TTL.on()
            delay(3*ms)

            # Slice 5: Detection
            with parallel:
                with sequential:
                    self.MOT_Coils.write_dac(0, 4.15)
                    self.MOT_Coils.load()   
                self.BMOT_AOM.set(frequency=90*MHz, amplitude=0.09)
                self.Camera.pulse(5*ms)

            delay(50*ms)

            # Slice 6
            self.ZeemanSlower.set_att(0.0)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)
            
            # Slice 6: Headroom for 2nd cycle
            delay(1000*ms)

        print("RedMOT exp complete!!")