from collections import defaultdict
from math import e

from cars import Vehicle


class Firm:
    """ Produce and market vehicles
    """
    def __init__(self, _id, region, sim, gas=True):
        self.id = _id
        self.region = region
        # Budget
        self.sim = sim
        self.budget = sim.seed.randint(0, self.sim.params.budget_max_limit)
        # Firm configuration decisions:
        self.profit = {'gas': defaultdict(float),
                       'hybrid': defaultdict(float),
                       'green': defaultdict(float)}
        # Investments in R&D
        self.investments = {'gas': defaultdict(float),
                            'hybrid': defaultdict(float),
                            'green': defaultdict(float)}
        self.sold_cars = {'gas': defaultdict(int),
                          'hybrid': defaultdict(int),
                          'green': defaultdict(int)}
        # Assign a vehicle for this firm to sell
        self.cars = dict()
        self.market_share = {'gas': defaultdict(float),
                             'hybrid': defaultdict(float),
                             'green': defaultdict(float),
                             'total': defaultdict(float)}
        self.portfolio_marker = 0
        if gas:
            self.create_gas_car()

    def create_gas_car(self):
        self.cars['gas'] = Vehicle(firm=self)
        self.portfolio_marker = self.sim.t

    def update_budget(self):
        # Investments are deduced immediately when they occur, if they occcur
        # Here we add profits per car, deduce fixed costs
        # Cost of adoption are also deduced as/if they happen
        for tech in self.cars:
            self.budget += self.profit[tech][self.sim.t]
        self.budget -= self.sim.params.fixed_costs if self.sim.t != 0 else 0

    def update_profit(self):
        # Sales income is accounted for at update profit, followed by update budget iteration
        if self.sim.t == 0:
            self.profit['gas'][0] = 0
            return
        # Here we include in the profit per car the quantity sold * the net gain between sales price and production cost
        for tech in self.cars:
            # For each technology (gas, green), number of cars sold times sales price minus production cost
            self.profit[tech][self.sim.t] += self.sold_cars[tech][self.sim.t - 1] * \
                                             (self.cars[tech].sales_price - self.cars[tech].production_cost
                                              - self.cars[tech].owed_taxes)

    def update_market_share(self, total_cars_sold):
        if self.sim.t == 0:
            self.market_share['gas'][0] = 0
            self.market_share['total'][0] = 0
            return
        for tech in ['gas', 'hybrid', 'green']:
            if tech in self.cars and self.sim.num_cars[tech][self.sim.t - 1] > 0:
                self.market_share[tech][self.sim.t] = self.sold_cars[tech][self.sim.t - 1] / \
                                                      self.sim.num_cars[tech][self.sim.t - 1]
            else:
                self.market_share[tech][self.sim.t] = 0
        self.market_share['total'][self.sim.t] = (self.sold_cars['gas'][self.sim.t - 1] +
                                                  self.sold_cars['hybrid'][self.sim.t - 1] +
                                                  self.sold_cars['green'][self.sim.t - 1]) / total_cars_sold \
            if total_cars_sold > 0 else 0

    def bankrupt(self):
        return True if self.budget < 0 else False

    def change_portfolio(self):
        if len(self.cars) == 3 or 'gas' not in self.cars.keys():
            # Firms only move from gas to green and hybrid
            # Firm already has all portfolios
            return
        if self.budget > self.sim.params.cost_adoption:
            epsilon = self.sim.params.epsilon if self.sim.green_market_share[self.sim.t] == 0 \
                else self.sim.green_market_share[self.sim.t]
            prob_adoption = (((self.cars['gas'].EE / self.sim.params.energy_economy['max'] + self.sim.params.production_cost['min'] /
                               self.cars['gas'].production_cost) ** self.sim.params.omega) / 2) * epsilon ** (1 - self.sim.params.omega)
            self.sim.log.info(self.sim.params.cor.Fore.LIGHTRED_EX + f'Prob. adoption of a new portfolio: {prob_adoption:.4f}')
            if prob_adoption > self.sim.seed.random():
                # Choosing randomly between green or hybrid
                new_tech = self.sim.seed.choice(['green', 'hybrid'])
                # Determine costs of adopting each new technology
                # Choosing parameters of cost before calculating probability
                firms_available = [firm for firm in self.sim.firms.values() if new_tech in firm.cars]
                imitation_parameters = None, None, None
                if not firms_available:
                    # Be the first firm
                    pc, ec, ql = (self.sim.params.production_cost[new_tech], self.sim.params.energy_capacity[new_tech],
                                  self.sim.params.quality_level[new_tech])
                else:
                    # Choose company to imitate green technology, prob. proportional to firm size
                    weights = [f.market_share[new_tech][self.sim.t] for f in firms_available]
                    choices = self.sim.seed.choices(firms_available, weights=weights)
                    firm_to_imitate = choices[0]
                    car = firm_to_imitate.cars[new_tech]
                    # New car production will fall somewhere between initial value and imitated firm value
                    pc, ec, ql = (self.sim.seed.uniform(self.sim.params.production_cost[new_tech], car.production_cost),
                                  self.sim.seed.uniform(self.sim.params.energy_capacity[new_tech], car.EC),
                                  self.sim.seed.uniform(self.sim.params.quality_level[new_tech], car.QL))
                # Adopt Green
                print(self.sim.params.cor.Fore.LIGHTYELLOW_EX + f'Great news. Firm {self.id} has adopted '
                                                       f'a new {new_tech} portfolio '
                                                       f'at time {self.sim.t}')
                self.budget -= self.sim.params.cost_adoption
                self.cars[new_tech] = Vehicle(_type=new_tech,
                                              production_cost=pc,
                                              ec=ec,
                                              ee=self.sim.params.energy_economy[new_tech],
                                              ql=ql,
                                              firm=self)
                self.portfolio_marker = self.sim.t

    def invest_rd(self):
        # 1. Check available money
        if self.budget <= 0:
            return
        # 2. Update self.investments
        # This random factor is characterized as mu in the model description
        mu = self.sim.seed.uniform(0, self.sim.params.mu_max)
        investments = max(mu * self.budget, self.sim.params.rd_min)
        # Actually invest into vehicle
        self.invest_into_vehicle(investments)

    def invest_into_vehicle(self, investments):
        # eta = 1 if just one car, 1/2 if gas and green
        to_invest_now = investments * 1 if len(self.cars) == 1 else investments * .5
        for tech in self.cars.keys():
            rdm = self.sim.seed.random()
            # May improve PC (production_cost), EE, EC, QL
            # Choose which one randomly depending on current technology
            # 1. PC 2. EE or EC 3. QL
            choice = self.sim.seed.choice([1, 2, 3])
            if rdm < 1 - e ** (-self.sim.params.alpha1 * to_invest_now):
                # Success. Investment to occur!
                self.investments[tech][self.sim.t] += to_invest_now
                self.budget -= to_invest_now
                self.sim.log.info(self.sim.params.cor.Fore.LIGHTCYAN_EX + f'Advertise material. We, at firm {self.id}, '
                                                                 f'have made an investment on {tech} '
                                                                 f'of {to_invest_now:,.2f}')
                # 'PC_min', 'EE_max', 'EC_max', 'QL_max'
                if choice == 1:
                    if self.cars[tech].production_cost >= self.sim.params.production_cost['min']:
                        delta = self.sim.params.alpha2 * rdm * (self.sim.params.production_cost['min'] - self.cars[tech].production_cost)
                        self.cars[tech].production_cost += delta
                        self.sim.log.info(self.sim.params.cor.Fore.GREEN + f'Production cost reduced by {delta:,.2f}')
                elif choice == 3:
                    if self.cars[tech].QL <= self.sim.params.quality_level['max']:
                        delta = self.sim.params.alpha2 * rdm * (self.sim.params.quality_level['max'] - self.cars[tech].QL)
                        self.cars[tech].QL += delta
                        self.sim.log.info(self.sim.params.cor.Fore.MAGENTA + f'Quality increased by {delta:,.4f}')
                else:
                    if tech == 'gas':
                        if self.cars[tech].EE <= self.sim.params.energy_economy['max']:
                            delta = self.sim.params.alpha2 * rdm * (self.sim.params.energy_economy['max'] - self.cars[tech].EE)
                            self.cars[tech].EE += delta
                            self.sim.log.info(self.sim.params.cor.Fore.LIGHTYELLOW_EX + f'Energy economy increased by {delta:,.4f}')
                    else:
                        if self.cars[tech].EC <= self.sim.params.energy_capacity['max']:
                            delta = self.sim.params.alpha2 * rdm * (self.sim.params.energy_capacity['max'] - self.cars[tech].EC)
                            self.cars[tech].EC += delta
                            self.sim.log.info(self.sim.params.cor.Fore.GREEN + f'Energy capacity increased by {delta:,.4f}')

    def sales(self, car_type):
        # Register number of sold_cars
        self.sold_cars[car_type][self.sim.t] += 1

    def abandon_portfolio(self):
        if len(self.cars) == 1:
            return
        if self.sim.t - self.portfolio_marker < 10:
            return
        for car in self.cars.values():
            roi = self.calculate_roi(car)
            self.sim.log.info(f'ROI for firm {self.id} is {roi:.2f}')
            if roi < 1:
                print(self.sim.params.cor.Fore.LIGHTRED_EX + f'Abandoning portfolio {car.type}: firm {self.id} '
                                                    f'at time {self.sim.t}')
                # Also, restrict new change, setting marker
                self.portfolio_marker = self.sim.t
                del self.cars[car.type]
                # This return guarantees it just gives up one car portfolio each period.
                return

    def calculate_roi(self, car):
        # ROI is dependent on each vehicle
        # IMPLEMENTED REDUCTOR OF PROBABILITY GIVEN MORE TIME OF ADOPTION: e ** (-.01 * time_adoption)
        if self.investments[car.type][self.sim.t - 1] > 0:
            return self.sim.params.p_lambda * car.production_cost * self.sold_cars[car.type][self.sim.t - 1] / \
                   self.investments[car.type][self.sim.t - 1]
        else:
            return 0
