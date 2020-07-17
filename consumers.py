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
        choice = sim.seed.random() < params.prob_adoption
        if not choice:
            return
        # Conditions to enter the market
        # 1. Condition, car price less than my reserve price and can go the distance
        my_market = [car for firm in sim.firms.values() for car in firm.cars.values()
                     if car.sales_price < self.price_max and car.autonomy() > self.distance]
        if not my_market:
            return

        my_market.sort(key=lambda c: c.criteria_selection(self.emotion), reverse=True)

        self.my_car = my_market[0]
        self.my_car.firm.sales(self.my_car)
        sim.update_car_info(self.my_car)

    def driving(self):
        # Return emissions
        return self.distance * self.my_car.emissions() if self.my_car else 0
