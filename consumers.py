import params


class Consumer:
    """ Purchase and use vehicles
    """

    def __init__(self, _id, sim):
        self.id = _id
        self.price_max = sim.seed.normalvariate(params.p_max['mu'], params.p_max['sigma'])
        # Value that represents consumer emotion (Br)
        self.emotion = sim.seed.random()
        self.my_car = None
        self.distance = sim.seed.normalvariate(params.distance['mu'], params.distance['sigma'])

    def purchase(self, sim):
        # Probability to buy a new car: params.prob_adoption
        if not sim.seed.random() < params.prob_adoption:
            return
        # Conditions to enter the market
        # 1. Condition, car price less than my reserve price and can go the distance
        # Dk: minimum distance parameter
        choice = sim.seed.random()
        # Calculate needed range
        if choice < .23:
            dk = sim.seed.uniform(params.dk['23']['min'], params.dk['23']['max'])
        elif choice < .45:
            dk = sim.seed.uniform(params.dk['22']['min'], params.dk['22']['max'])
        else:
            dk = sim.seed.uniform(params.dk['55']['min'], params.dk['55']['max'])
        # Policy introduced here. When testing policy e_max will be endogenously set
        # My market includes affordable cars, within needed range and within regulation, if applicable.
        my_market = [car for firm in sim.firms.values() for car in firm.cars.values()
                     if car.sales_price < self.price_max and car.drive_range() > dk and
                     car.emissions() < sim.e_max]
        # Stop if no cars in pre-selection above
        if not my_market:
            return

        # Choose two criteria to evaluate among possible purchases
        criteria = ['car_affordability', 'use_affordability', 'stations', 'market_share',
                    'energy_capacity', 'car_cleanness', 'quality', 'emotion']
        criteria1, criteria2 = sim.seed.choices(criteria, k=2)
        my_market.sort(key=lambda c: c.criteria_selection(self.emotion, criteria1, criteria2), reverse=True)

        self.my_car = my_market[0]
        self.my_car.firm.sales(self.my_car.type)
        sim.update_car_info(self.my_car.type)

    def driving(self):
        # Return emissions
        return self.distance * self.my_car.emissions() if self.my_car else 0
