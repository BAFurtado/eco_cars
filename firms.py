import params


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
        self.portfolio = 'combustion'
        self.profit = 0
        # Investments in R&D
        self.investments = 0
        self.sold_cars = dict()
        # Assign a vehicle for this firm to sell
        self.cars = dict()
        self.roi = dict()

    def update_budget(self):
        self.budget += self.profit - params.cost_adoption - self.investments

    def calculate_profit(self):
        # TODO: check when to verify whether to go bankrupt
        if self.budget < 0:
            # Firm is bankrupt, trigger new company
            pass
        # Make new budget
        # update self.profit
        for car in self.cars:
            self.profit += self.sold_cars[car] * self.cars[car].sales_price - params.fixed_costs

    def change_portfolio(self, info):
        # Determine costs of new_technology_adoption
        # TODO: Generalize for more than one car
        prob_adoption = ((self.car.EE/params.energy_economy['max'] + params.production_cost['min']
                          /self.car.production_cost) ** params.omega)/2 * \
                        (info['green_share'] + info['epsilon']) ** (1 - params.omega)
        # Choose company to imitate green technology, prob. proportional to firm size
        # New car production will fall somewhere between current Vehicle EC, QL, production_cost

        # abandon current technology depends on magnitude of ROI and how long it has been adopted
        # TODO: set a time marker for portfolio change

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
        # Register number of sold_cars and prices_sold
        # TODO: Remember to reset every new turn
        # Check if there is more than one car
        self.sold_cars[car] += 1

    def calculate_roi(self, car):
        # ROI is dependent on each vehicle
        self.roi[car] = params.p_lambda * car.production_cost * self.sold_cars / self.investments


class Vehicle:
    """ Type
        1. Combustion: 'gas'
        2. Electric: 'green'

        CO2 emission reduction is the goal
        """
    def __init__(self):
        # Type: 'combustion' or 'electric'
        self.type = 'gas'
        # Price (production_cost)
        self.production_cost = params.production_cost[self.type]
        # Energy: distance per unit of energy (engine power per km)
        self.EE = params.energy_economy[self.type]
        # Energy capacity: quantity of units able to carry
        self.EC = params.energy_capacity[self.type]
        # Quality
        self.QL = params.quality_level[self.type]
        self.sales_price = None

    def autonomy(self):
        return self.EE * self.EC

    def running_cost(self):
        return params.price_energy[self.type]/self.EE

    def emissions(self):
        return params.emission[self.type]/self.EE

    def calculate_price(self, a):
        self.sales_price = (1 + params.iva) * (1 + a) * self.production_cost - 1
