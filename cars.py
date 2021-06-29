from numpy import prod


class Vehicle:
    """ Type
        1. Combustion: 'gas'
        2. Electric: 'green'

        CO2 emission reduction is the goal
        """
    def __init__(self, firm, _type='gas', production_cost=None, ee=None, ec=None, ql=None):
        # Type: 'combustion' or 'electric', 'gas' or 'green'
        self.type = _type
        # Price (production_cost)
        self.production_cost = firm.sim.params.production_cost['gas'] if not production_cost else production_cost
        # Energy: distance per unit of energy (engine power per km)
        self.EE = firm.sim.params.energy_economy['gas'] if not ee else ee
        # Energy capacity: quantity of units able to carry
        self.EC = firm.sim.params.energy_capacity['gas'] if not ec else ec
        # Quality
        self.QL = firm.sim.params.quality_level['gas'] if not ql else ql
        self.firm = firm
        self.sales_price = None
        self.calculate_price()
        self.owed_taxes = 0

    def drive_range(self):
        # Driving range (DR)
        return self.EE * self.EC

    def emissions(self):
        return self.firm.sim.params.emission[self.type]/self.EE

    def calculate_price(self):
        # policy_value é DESCONTO. policy_tax é SOBRETAXA OU DESCONTO NA TAXA
        # Politica Brasileira: descontar do IPI  no minimo 3% quando a fabrica inicia desenvolvimento do carro eletrico
        policy_tax = 0
        if self.firm.sim.policy['policy'] == 'tax':
            policy_tax = self.firm.sim.params.tax[self.firm.sim.policy['level']]
        elif self.firm.sim.policy['policy'] == 'e_max':
            # First part refers to intensity of policy. Second refers to Table 5 levels
            e_parameter = self.firm.sim.params.discount_tax_table(self.firm.sim.e, self.emissions())
            # tax parameter
            policy_tax = self.firm.sim.params.e_max_tax[self.firm.sim.policy['level']] * e_parameter
        # P&D CASHBACK Policy should be applied at the firm level. Not the car level.
        # Sales Price does not include FREIGHT and ICMS.
        # They are added at the moment of evaluation and purchasing of the consumer
        self.sales_price = (1 + self.firm.sim.params.pis[self.type]) * \
                           (1 + self.firm.sim.params.cofins[self.type]) * \
                           (1 + self.firm.sim.params.ipi[self.type]) * \
                           (1 + self.firm.sim.params.p_lambda) * (1 + policy_tax) * self.production_cost
        self.owed_taxes = (policy_tax + self.firm.sim.params.pis[self.type] +
                           self.firm.sim.params.cofins[self.type] +
                           self.firm.sim.params.ipi[self.type]) * self.production_cost
        return self.owed_taxes

    def criteria_selection(self, emotion, region, *criteria):
        ms1 = self.firm.market_share[self.type][self.firm.sim.t]
        # Included FREIGHT from firm region to consumer region!
        # Included ICMS charged on DESTIN. That is, the region of the CONSUMER
        criterion = {'car_affordability': 1 / ((self.sales_price * (1 + self.firm.sim.params.icms[region])) +
                                               self.firm.sim.params.freight[self.firm.region][region]),
                     'use_affordability': 1 / self.firm.sim.params.price_energy[region][self.type],
                     'stations': self.firm.sim.green_stations[self.firm.sim.t] if self.type == 'green'
                     else self.firm.sim.params.stations['gas'],
                     'market_share': max(ms1, self.firm.sim.params.epsilon),
                     'energy_capacity': self.EC,
                     'car_cleanness': 1 / self.emissions(),
                     'quality': self.QL,
                     'emotion': emotion}
        res = 1
        for c in criteria[0]:
            res *= criterion[c]
        return res
