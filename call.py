from artiq.experiment import *
from repository.print import printing

class call(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.print:printing
        
    
    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
        
        self.print.run()