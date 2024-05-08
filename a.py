steps = 20
t = 20/steps
for i in range(steps):
    amp_steps = 0.09/steps
    amp = 0.09 - ((i+1) * amp_steps)
    print(amp)