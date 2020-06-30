import random
import params

# Sequence
"""
1. Offer of firms
2. Policy
3. Consumers purchase
4. Use of cars => results of CO2 emission and Public Finance
"""


class Simulation:
    def __init__(self):
        self.seed = random.Random(0)
        self.t = 0
        self.running = False

    def controller(self):
        while self.running:
            self.run()
            self.t += 1
            if self.t == params.t_f:
                self.running = False

    def run(self):
        pass

