voltage = 3.45
voltage_com = 2.75
steps_com = 8
t_com = 8/steps_com
change = (voltage - voltage_com)/steps_com

for i in range(steps_com):
    voltage = voltage - change
    self.MOT_Coils.write_dac(0, voltage_com)
    self.MOT_Coils.load()
    delay(t_com*ms)