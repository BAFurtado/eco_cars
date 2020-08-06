import params


class Vehicle:
    """ Type
        1. Combustion: 'gas'
        2. Electric: 'green'

        CO2 emission reduction is the goal
        """
    def __init__(self, _type='gas',
                 production_cost=params.production_cost['gas'],
                 ee=params.energy_economy['gas'],
                 ec=params.energy_capacity['gas'],
                 ql=params.quality_level['gas'],
                 firm=None):
        # Type: 'combustion' or 'electric'
        self.type = _type
        # Price (production_cost)
        self.production_cost = production_cost
        # Energy: distance per unit of energy (engine power per km)
        self.EE = ee
        # Energy capacity: quantity of units able to carry
        self.EC = ec
        # Quality
        self.QL = ql
        self.firm = firm
        self.sales_price = None
        self.calculate_price()

    def autonomy(self):
        return self.EE * self.EC

    def emissions(self):
        return params.emission[self.type]/self.EE

    def calculate_price(self):
        policy_value, policy_tax = 0, 0
        e_parameter = params.discount_tax_table(self.firm.sim.e, self.emissions())
        if 'tax' in self.firm.sim.policy.keys():
            # First part refers to 'low', 'high' [.1, .5], Second refers to Table 5 levels
            policy_tax = next(iter(self.firm.sim.policy['tax'].values())) * e_parameter
        elif 'discount' in self.firm.sim.policy.keys():
            policy_value = next(iter(self.firm.sim.policy['discount'].values())) * e_parameter
        elif 'green_support' in self.firm.sim.policy.keys():
            # Only for green cars that perform less than average benchmark
            if self.type == 'green' and self.emissions() < self.fimr.sim.e:
                policy_value = next(iter(self.firm.sim.policy['green_support'].values())) * e_parameter
        self.sales_price = (1 + params.iva) * (1 + params.p_lambda) * \
                           (1 + policy_tax) * self.production_cost - 1 + policy_value
        return policy_tax * self.production_cost + policy_value

    def criteria_selection(self, emotion, criteria1, criteria2):
        ms1 = self.firm.market_share[self.type][self.firm.sim.t]
        criteria = {'price_accessibility': 1/self.sales_price,
                    'use_accessibility': 1/params.price_energy[self.type],
                    'stations': params.stations['gas'] if self.type == 'gas' else self.firm.sim.green_stations[self.firm.sim.t],
                    'market_share': max(ms1, params.epsilon),
                    'energy_capacity': self.EC,
                    'car_cleanness': 1/self.autonomy(),
                    'quality': self.QL,
                    'emotion': emotion}

        return criteria[criteria1] * criteria[criteria2]
