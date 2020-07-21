from collections import defaultdict
from math import e

import params
from cars import Vehicle


class Firm:
    """ Produce and market vehicles
    """
    def __init__(self, _id, sim, gas=True):
        self.id = _id
        # Budget
        self.budget = sim.seed.randint(0, params.budget_max_limit)
        # Firm configuration decisions:
        self.portfolio = 'gas'
        self.profit = 0
        # Investments in R&D
        self.investments = defaultdict(int)
        self.sold_cars = defaultdict(int)
        # Assign a vehicle for this firm to sell
        self.cars = dict()
        self.market_share = 0
        self.sim = sim
        if gas:
            self.create_gas_car()
        self.green_adoption_marker = 0

    def create_gas_car(self):
        self.cars['gas'] = Vehicle(firm=self)

    def update_budget(self):
        # Investments are deduced immediately when done and retained cumulatively to calculate ROI
        self.budget += self.profit

    def update_market_share(self, total):
        self.market_share = self.profit / total

    def bankrupt(self):
        return True if self.budget < 0 else False

    def update_profit(self):
        # Sales income is accounted for at update profit, followed by update budget iteration
        for car in self.cars:
            self.profit += self.sold_cars[car] * self.cars[car].sales_price - params.fixed_costs
        return self.profit

    def change_portfolio(self):
        if len(self.cars) == 2:
            # Firm already has both portfolios
            return
        if 'green' in self.cars.keys():
            # Firms only move from gas to green
            return
        if self.budget > params.cost_adoption:
            # TODO: Check values are of current 'gas' technology: both for EE and production_cost
            prob_adoption = ((self.cars['gas'].EE / params.energy_economy['max']
                              + params.production_cost['min'] / self.cars['gas'].production_cost) / 2) ** params.omega \
                            * (self.sim.current_data['green_share'] + self.sim.current_data['epsilon']) ** \
                            (1 - params.omega)
            # print(params.cor.Fore.LIGHTRED_EX + f'Prob. adoption of green portfolio: {prob_adoption:.4f}')
            if prob_adoption > self.sim.seed.random():
                # Determine costs of adopting green technology
                # Choosing parameters of cost before calculating probability
                greens = [firm for firm in self.sim.firms.values() if firm.portfolio == 'green']
                imitation_parameters = None, None, None
                if not greens:
                    # Be the first firm
                    pc, ec, ql = (params.production_cost['green'], params.energy_capacity['green'],
                                  params.quality_level['green'])
                else:
                    # Choose company to imitate green technology, prob. proportional to firm size
                    firm_to_imitate = self.sim.seed.choices(greens, weights=lambda x: x.market_share)
                    car = firm_to_imitate.cars['green']
                    # New car production will fall somewhere between current Vehicle EC, QL, production_cost
                    pc, ec, ql = (self.sim.seed.uniform(self.cars['gas'].production_cost, car.production_cost),
                                  self.sim.seed.uniform(self.cars['gas'].energy_capacity, car.energy_capacity),
                                  self.sim.seed.uniform(self.cars['gas'].quality_level, car.quality_level))
                # Adopt Green
                print(params.cor.Fore.RED + f'Great news. Firm {self.id} has adopted a new green portfolio')
                self.budget -= params.cost_adoption
                self.cars['green'] = Vehicle(_type='green',
                                             production_cost=pc,
                                             ec=ec,
                                             ee=params.energy_economy['green'],
                                             ql=ql,
                                             firm=self)
                self.green_adoption_marker = self.sim.t

    def invest_rd(self):
        # 1. Check available money
        if self.budget <= 0:
            return
        # 2. Update self.investments
        # This random factor is characterized as mu in the model description
        mu = self.sim.seed.uniform(0, params.mu_max)
        investments = max(mu * self.budget, params.rd_min)
        # Actually invest into vehicle
        self.invest_into_vehicle(investments)

    def invest_into_vehicle(self, investments):
        # May improve PC (production_cost), EE, EC, QL
        # Choose which one randomly depending on current technology
        # 1. PC 2. EE or EC 3. QL
        choice = self.sim.seed.choice([1, 2, 3])
        for tech in self.cars.keys():
            rdm = self.sim.seed.random()
            # eta = 1 if just one car, 1/2 if gas and green
            to_invest_now = investments * 1 if len(self.investments) == 1 else investments * .5
            if rdm < 1 - e ** (-params.alpha1 * to_invest_now):
                # Success. Investment to occur!
                self.investments[tech] += to_invest_now
                self.budget -= to_invest_now
                print(params.cor.Fore.LIGHTCYAN_EX + f'Advertise material. We, at firm {self.id}, '
                                                     f'have made an investment on {tech} '
                                                     f'of {to_invest_now:,.2f}')

                # 'PC_min', 'EE_max', 'EC_max', 'QL_max'
                if choice == 1 and self.cars[tech].production_cost > params.production_cost['min']:
                    delta = params.alpha2 * rdm * (params.production_cost['min'] - self.cars[tech].production_cost)
                    self.cars[tech].production_cost += delta
                    print(params.cor.Fore.GREEN + f'Production cost reduced by {delta:,.2f}')
                elif choice == 3 and self.cars[tech].QL < params.quality_level['max']:
                    delta = params.alpha2 * rdm * (params.quality_level['max'] - self.cars[tech].QL)
                    self.cars[tech].QL += delta
                    print(params.cor.Fore.MAGENTA + f'Quality increased by {delta:,.2f}')
                else:
                    if tech == 'gas':
                        # EE
                        if self.cars[tech].EE < params.energy_economy['max']:
                            delta = params.alpha2 * rdm * (params.energy_economy['max'] - self.cars[tech].EE)
                            self.cars[tech].EE += delta
                            print(params.cor.Fore.LIGHTYELLOW_EX + f'Energy economy increased by {delta:,.2f}')
                    else:
                        # EC
                        if self.cars[tech].EC < params.energy_capacity['max']:
                            delta = params.alpha2 * rdm * (params.energy_capacity['max'] - self.cars[tech].EC)
                            self.cars[tech].EC += delta
                            print(params.cor.Fore.GREEN + f'Energy capacity increased by {delta:,.4f}')

    def sales(self, car):
        # Register number of sold_cars
        self.sold_cars[car] += 1

    def abandon_portfolio(self):
        if len(self.cars) == 1:
            return
        if self.sim.t - self.green_adoption_marker < 10:
            return
        for car in self.cars.values():
            roi = self.calculate_roi(car)
            if self.sim.seed.random() < roi:
                print(params.cor.Fore.LIGHTRED_EX + f'Abandoning a portfolio: firm {self.id}')
                del self.cars[car.type]
                return

    def calculate_roi(self, car):
        # ROI is dependent on each vehicle
        return params.p_lambda * car.production_cost * self.sold_cars[car.type] / self.investments[car.type]
