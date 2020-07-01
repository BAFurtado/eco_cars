import params


class Firm:
    """ Produce and market vehicles
    """
    def __init__(self, sim):
        # Margin of cost
        self.a = None
        # Budget
        self.B0 = sim.seed.random.randint()
        # Firm configuration decisions:
        self.portfolio = 'combustion'
        self.profit = 0
        # Costs of adoption of new technology
        self.Cad = 0
        # Investments in R&D
        self.investments = 0
        self.sold_cars = 0
        # Assign a vehicle for this firm to sell
        self.cars = Vehicle()

    def update_budget(self):
        self.B0 = self.profit - self.Cad - self.investments

    def calculate_profit(self):
        # TODO: check when to verify whether to go bankrupt
        if self.B0 < 0:
            # Firm is bankrupt, trigger new company
            pass
        # Make new budget
        # update self.profit
        self.profit = self.sold_cars * self.cars.sales_price - params.Fixed_Costs
        pass

    def change_portfolio(self, info):
        # Determine costs of new_technology_adoption
        prob_adoption = (info['green_share'] + params.epsilon) ** (1 - params.omega)
        pass

    def invest_rd(self):
        # 1. Check available money
        # 2. Update self.investments
        pass

    def sales(self):
        # Register number of sold_cars and prices_sold
        # TODO: Remember to reset every new turn
        # Check if there is more than one car
        self.sold_cars += 1
        pass


class Vehicle:
    """ Type
        1. Combustion
        2. Electric

        CO2 emission
        """
    def __init__(self):
        # Type: 'combustion' or 'electric'
        self.type = None
        # Price (cost of production)
        self.cost_production = None
        # Energy: distance per unit of energy (engine power per km)
        self.EE = None
        # Energy capacity: quantity of units able to carry
        self.EC = None
        # Quality
        self.QL = None
        self.sales_price = None

    def distance_run(self):
        return self.EE * self.EC

    def running_cost(self, pe):
        return pe/self.EE

    def emissions(self, em):
        return em/self.EE

    def calculate_price(self, a, IVA):
        self.sales_price = (1 + IVA) * (1 + a) * self.cost_production - 1
