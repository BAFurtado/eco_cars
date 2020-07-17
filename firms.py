import params
from cars import Vehicle
from collections import defaultdict


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
        self.budget += self.profit - sum(self.investments.values())
        self.investments = defaultdict(int)
        self.profit = 0

    def update_market_share(self, total):
        self.market_share = self.profit / total

    def bankrupt(self):
        return True if self.budget < 0 else False

    def update_profit(self):
        # Sales income is accounted for at update profit, followed by update budget iteration
        for car in self.cars:
            self.profit += self.sold_cars[car] * self.cars[car].sales_price - params.fixed_costs
            self.sold_cars[car] = 0
        return self.profit

    def change_portfolio(self):
        if self.budget > params.cost_adoption:
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
            # TODO: Check energy_economy is always 1
            prob_adoption = ((params.energy_economy['green'] / params.energy_economy['max']
                              + params.production_cost['min'] / pc) ** params.omega) / 2 * \
                            (self.sim.current_data['green_share'] + self.sim.current_data['epsilon']) ** \
                            (1 - params.omega)

            if prob_adoption > self.sim.seed.random():
                # Adopt Green
                self.budget -= params.cost_adoption
                self.cars['green'] = Vehicle(_type='green',
                                             production_cost=pc,
                                             ec=ec,
                                             ee=params.energy_economy['green'],
                                             ql=ql,
                                             firm=self)
                self.green_adoption_marker = self.sim.t

    def abandon_portfolio(self):
        if len(self.cars) == 1:
            return
        if self.sim.t - self.green_adoption_marker < 10:
            return
        for car in self.cars.values():
            roi = self.calculate_roi(car)
            if self.sim.seed.random() < roi:
                print(f'Abandoning a portfolio: firm {self.id}')
                del self.cars[car.type]
                return

    def invest_rd(self):
        # 1. Check available money
        if self.budget <= 0:
            return
        # 2. Update self.investments
        # This random factor is characterized as mu in the model description
        mu = self.sim.seed.uniform(0, params.mu_max)
        mu = min(mu * self.budget, params.rd_min)
        investments = mu * self.budget
        for key in self.investments.keys():
            # eta = 1 if just one car, 1/2 if gas and green
            self.investments[key] += investments * 1 if len(self.investments) == 1 else investments * .5
        # Actually invest into vehicle
        self.invest_into_vehicle()

    def invest_into_vehicle(self):
        # May improve PC (production_cost), EE, EC, QL
        # Choose which one randomly depending on current technology
        # 1. PC 2. EE or EC 3. QL
        choice = self.sim.seed.choice([1, 2, 3])
        for tech in self.cars.keys():
            rdm = self.sim.seed.random()
            if rdm < 1 ** -(-params.alpha1 * self.investments[tech]):
                # Success. Investment to occur!
                print(f'Advertise material. We, at firm {self.id}, have made an investment of '
                      f'{sum(self.investments.values())}')
                # 'PC_min', 'EE_max', 'EC_max', 'QL_max'
                if choice == 1:
                    delta = params.alpha2 * rdm * (params.production_cost['min'] - self.cars[tech].production_cost)
                    self.cars[tech].production_cost -= delta
                elif choice == 3:
                    delta = params.alpha2 * rdm * (params.quality_level['max'] - self.cars[tech].QL)
                    self.cars[tech].QL += delta
                else:
                    if tech == 'gas':
                        # EE
                        delta = params.alpha2 * rdm * (params.energy_economy['max'] - self.cars[tech].EE)
                        self.cars[tech].EE += delta
                    else:
                        # EC
                        delta = params.alpha2 * rdm * (params.energy_capacity['max'] - self.cars[tech].EC)
                        self.cars[tech].EC += delta

    def sales(self, car):
        # Register number of sold_cars
        self.sold_cars[car] += 1

    def calculate_roi(self, car):
        # ROI is dependent on each vehicle
        return params.p_lambda * car.production_cost * self.sold_cars[car.type] / self.investments[car.type]
