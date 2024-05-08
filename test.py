from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut
from numpy import int64

class testtttttt(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.camera:TTLOut=self.get_device("ttl8")
        self.red:TTLOut=self.get_device("ttl6")
        self.MOT_Coils=self.get_device("zotino0")
        self.BMOT=self.get_device("urukul1_ch0")
        self.ZeemanSlower=self.get_device("urukul1_ch1")
        self.ad9912_0 = self.get_device("urukul0_ch0")

        self.setattr_argument("Cycle", NumberValue(default = 1))
        self.setattr_argument("Modulating_Frequency", NumberValue(default = 25, unit = "kHz"))
        self.setattr_argument("Max_Frequency", NumberValue(default = 81, unit = "MHz"))
        self.setattr_argument("Min_Frequency", NumberValue(default = 79, unit = "MHz"))
        # self.setattr_argument("Mid_Frequency", NumberValue(default = 80, unit = "MHz"))
        self.setattr_argument("Detuned_Frequency", NumberValue(default = 81, unit = "MHz"))

    @kernel
    def record(self):
        with self.core_dma.record("sweep"):

            # Set attenuation
            self.ad9912_0.set_att(10.0)
            
            # Set the parameters for modulation 1
            steps = 20.0                # Steps for ramp
            ramp_time = (1/self.Modulating_Frequency) / 2     # Time for total ramp in ms   # 25kHz = 0.04ms
            t = ramp_time/(steps)       # Time between each step
            freq_steps = (self.Max_Frequency - self.Min_Frequency)/steps            # Frequency rise in each step

            # Sweep
            for i in range(1500):
                freq = self.Min_Frequency

                for i in range(int64(steps + 1.0)):
                    self.ad9912_0.set(frequency=freq * MHz)
                    delay(t*ms)
                    freq += freq_steps
                # print(freq - freq_steps)
        
                freq0 = freq - freq_steps
                
                for i in range(int64(steps + 1.0)):
                    self.ad9912_0.set(frequency=freq0 * MHz)
                    delay(t*ms)
                    freq0 -= freq_steps
                # print(freq0 + freq_steps)

        with self.core_dma.record("mod"):
            # Set the parameters for modulation 2
            steps = 200.0
            freq_steps = (self.Detuned_Frequency - self.Min_Frequency)/steps        # Frequency change in each step
            freq1 = self.Min_Frequency + freq_steps
            # att = 20 + att_steps
            # att_steps = (31.9-20)/steps         # Attenuation increase in each step
            # t = 100*ms

            # Modulation_

            if self.Detuned_Frequency == self.Max_Frequency:
                for i in range(int64(steps - 1.0)):
                    for j in range(int64(steps - i)):
                        # self.ad9912_0.set_att(att)
                        self.ad9912_0.set(frequency=freq1 * MHz)
                        delay(t*ms)
                        freq1 += freq_steps
                        # att += att_steps
                    freq10 = freq1 - freq_steps
                    # print(freq10)
                    # print(att - att_steps)

                    for j in range(int64((steps - 1.0) - i)):
                        # self.ad9912_0.set_att(att)
                        self.ad9912_0.set(frequency=freq10 * MHz)
                        delay(t*ms)
                        freq10 -= freq_steps
                        # att += att_steps
                    freq1 = freq10 + freq_steps
                    # print(freq1)
                    # print(att - att_steps)

            if self.Detuned_Frequency == self.Min_Frequency:
                for i in range(int64(steps - 1.0)):
                    for j in range(int64((steps - 1.0) - i)):
                        # self.ad9912_0.set_att(att)
                        self.ad9912_0.set(frequency=freq1 * MHz)
                        delay(t*ms)
                        freq1 += freq_steps
                        # att += att_steps
                    freq10 = freq1 - freq_steps
                    print(freq10)
                    # print(att - att_steps)

                    for j in range(int64(steps - i)):
                        # self.ad9912_0.set_att(att)
                        self.ad9912_0.set(frequency=freq10 * MHz)
                        delay(t*ms)
                        freq10 -= freq_steps
                        # att += att_steps
                    freq1 = freq10 + freq_steps
                    print(freq1)
                    # print(att - att_steps)

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        # Initialize the modules
        self.camera.output()
        self.red.output()
        self.MOT_Coils.init()
        self.BMOT.cpld.init()
        self.BMOT.init()
        self.ad9912_0.cpld.init()
        self.ad9912_0.init()
        self.ZeemanSlower.cpld.init()
        self.ZeemanSlower.init()
        

        # Set the channel ON
        self.BMOT.sw.on()
        self.ad9912_0.sw.on()
        self.ZeemanSlower.sw.on()

        self.BMOT.set_att(0.0)
        self.ZeemanSlower.set_att(0.0)

        # Initialize the DMA
        self.record()

        sweep = self.core_dma.get_handle("sweep")
        mod = self.core_dma.get_handle("mod")

        delay(4e-3)

        self.core.break_realtime()

        for i in range(int64(self.Cycle)):
            # Slice 1
            # with parallel:
                # BMOT
            self.BMOT.set(frequency=90*MHz, amplitude=0.09)

                # Zeeman Slower
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.35)

            with parallel:
                # Magnetic field (3.5v)
                with sequential:
                    self.MOT_Coils.write_dac(0, 0.52)
                    self.MOT_Coils.load()
                    
                    # Start the modulation of red
                self.red.on()

                for i in range(7):
                    self.core_dma.playback_handle(sweep)

            # Slice 1 duration
            # delay(550*ms)

            # Slice 2: Transfer

            # with parallel:
                # Magnetic field (2.2A)
                # with sequential:
            self.MOT_Coils.write_dac(0, 0.52) #3.04
            self.MOT_Coils.load()

                # Zeeman Slower
                # with sequential:
            # self.ZeemanSlower.set_att(31.9)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.0)

            # BMOT
            # with sequential:
            steps = 20.0
            t = 20/steps
            for i in range(int64(steps + 1.0)):
                amp_steps = 0.09/steps
                amp = 0.09 - (i * amp_steps)
                self.BMOT.set(frequency=90*MHz, amplitude=amp)
                delay(t*ms)


            # Slice 3
            delay(20*ms)

            # Slice 4: Compentation for shutter delay
            self.red.off()
            delay(3*ms)

            # Slice 5: Detection
            with parallel:
                self.BMOT.set(frequency=90*MHz, amplitude=0.09)
                self.camera.pulse(5*ms)

            delay(50*ms)

            # Slice 6
            self.ZeemanSlower.set_att(0.0)
            self.ZeemanSlower.set(frequency=180 * MHz, amplitude=0.00)
            
            # Slice 6: Headroom for 2nd cycle
            delay(1000*ms)

        print("RedMOT exp complete!!")