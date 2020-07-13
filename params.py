""" Exogenous inputs
"""

# Initiating time parameter
T = 40
num_firms = 8
num_consumers = 2000

# Vehicles characteristics ---------------------------------------------
production_cost = {'green': 27356, 'gas': 16950, 'min': 10000}
energy_economy = {'green': 66.2, 'gas': 15.9, 'max': 66.2}
energy_capacity = {'green': 2.35, 'gas': 60, 'max': 60}
quality_level = {'green': .5, 'gas': .5, 'max': 1}
emission = {'green': 1, 'gas': 23.06}
price_energy = {'green': 1.12, 'gas': 1.6}
stations = {'green': 2, 'gas': 1}
iva = .196

# Firms characteristics ---------------------------------------------
budget_max_limit = 500000
fixed_costs = 25000
mu_max = .1
rd_min = 50000
alpha1 = 1e-5
alpha2 = .5
# epsilon is calculated when there is at least one firm that is green. Otherwise it is .1 -- check model.info()
omega = .5
# Costs of adoption of new technology
cost_adoption = 10000
# ROI
p_lambda = .1

# Consumers characteristics ---------------------------------------------
# Distance of consumers
prob_adoption = .25
distance = {'mu': 11755, 'sigma': 2500}
p_max = {'mu': 29000, 'sigma': 5000}
dk = {'23': {'min': 0, 'max': 99},
      '22': {'min': 100, 'max': 249},
      '55': {'min': 250, 'max': 953}}
br = {'min': 0, 'max': 1}

# Policy characteristics ---------------------------------------------

