from artiq.experiment import *
from artiq.coredevice.ad9910 import _AD9910_REG_CFR2
from artiq.coredevice.ad9910 import _AD9910_REG_RAMP_LIMIT
from artiq.coredevice.ad9910 import _AD9910_REG_RAMP_RATE
from artiq.coredevice.ad9910 import _AD9910_REG_STEP
from numpy import int64


class AD9910Ramper(EnvEnvironment):
    def build(self):
        self.setattr_device("core")
        self.ad9910_ch3 = self.get_device("urukul1_ch3")
        self.ad9910_ch3.init()
