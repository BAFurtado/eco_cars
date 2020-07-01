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
        self.firms = dict()
        self.current_data = dict()

    def create_agents(self):
        pass

    def controller(self):
        while self.running:
            self.run()
            self.t += 1
            if self.t == params.t_f:
                self.running = False

    def info(self):
        # Calculate green_share of firms
        green_share = sum([1 for firm in self.firms.values() if firm.portfolio == 'green']) / len(self.firms)
        epsilon = 1 if green_share > 0 else 0
        self.current_data['green_share'] = green_share
        self.current_data['epsilon'] = epsilon

    def run(self):
        """
        Demand:
        1. Consumers decided whether to buy
        2. Consumers check cars availability
        3. Consumers select, given constraints
        4. Criteria
        5. Choose car

        """

