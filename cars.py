import params


class Vehicle:
    """ Type
        1. Combustion: 'gas'
        2. Electric: 'green'

        CO2 emission reduction is the goal
        """
    def __init__(self, _type='gas',
                 production_cost=params.production_cost['gas'],
                 # Distance (km) a car can travel per unit of energy consumed
                 ee=params.energy_economy['gas'],
                 # Storage size
                 ec=params.energy_capacity['gas'],
                 # Performance measure ~= quality characteristics
                 ql=params.quality_level['gas'],
                 firm=None):
        # Type: 'combustion' or 'electric', 'gas' or 'green'
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
        self.owed_taxes = 0
        self.policy_value_discount = 0

    def drive_range(self):
        # Driving range (DR)
        return self.EE * self.EC

    def emissions(self):
        return params.emission[self.type]/self.EE

    def calculate_price(self):
        # policy_value é DESCONTO. policy_tax é SOBRETAXA OU DESCONTO NA TAXA
        # Politica Brasileira: descontar do IPI  no minimo 3% quando a fabrica inicia desenvolvimento do carro eletrico
        policy_value, policy_tax = 0, 0

        if self.firm.sim.policy['policy'] == 'tax':
            policy_tax = params.tax[self.firm.sim.policy['level']]
        elif self.firm.sim.policy['policy'] == 'max_e':
            # First part refers to intensity of policy. Second refers to Table 5 levels
            e_parameter = params.discount_tax_table(self.firm.sim.e, self.emissions())
            policy_tax = params.tax[self.firm.sim.policy['level']] * e_parameter
        # P&D CASHBACK Policy should be applied at the firm level. Not the car level.
        # Sales Price does not include FREIGHT and ICMS.
        # They are added at the moment of evaluation and purchasing of the consumer
        self.sales_price = (1 + params.pis[self.type]) * \
                           (1 + params.cofins[self.type]) * \
                           (1 + params.ipi[self.type]) * \
                           (1 + params.p_lambda) * (1 + policy_tax) * self.production_cost + policy_value
        self.owed_taxes = (policy_tax + params.pis[self.type] +
                           params.cofins[self.type] +
                           params.ipi[self.type]) * self.production_cost
        self.policy_value_discount = policy_value
        return self.owed_taxes + self.policy_value_discount

    def criteria_selection(self, emotion, region, criteria1, criteria2):
        ms1 = self.firm.market_share[self.type][self.firm.sim.t]
        # Included FREIGHT from firm region to consumer region!
        # Included ICMS charged on DESTIN. That is, the region of the CONSUMER
        criteria = {'car_affordability': 1 / ((self.sales_price * (1 + params.icms[region])) +
                                              params.freight[self.firm.region][region]),
                    'use_affordability': 1 / params.price_energy[self.type],
                    'stations': params.stations['gas'] if self.type == 'gas'
                    else self.firm.sim.green_stations[self.firm.sim.t],
                    'market_share': max(ms1, params.epsilon),
                    'energy_capacity': self.EC,
                    'car_cleanness': 1 / self.emissions(),
                    'quality': self.QL,
                    'emotion': emotion}

        return criteria[criteria1] * criteria[criteria2]
