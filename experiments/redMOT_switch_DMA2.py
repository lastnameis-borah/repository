from artiq.experiment import *
from numpy import *
from artiq.coredevice.core import Core

class redMOT_switch_DMA2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.ad9912_0 = self.get_device("urukul0_ch0")

        self.setattr_argument("High_Frequency", NumberValue())
        self.setattr_argument("Low_Frequency", NumberValue())
        self.setattr_argument("Mid_Frequency", NumberValue())
        self.setattr_argument("Detuned_Frequency", NumberValue())

    @kernel
    def record(self):
        with self.core_dma.record("sweep"):

            # Set attenuation
            self.ad9912_0.set_att(10.0)
            
            # Set the parameters for modulation 1
            steps = 20.0                # Steps for ramp
            ramp_time = 0.02            # Time for total ramp in ms   # 225kHz = 0.1ms
            t = ramp_time/(steps)       # Time between each step
            freq_steps = (self.High_Frequency - self.Low_Frequency)/steps            # Frequency rise in each step

            # Sweep
            for i in range(1000):
                freq = self.Low_Frequency

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
            freq_steps = (self.Detuned_Frequency - self.Low_Frequency)/steps        # Frequency change in each step
            freq1 = self.Low_Frequency + freq_steps
            # att = 20 + att_steps
            # att_steps = (31.9-20)/steps         # Attenuation increase in each step
            # t = 100*ms

            # Modulation_

            if self.Detuned_Frequency == self.High_Frequency:
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

            if self.Detuned_Frequency == self.Low_Frequency:
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

        # Initialize Urukul AD9910
        self.ad9912_0.cpld.init()
        self.ad9912_0.init()

        # switch the channel ON
        self.ad9912_0.sw.on()

        # Initialize the DMA
        self.record()

        sweep = self.core_dma.get_handle("sweep")
        mod = self.core_dma.get_handle("mod")

        self.core.break_realtime()

        for i in range(15):
            self.core_dma.playback_handle(sweep)
        
        for i in range(1):
            self.core_dma.playback_handle(mod)

        # self.ad9912_0.sw.off()

        print("DMA test is done")