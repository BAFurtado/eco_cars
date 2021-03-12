import random
from collections import defaultdict

import pandas as pd
import numpy as np
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
    def __init__(self, policy=None, verbose=False, seed=True):
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
        # Benchmark e policy parameter: average emission sold vehicles
        self.e = 1
        # When e_max policy is not being tested, all cars will pass
        self.e_max = 99
        self.policy = policy
        self.ids = 0
        self.running = True
        self.firms = dict()
        self.new_firms = list()
        self.consumers = dict()
        self.create_agents()
        self.green_market_share = dict()
        self.green_stations = dict()
        self.num_cars = {'green': defaultdict(int),
                         'hybrid': defaultdict(int),
                         'gas': defaultdict(int)}
        self.emissions = 0
        # 'emissions' is total value, 'emissions_index' is relative to first month emissions
        # 'e' is the calculated parameter benchmark, based on sold vehicles and their energy economy
        self.report = pd.DataFrame(columns=['green_market_share', 'hybrid_market_share', 'new_firms_share',
                                            'emissions', 'emissions_index', 'e',
                                            'public', 'public_index', 'public_cumulative'])

    def create_agents(self):
        for key in params.regions_firms:
            for i in range(params.regions_firms[key]):
                self.firms[self.ids] = Firm(self.ids, key, self)
                self.ids += 1
        regions = self.seed.choices(population=list(params.regions_consumers.keys()),
                                    k=params.num_consumers, weights=params.regions_consumers.values())
        for j in range(params.num_consumers):
            self.consumers[self.ids] = Consumer(self.ids, regions[j], self)
            self.ids += 1
        self.log.info(params.cor.Fore.MAGENTA + f"We have created {len(self.firms)} firms "
                                                f"and {len(self.consumers)} agents, being "
                                                f"{len([c for c in self.consumers.values() if c.region == 'se'])} "
                                                f"of them from SE")

    def controller(self):
        while self.running:
            self.run()
            self.t += 1
            if self.t == params.T:
                self.running = False
                break
            if self.sleep:
                sleep = 1
                time.sleep(sleep)
                self.log.info(params.cor.Fore.MAGENTA + f'Time: {self.t} -- deliberate pausing for {sleep} seconds')
        print(params.cor.Fore.RED + f"Total emissions for this run was {sum(self.report['emissions']):,.2f}")

    def update_car_info(self, car_type):
        self.num_cars[car_type][self.t] += 1

    def new_firm(self, busted):
        # 1. Pick an existing firm, proportional to market share
        weights = [f.market_share['total'][self.t] for f in self.firms.values()]
        key = self.seed.choices(list(self.firms.values()), weights=weights)
        while True:
            # Making sure firm to imitate has not just gone busted
            try:
                i = 0
                if self.firms[key[i].id] not in busted:
                    firm_to_imitate = self.firms[key[i].id]
                    break
                else:
                    i += 1
            except IndexError:
                # In the case that there are no firms to imitate that have not gone busted
                firm_to_imitate = self.firms[key[0].id]
                break
        # 2. if original company has both technologies, just 1/3 chance both are going to be replicated
        choice = self.seed.random()
        if len(firm_to_imitate.cars) == 3:
            # 1/6 chance of copying both technologies
            if choice < 1/6:
                techs = ['gas', 'green', 'hybrid']
            elif choice < 1/2:
                techs = self.seed.sample(firm_to_imitate.cars.keys(), k=2)
            else:
                techs = [self.seed.choice(list(firm_to_imitate.cars.keys()))]
        else:
            techs = firm_to_imitate.cars.keys()
        # Create new firm, without a car at first, then follow decision on techs
        # Budget is random
        new_firm = Firm(self.ids, firm_to_imitate.region, self, gas=False)
        self.log.info(f'New firm {new_firm.id} created')
        self.new_firms.append(new_firm.id)
        self.ids += 1
        # Add portfolio
        for i in techs:
            # Choose random values between initial values and current values of the company to imitate
            pc, ec, ee = (self.seed.uniform(params.production_cost[i], firm_to_imitate.cars[i].production_cost),
                          self.seed.uniform(params.energy_capacity[i], firm_to_imitate.cars[i].EC),
                          self.seed.uniform(params.energy_economy[i], firm_to_imitate.cars[i].EE))
            new_firm.cars[i] = Vehicle(firm=new_firm, _type=i, production_cost=pc, ec=ec, ee=ee)
            new_firm.portfolio_marker = self.t

    def update_green_market_and_stations(self):
        # Update green market share
        if self.t < 9:
            self.green_market_share[self.t] = 0
            self.green_stations[self.t] = 1
        else:
            green_cars = self.num_cars['green'][self.t - 1]
            total_cars = self.num_cars['gas'][self.t - 1] + self.num_cars['green'][self.t - 1] \
                                                          + self.num_cars['hybrid'][self.t - 1]
            # One more place in which sold cars are 0
            self.green_market_share[self.t] = green_cars / total_cars if total_cars > 0 else 0
            # Update green stations
            self.green_stations[self.t] = 1 + max(self.green_market_share.values())
        self.report.loc[self.t, 'green_market_share'] = self.green_market_share[self.t]

    def apply_policies(self):
        # e (e_benchmark) is the average emission of vehicles sold in the previous period
        # Calculate e
        if self.t > 0:
            cars_emission = [car.emissions() for firm in self.firms.values() for car in firm.cars.values()]
            sold = [sold[self.t - 1] for firm in self.firms.values() for sold in firm.sold_cars.values()]
            # Notice, sometimes no cars are sold (market conditions or policies are too restrict)
            sold_cars_emissions = sum([c * sd for c, sd in zip(cars_emission, sold)])/sum(sold) if sum(sold) > 0 else 0
            self.e = sold_cars_emissions
            self.report.loc[self.t, 'e'] = self.e
            self.log.info(f'Parameter e -- sold cars emission average -- is {sold_cars_emissions:.4f}')
            if self.policy['policy'] == 'e_max':
                self.e_max = self.e * (1 + self.seed.uniform(0, params.e_max[self.policy['level']]))
                self.log.info(f'Max emission for time {self.t} is {self.e_max:.2f}')
            # When updating car prices, if policy is in effect, DISCOUNTS AND TAXES are summed and returned
            public_expenditure = defaultdict(float)
            for r in ['se', 's', 'ne', 'n', 'co']:
                for firm in self.firms.values():
                    if firm.region == r:
                        for car in firm.cars.values():
                            temp_debt = sum([car.calculate_price() * firm.sold_cars[car.type][self.t - 1]])
                            # Checking criteria to enter policy tax deduction when in effect.
                            if (car.type == 'green' or car.type == 'hybrid') and self.policy['policy'] == 'p_d':
                                # Deducing up to 12.5% of the investment made by the firm on that car
                                max_possible_deduction = firm.investments[car.type][self.t - 1] * self.policy['level']
                                cashback = min(temp_debt, max_possible_deduction)
                                public_expenditure[r] += temp_debt - cashback
                                firm.budget += cashback
                            else:
                                public_expenditure[r] += temp_debt
                # Registering all public investment on the region
                self.report.loc[self.t, 'public' + '_' + r] = public_expenditure[r]
            # All regions together
            self.report.loc[self.t, 'public'] = sum(public_expenditure.values())
            base = [b for b in self.report.public if (not np.isnan(b)) and (b != 0)]
            self.report.loc[self.t, 'public_cumulative'] = sum(base)
            if not base:
                self.report.loc[self.t, 'public_index'] = 0
            else:
                self.report.loc[self.t, 'public_index'] = sum(public_expenditure.values()) / base[0]
            self.log.info(params.cor.Fore.RED + f"Government has paid/received total at this t {self.t} "
                                                f"a net total of $ {sum(public_expenditure.values()):,.2f}")

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
        self.update_green_market_and_stations()
        landfill = list()
        # Randomize order of firms at each turn
        keys = list(self.firms)
        self.seed.shuffle(keys)

        total_cars_sold = sum([self.num_cars[tech][self.t - 1] for tech in ['gas', 'green', 'hybrid']])
        for key in keys:
            self.firms[key].update_profit()
            self.firms[key].update_market_share(total_cars_sold)
            self.firms[key].update_budget()
            if self.firms[key].bankrupt():
                landfill.append(key)
                # If bankrupt, go to the next firm
                continue
            if self.t > 9:
                # If portfolio is changed, costs of adoption apply
                self.firms[key].change_portfolio()
                self.firms[key].abandon_portfolio()
            self.firms[key].invest_rd()

        # New firms market share
        self.report.loc[self.t, 'new_firms_share'] = sum([f.market_share['total'][self.t]
                                                          for f in self.firms.values()
                                                          if f.id in self.new_firms])

        if landfill:
            print(params.cor.Fore.LIGHTMAGENTA_EX + f'Firms {[i for i in landfill]} '
                                                    f'has(ve) gone bankrupt at time {self.t}')
        for i in landfill:
            self.new_firm(landfill)
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
        if self.t > 2:
            self.report.loc[self.t, 'emissions_index'] = self.emissions / self.report.loc[3, 'emissions']
        self.log.info(params.cor.Fore.RED + f"Emissions at t {self.t} was {self.emissions:,.2f}. "
                                            f"Emissions index: {self.report.loc[self.t, 'emissions_index']:.4f}")
        self.emissions = 0


def main(policy, verbose=False, seed=True):
    my_sim = Simulation(policy, verbose, seed)
    my_sim.controller()
    return my_sim


if __name__ == '__main__':
    level = 1.0
    # Three policies may be applied
    # Pol = NONE is baseline, no policy example
    # 1. Reduction of IPI: 'tax'
    # 2. Cashback on P&D investment: 'p_d'
    # 3. Ruling on max emissions: 'e_max'
    pols = [None, 'tax', 'p_d', 'e_max']
    # pols = pols[0]
    pol = pols[1]
    p = {'policy': pol, 'level': level}
    s = main(p, verbose=False)
