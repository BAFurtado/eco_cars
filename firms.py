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
        self.profit = {'gas': defaultdict(float),
                       'green': defaultdict(float)}
        # Investments in R&D
        self.investments = {'gas': defaultdict(float),
                            'green': defaultdict(float)}
        self.sold_cars = {'gas': defaultdict(int),
                          'green': defaultdict(int)}
        # Assign a vehicle for this firm to sell
        self.cars = dict()
        self.market_share = {'gas': defaultdict(float),
                             'green': defaultdict(float),
                             'total': defaultdict(float)}
        self.sim = sim
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
        self.budget -= params.fixed_costs if self.sim.t != 0 else 0

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
                                              - self.cars[tech].owed_taxes - self.cars[tech].policy_value_discount)

    def update_market_share(self, total_cars_sold):
        if self.sim.t == 0:
            self.market_share['gas'][0] = 0
            self.market_share['total'][0] = 0
            return
        for tech in ['gas', 'green']:
            if tech in self.cars and self.sim.num_cars[tech][self.sim.t - 1] > 0:
                self.market_share[tech][self.sim.t] = self.sold_cars[tech][self.sim.t - 1] / \
                                                      self.sim.num_cars[tech][self.sim.t - 1]
            else:
                self.market_share[tech][self.sim.t] = 0
        self.market_share['total'][self.sim.t] = (self.sold_cars['gas'][self.sim.t - 1] +
                                                  self.sold_cars['green'][self.sim.t - 1]) / total_cars_sold \
            if total_cars_sold > 0 else 0

    def bankrupt(self):
        return True if self.budget < 0 else False

    def change_portfolio(self):
        if len(self.cars) == 2:
            # Firm already has both portfolios
            return
        if 'green' in self.cars.keys():
            # Firms only move from gas to green
            return
        if self.budget > params.cost_adoption:
            epsilon = params.epsilon if self.sim.green_market_share[self.sim.t] == 0 \
                else self.sim.green_market_share[self.sim.t]
            prob_adoption = (((self.cars['gas'].EE / params.energy_economy['max'] + params.production_cost['min'] /
                               self.cars['gas'].production_cost) ** params.omega) / 2) * epsilon ** (1 - params.omega)
            # A formula anterior prob_adoption tem em erro. Ao epsilon temos adicionar o Green Market_Share.
            self.sim.log.info(params.cor.Fore.LIGHTRED_EX + f'Prob. adoption of green portfolio: {prob_adoption:.4f}')
            if prob_adoption > self.sim.seed.random():
                # Determine costs of adopting green technology
                # Choosing parameters of cost before calculating probability
                greens = [firm for firm in self.sim.firms.values() if 'green' in firm.cars]
                imitation_parameters = None, None, None
                if not greens:
                    # Be the first firm
                    pc, ec, ql = (params.production_cost['green'], params.energy_capacity['green'],
                                  params.quality_level['green'])
                else:
                    # Choose company to imitate green technology, prob. proportional to firm size
                    weights = [f.market_share['green'][self.sim.t] for f in greens]
                    choices = self.sim.seed.choices(greens, weights=weights)
                    firm_to_imitate = choices[0]
                    car = firm_to_imitate.cars['green']
                    # New car production will fall somewhere between initial value and imitated firm value
                    # Não estou achando os parametros car.production_cost, car.E e car.QL
                    pc, ec, ql = (self.sim.seed.uniform(params.production_cost['green'], car.production_cost),
                                  self.sim.seed.uniform(params.energy_capacity['green'], car.EC),
                                  self.sim.seed.uniform(params.quality_level['green'], car.QL))
                # Adopt Green
                print(params.cor.Fore.LIGHTYELLOW_EX + f'Great news. Firm {self.id} has adopted a new green portfolio '
                                                       f'at time {self.sim.t}')
                self.budget -= params.cost_adoption
                self.cars['green'] = Vehicle(_type='green',
                                             production_cost=pc,
                                             ec=ec,
                                             ee=params.energy_economy['green'],
                                             ql=ql,
                                             firm=self)
                self.portfolio_marker = self.sim.t

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
        # eta = 1 if just one car, 1/2 if gas and green
        to_invest_now = investments * 1 if len(self.cars) == 1 else investments * .5
        for tech in self.cars.keys():
            rdm = self.sim.seed.random()
            # May improve PC (production_cost), EE, EC, QL
            # Choose which one randomly depending on current technology
            # 1. PC 2. EE or EC 3. QL
            choice = self.sim.seed.choice([1, 2, 3])
            if rdm < 1 - e ** (-params.alpha1 * to_invest_now):
                # Success. Investment to occur!
                # TODO: implement future reduction on investments costs
                self.investments[tech][self.sim.t] += to_invest_now
                self.budget -= to_invest_now
                self.sim.log.info(params.cor.Fore.LIGHTCYAN_EX + f'Advertise material. We, at firm {self.id}, '
                                                                 f'have made an investment on {tech} '
                                                                 f'of {to_invest_now:,.2f}')
                # 'PC_min', 'EE_max', 'EC_max', 'QL_max'
                if choice == 1:
                    if self.cars[tech].production_cost >= params.production_cost['min']:
                        delta = params.alpha2 * rdm * (params.production_cost['min'] - self.cars[tech].production_cost)
                        self.cars[tech].production_cost += delta
                        self.sim.log.info(params.cor.Fore.GREEN + f'Production cost reduced by {delta:,.2f}')
                elif choice == 3:
                    if self.cars[tech].QL <= params.quality_level['max']:
                        delta = params.alpha2 * rdm * (params.quality_level['max'] - self.cars[tech].QL)
                        self.cars[tech].QL += delta
                        self.sim.log.info(params.cor.Fore.MAGENTA + f'Quality increased by {delta:,.4f}')
                else:
                    if tech == 'gas':
                        if self.cars[tech].EE <= params.energy_economy['max']:
                            delta = params.alpha2 * rdm * (params.energy_economy['max'] - self.cars[tech].EE)
                            self.cars[tech].EE += delta
                            self.sim.log.info(params.cor.Fore.LIGHTYELLOW_EX + f'Energy economy increased by {delta:,.4f}')
                    else:
                        if self.cars[tech].EC <= params.energy_capacity['max']:
                            delta = params.alpha2 * rdm * (params.energy_capacity['max'] - self.cars[tech].EC)
                            self.cars[tech].EC += delta
                            self.sim.log.info(params.cor.Fore.GREEN + f'Energy capacity increased by {delta:,.4f}')

    def sales(self, car_type):
        # Register number of sold_cars
        self.sold_cars[car_type][self.sim.t] += 1

    def abandon_portfolio(self):
        if len(self.cars) == 1:
            return
        for car in self.cars.values():
            if self.sim.t - self.portfolio_marker < 10:
                continue
            roi = self.calculate_roi(car)
            self.sim.log.info(f'ROI for firm {self.id} is {roi:.2f}')
            if roi < 1:
                print(params.cor.Fore.LIGHTRED_EX + f'Abandoning portfolio {car.type}: firm {self.id} '
                                                    f'at time {self.sim.t}')
                # Also, restrict new change, setting marker
                self.portfolio_marker = self.sim.t
                del self.cars[car.type]
                return

    def calculate_roi(self, car):
        # ROI is dependent on each vehicle
        # IMPLEMENTED REDUCTOR OF PROBABILITY GIVEN MORE TIME OF ADOPTION: e ** (-.01 * time_adopation)
        if self.investments[car.type][self.sim.t - 1] > 0:
            return params.p_lambda * car.production_cost * self.sold_cars[car.type][self.sim.t - 1] / \
                   self.investments[car.type][self.sim.t - 1]
        else:
            return 0
