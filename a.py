voltage = 0.52
steps = 20
t = 20/steps
change = (1.95 - voltage)/steps
for i in range(steps):
    voltage = voltage + change
    print(voltage)