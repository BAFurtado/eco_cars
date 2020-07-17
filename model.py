import random
import params
from firms import Firm
from consumers import Consumer
from collections import defaultdict

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
        self.running = True
        self.firms = dict()
        self.consumers = dict()
        self.current_data = dict()
        self.create_agents()
        self.num_cars = defaultdict(int)
        self.emissions = 0
        self.total_sales = defaultdict(float)

    def create_agents(self):
        for i in range(params.num_firms):
            self.firms[i] = Firm(i, self)
        for j in range(params.num_consumers):
            self.consumers[i + j + 1] = Consumer(i + j + 1, self)

    def controller(self):
        while self.running:
            self.run()
            self.t += 1
            if self.t == params.T:
                self.running = False
        print(f'Emissions for this run was {self.emissions:,.2f}')

    def update_current_data(self):
        # TODO: Probably, it will be here that global characteristics of the market are calculated
        # Calculate green_share of firms
        green_share = sum([1 for firm in self.firms.values() if firm.portfolio == 'green']) / len(self.firms)
        epsilon = .1 if green_share > 0 else 0
        self.current_data['green_share'] = green_share
        self.current_data['epsilon'] = epsilon
        # Market share
        # TODO: Check. Market share is based on sales
        total = sum([])

    def update_car_info(self, car):
        self.num_cars.get(car.type, 0) + 1

    def new_firm(self):
        # 1. Pick an existing firm, proportional to market share
        key = self.seed.choices()
        # 2. if original company has both technologies, just 1/3 chance both are going to be replicated
        # Choose random values between initial values and current values of the company to imitate
        # Budget is random
        pass

    def apply_policies(self):
        # TODO: Check item 3.5
        pass

    def run(self):
        """
        Offer:
        1. Calculate profit
        2. Calculate new budget. If bankrupt, create new firm
        3. Check for new portfolio
        4. Investments
        Demand:
        1. Consumers decided whether to buy
        2. Consumers check cars availability
        3. Consumers select, given constraints
        4. Criteria
        5. Choose car
        6. Update market share
        """

        self.offer()
        self.demand()
        self.driving()

    def offer(self):
        landfill = list()
        # Randomize order of firms at each turn
        keys = list(self.firms)
        self.seed.shuffle(keys)

        self.total_sales = defaultdict(float)
        for key in keys:
            self.total_sales[key] += self.firms[key].update_profit()

        for key in keys:
            self.firms[key].update_market_share(sum(self.total_sales.values()))
            self.firms[key].update_budget()
            if self.firms[key].bankrupt():
                landfill.append(key)
                continue
            if self.t > 9:
                # If portfolio is changed, costs of adoption apply
                self.firms[key].change_portfolio()
            self.firms[key].abandon_portfolio()
            self.firms[key].invest_rd()

        # TODO: currently all firms going bankrupt. Implement investments. Consumers not buying any cars because Dk?
        # for i in landfill:
        #     print(f'Firm {i} has gone bankrupt')
        #     del self.firms[i]
        #     self.new_firm()

    def demand(self):
        # Randomize order of firms at each turn
        keys = list(self.consumers)
        self.seed.shuffle(keys)
        for key in keys:
            self.consumers[key].purchase(self)
        self.update_current_data()

    def driving(self):
        for each in self.consumers.values():
            self.emissions += each.driving()


def main():
    my_sim = Simulation()
    my_sim.controller()
    return my_sim


if __name__ == '__main__':
    s = main()
