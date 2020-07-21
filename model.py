import random
from collections import defaultdict

import pandas as pd
import time
import params
from cars import Vehicle
from consumers import Consumer
from firms import Firm

# Sequence
"""
1. Offer of firms
2. Policy
3. Consumers purchase
4. Use of cars => results of CO2 emission and Public Finance
"""


class Simulation:
    def __init__(self):
        self.seed = random.Random()
        self.t = 0
        self.ids = 0
        self.running = True
        self.firms = dict()
        self.consumers = dict()
        self.current_data = dict()
        self.create_agents()
        self.num_cars = {'green': defaultdict(int), 'gas': defaultdict(int)}
        self.emissions = 0
        self.total_sales = {'green': defaultdict(float), 'gas': defaultdict(float)}
        self.report = pd.DataFrame(columns=['t', 'green_market_share', 'new_firm', 'emissions', 'emissions_index'])

    def create_agents(self):
        for i in range(params.num_firms):
            self.firms[self.ids] = Firm(self.ids, self)
            self.ids += 1
        for j in range(params.num_consumers):
            self.consumers[self.ids] = Consumer(self.ids, self)
            self.ids += 1

    def controller(self):
        while self.running:
            self.run()
            self.t += 1
            # time.sleep(3)
            # print(params.cor.Fore.MAGENTA + f'Time: {self.t} -- deliberate pausing for 3 seconds')
            if self.t == params.T:
                self.running = False
        print(params.cor.Fore.RED + f"Total emissions for this run was {sum(self.report['emissions']):,.2f}")

    def update_current_data(self):
        # Calculate green_share of firms
        green_share = sum([1 for firm in self.firms.values() if firm.portfolio == 'green']) / len(self.firms)
        epsilon = .1 if green_share >= 0 else 0
        self.current_data['green_share'] = green_share
        self.current_data['epsilon'] = epsilon

    def update_car_info(self, car):
        self.num_cars[car.type][self.t] += 1

    def new_firm(self):
        # 1. Pick an existing firm, proportional to market share
        weights = [f.current_market_share for f in self.firms.values()]
        key = self.seed.choices(list(self.firms.values()), weights=weights)
        firm_to_imitate = self.firms[key[0].id]
        # 2. if original company has both technologies, just 1/3 chance both are going to be replicated
        choice = self.seed.random()
        if len(firm_to_imitate.cars) == 2:
            # 1/3 chance of copying both technologies
            if choice < 1/3:
                techs = ['gas', 'green']
            elif choice < 2/3:
                techs = ['gas']
            else:
                techs = ['green']
        else:
            techs = list(firm_to_imitate.cars.keys())
        # Create new firm, without a car at first, then follow decision on techs
        # Budget is random
        new_firm = self.firms[self.ids] = Firm(self.ids, self, gas=False)
        self.ids += 1
        # Add portfolio
        for i in techs:
            # Choose random values between initial values and current values of the company to imitate
            pc, ec, ee = (self.seed.uniform(params.production_cost[i], firm_to_imitate.cars[i].production_cost),
                          self.seed.uniform(params.energy_capacity[i], firm_to_imitate.cars[i].EC),
                          self.seed.uniform(params.energy_economy[i], firm_to_imitate.cars[i].EE))
            new_firm.cars[i] = Vehicle(firm=new_firm, _type=i, production_cost=pc, ec=ec, ee=ee)
            if i == 'green':
                new_firm.green_adoption_marker = self.t

    def current_market_share(self):
        total_sales = self.total_sales['green'][self.t] + self.total_sales['gas'][self.t]
        for key in self.firms:
            self.firms[key].current_market_share = self.firms[key].profit['green'][self.t] + \
                                                   self.firms[key].profit['gas'][self.t] / total_sales

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
        self.apply_policies()
        self.demand()
        self.driving()

    def offer(self):
        landfill = list()
        # Randomize order of firms at each turn
        keys = list(self.firms)
        self.seed.shuffle(keys)

        # TODO: Check. Market share is based on sales
        for tech in ['gas', 'green']:
            for key in keys:
                if tech in self.firms[key].cars:
                    self.total_sales[tech][self.t] += self.firms[key].update_profit(tech)

        for key in keys:
            self.firms[key].update_market_share()
            self.firms[key].update_budget()
            if self.firms[key].bankrupt():
                landfill.append(key)
                continue
            if self.t > 9:
                # If portfolio is changed, costs of adoption apply
                self.firms[key].change_portfolio()
            self.firms[key].abandon_portfolio()
            self.firms[key].invest_rd()

        self.current_market_share()

        if landfill:
            print(params.cor.Fore.LIGHTMAGENTA_EX + f'Firms {[i for i in landfill]} '
                                                    f'has(ve) gone bankrupt at time {self.t}')
        for i in landfill:
            self.new_firm()
            del self.firms[i]

    def demand(self):
        self.update_current_data()
        # Randomize order of firms at each turn
        keys = list(self.consumers)
        self.seed.shuffle(keys)
        for key in keys:
            self.consumers[key].purchase(self)

    def driving(self):
        for each in self.consumers.values():
            self.emissions += each.driving()
        self.report.loc[self.t, 'emissions'] = self.emissions
        self.report.loc[self.t, 'emissions_index'] = self.emissions / self.report.loc[0, 'emissions']
        print(params.cor.Fore.RED + f"Emissions at t {self.t} was {self.emissions:,.2f}. "
                                    f"Emissions index: {self.report.loc[self.t, 'emissions_index']:.4f}")
        self.emissions = 0


def main():
    my_sim = Simulation()
    my_sim.controller()
    return my_sim


if __name__ == '__main__':
    s = main()
