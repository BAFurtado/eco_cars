import params
from cars import Vehicle
from collections import defaultdict

class Firm:
    """ Produce and market vehicles
    """
    def __init__(self, id, sim):
        self.id = id
        # Margin of cost
        # TODO: Check if this "a" is the same of params.p_lambda
        self.a = None
        # Budget
        self.budget = sim.seed.randint(0, params.budget_max_limit)
        # Firm configuration decisions:
        self.portfolio = 'gas'
        self.profit = 0
        # Investments in R&D
        self.investments = 0
        self.sold_cars = defaultdict(int)
        # Assign a vehicle for this firm to sell
        self.cars = dict()
        self.market_share = None
        self.sim = sim
        self.create_gas_car()

    def create_gas_car(self):
        self.cars['gas'] = Vehicle(firm=self)

    def update_budget(self):
        self.budget += self.profit - params.cost_adoption - self.investments

    def bankrupt(self):
        return True if self.budget < 0 else False

    def update_profit(self):
        self.profit = 0
        for car in self.cars:
            self.profit += self.sold_cars[car] * self.cars[car].sales_price - params.fixed_costs

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
                self.cars['green'] = Vehicle(_type='green',
                                             production_cost=pc,
                                             ec=ec,
                                             ee=params.energy_economy['green'],
                                             ql=ql,
                                             firm=self)

    def invest_rd(self, sim):
        # 1. Check available money
        # 2. Update self.investments
        # This random factor is characterized as mu in the model description
        mu = sim.seed.uniform(0, params.mu_max)
        mu = min(mu * self.budget, params.rd_min)
        self.investments = mu * self.budget

    def invest_into_vehicle(self, sim):
        # May improve PC (production_cost), EE, EC, QL
        # eta = 1 if just one car, 1/2 if gas and green
        eta = 1 if len(self.cars) == 1 else .5

        # If 'electric' possible candidates are production_cost, EC, QL else production_cost, EE, QL
        # choose characteristic randomly
        # for the chosen_one,
        # TODO: this has to work for more than one car
        rdm = sim.seed.random()
        if rdm < 1 ** -(-params.alpha1 * self.investments):
            # Success
            # Choose a random car to invest into?
            car = sim.seed.choice(self.cars)
            # TODO: make correct decision on the line below
            # TODO: remember PC is min, the rest max (bring these values from sim)
            tech_to_improve = sim.seed.choice('EC_max', 'PC_min', 'EE_max', 'QL_max')
            delta = params.alpha2 * rdm * (tech_to_improve - car) # TODO: add correct characteristic
            # TODO: delta is then added to chosen characteristic

    def sales(self, car):
        # Register number of sold_cars
        # TODO: Remember to reset every new turn
        self.sold_cars[car] += 1

    def calculate_roi(self, car):
        # ROI is dependent on each vehicle
        return params.p_lambda * car.production_cost * self.sold_cars / self.investments

    def update_market_share(self, num_cars_this_model):
        return len(self.sold_cars / num_cars_this_model)
