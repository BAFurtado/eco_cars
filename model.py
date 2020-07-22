import random
from collections import defaultdict

import pandas as pd
import logging
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
    def __init__(self, verbose=False, seed=False):
        self.log = logging.getLogger('main')
        if verbose:
            logging.basicConfig(level=logging.INFO)
            self.sleep = True
        else:
            self.log.setLevel(30)
            self.sleep = False
        if not seed:
            self.seed = random.Random()
        else:
            self.seed = random.Random(0)
        self.t = 0
        self.ids = 0
        self.running = True
        self.firms = dict()
        self.consumers = dict()
        self.create_agents()
        self.green_market_share = dict()
        self.green_stations = dict()
        self.num_cars = {'green': defaultdict(int), 'gas': defaultdict(int)}
        self.emissions = 0
        self.report = pd.DataFrame(columns=['green_market_share', 'new_firm', 'emissions', 'emissions_index'])

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
            if self.t == params.T:
                self.running = False
                break
            if self.sleep:
                sleep = 5
                time.sleep(sleep)
                self.log.info(params.cor.Fore.MAGENTA + f'Time: {self.t} -- deliberate pausing for {sleep} seconds')
        print(params.cor.Fore.RED + f"Total emissions for this run was {sum(self.report['emissions']):,.2f}")

    def update_car_info(self, car_type):
        self.num_cars[car_type][self.t] += 1

    def new_firm(self):
        # 1. Pick an existing firm, proportional to market share
        weights = [f.market_share['total'][self.t] for f in self.firms.values()]
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
        self.log.info(f'New firm {new_firm.id} created')
        self.report.loc[self.t, 'new_firm'] += 1
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

    def update_green_stations(self):
        # Update green market share
        if self.t < 9:
            self.green_market_share[self.t] = 0
            self.green_stations[self.t] = 1
        else:
            green_cars = sum([firm.sold_cars['green'][self.t - 1]
                              for firm in self.firms.values() if 'green' in firm.cars])
            total_cars = self.num_cars['gas'][self.t - 1] + self.num_cars['green'][self.t - 1]
            self.green_market_share[self.t] = green_cars/total_cars
            # Update green stations
            self.green_stations[self.t] = 1 + max(self.green_market_share.values())
        self.report.loc[self.t, 'green_market_share'] = self.green_market_share[self.t]

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
        self.update_green_stations()
        landfill = list()
        # Randomize order of firms at each turn
        keys = list(self.firms)
        self.seed.shuffle(keys)

        for key in keys:
            self.firms[key].update_profit()
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

        if landfill:
            print(params.cor.Fore.LIGHTMAGENTA_EX + f'Firms {[i for i in landfill]} '
                                                    f'has(ve) gone bankrupt at time {self.t}')
        for i in landfill:
            self.new_firm()
            del self.firms[i]

    def demand(self):
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
        self.log.info(params.cor.Fore.RED + f"Emissions at t {self.t} was {self.emissions:,.2f}. "
                                            f"Emissions index: {self.report.loc[self.t, 'emissions_index']:.4f}")
        self.emissions = 0


def main(verbose=False):
    my_sim = Simulation(verbose=verbose)
    my_sim.controller()
    return my_sim


if __name__ == '__main__':
    v = False
    s = main(v)
