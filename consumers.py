import params


class Consumer:
    """ Purchase and use vehicles
    """

    def __init__(self, id, sim):
        self.id = id
        self.price_max = sim.seed.normalvariate(params.p_max['mu'], params.p_max['sigma'])
        self.my_car = None
        self.distance = sim.seed.normalvariate(params.distance['mu'], params.distance['sigma'])

    def purchase(self, cars, dk):
        # Probability to buy a new car: params.prob_adoption
        # Conditions to enter the market
        my_market = [car for car in cars if (car.price < min(self.price_max, self.price_max)) and
                     (car.EC > dk)]
        # TODO: Select two random characteristics c1 c2 from table2 (p.10)
        # TODO: Sort by utility which is c1 x c2
        self.my_car = None

    def driving(self):
        # Return emissions
        # TODO: determine how to calculate distance. Import em
        return self.distance * self.my_car.emissions()
