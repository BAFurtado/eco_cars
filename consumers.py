import params


class Consumer:
    """ Purchase and use vehicles
    """

    def __init__(self, sim):
        # TODO: set min, max of purchase_capacity
        self.purchase_capacity = sim.seed.randint(100, 200)
        self.price_max = None
        self.my_car = None

    def purchase(self, cars, dk):
        # Conditions to enter the market
        my_market = [car for car in cars if (car.price < min(self.purchase_capacity, self.price_max)) and
                     (car.EC > dk)]
        # TODO: Select two random characteristics c1 c2 from table2 (p.10)
        # TODO: Sort by utility which is c1 x c2

    def driving(self):
        # Return emissions
        # TODO: determine how to calculate distance. Import em
        em = params.em_combustion if self.my_car.type == 'combustion' else params.em_electric
        return params.Dk * self.my_car.emissions(em)
