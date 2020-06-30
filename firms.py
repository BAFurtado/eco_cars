import params


class Firm:
    """ Produce and market vehicles
    """
    def __init__(self):
        # Margin of cost
        self.a = None


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
        self.PC = None
        # Energy: distance per unit of energy (engine power per km)
        self.EE = None
        # Energy capacity: quantity of units able to carry
        self.EC = None
        # Quality
        self.QL = None
        self.price = None

    def distance_run(self):
        return self.EE * self.EC

    def running_cost(self, pe):
        return pe/self.EE

    def emissions(self, em):
        return em/self.EE

    def calculate_price(self, a, IVA):
        self.price = (1 + IVA) * (1 + a) * self.PC - 1






