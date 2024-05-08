from artiq.experiment import *
from artiq.coredevice.ttl import TTLOut

class FreqModulationAD9912(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ad9910_0:TTLOut=self.get_device("urukul0_ch0")

        # self.setattr_argument("Number_of_pulse", NumberValue()) 
        # self.setattr_argument("Pulse_width", NumberValue()) 
        # self.setattr_argument("Time_between_pulse", NumberValue())

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.ad9910_0.cpld.init()
        self.ad9910_0.init()

        self.ad9910_0.set_att(0.0)     #limit  : 31.9



        self.ad9910_0.sw.on()

        # for i in range(10):

        #     freq = i + (10 * MHz)
        
        #     self.ad9910_0.set(frequency=freq, amplitude=1.0)

        #     delay(10*ms)

        

        # self.ad9910_0.set(frequency=10 * MHz, amplitude=1.0)

        # delay(1000*ms)

        # self.ad9910_0.set(frequency=15 * MHz, amplitude=1.0)

        # delay(1000*ms)

        delay(100000*ms)


        steps = 1000
        frequency_start = 0.000001 * MHz
        frequency_end = 0.000002 * MHz
        ramp_time = 1000
        
        t = ramp_time/(steps-1)
        freq_steps = (frequency_end - frequency_start)/steps

        # Modulation

        freq = frequency_start

        for i in range(steps + 1):
            self.ad9910_0.set(frequency=freq)
            delay(t*ms)
            print(freq)
            freq += freq_steps

        self.ad9910_0.sw.off()


        print("Frequency modulation test is complete")