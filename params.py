""" Exogenous inputs
"""
import colorama as cor
import bisect
from numpy import linspace

# Initiating time parameter
T = 40
num_firms = 8
num_consumers = 2000
regions_consumers = {'n': .0832, 'ne': .2783, 'se': .4213, 's': .1436, 'co': 1 - .0832 - .2783 - .4213 - .1436}
# TODO. Still waiting for actual input of number of firms here!
regions_firms = {'n': 0, 'ne': 3, 'se': 15, 's': 5, 'co': 1}

# Vehicles characteristics ---------------------------------------------
production_cost = {'green': 35.158, 'hybrid': 23474, 'gas': 18163, 'min': 10000}
energy_economy = {'green': 64.13, 'hybrid': 15.4, 'gas': 12.75, 'max': 66.2}
energy_capacity = {'green': 4.21, 'hybrid': 43, 'gas': 50, 'max': 60}
quality_level = {'green': .5, 'hybrid': .5, 'gas': .5, 'max': 1}
emission = {'green': 0, 'hybrid': 12.94, 'gas': 13.64}

# Price of hybrid is going to be taken as an average of the two
price_energy = {'co': {'green': .88, 'gas': .73},
                'ne': {'green': .81, 'gas': .74},
                'n': {'green': .99, 'gas': .73},
                'se': {'green': .89, 'gas': .75},
                's': {'green': .82, 'gas': 71}}
stations = {'green': 1, 'hybrid': 1, 'gas': 2}
pis = {'gas': .0165, 'hybrid': .02, 'green': .02}
cofins = {'gas': .076, 'hybrid': 0.96, 'green': .096}
ipi = {'gas': .11, 'hybrid': .07, 'green': .08}
icms = {'co': .1271, 'ne': .145, 'n': .157, 'se': .1322, 's': .1167}

# Firms characteristics ---------------------------------------------
budget_max_limit = 500000
fixed_costs = 25000
mu_max = .1
rd_min = 50000
alpha1 = 1e-5
alpha2 = .5
# epsilon is calculated when there is at least one firm that is green
epsilon = .1
omega = .5
# Costs of adoption of new technology
cost_adoption = 10000
# ROI
p_lambda = .1

# Our parameter to implement reduction of probability of adoption as long as it gets
k = -.01

# Consumers characteristics ---------------------------------------------
# Distance of consumers
prob_adoption = .25
distance = {'mu': 11755, 'sigma': 2500}

p_max_proportion = {'n': .6436, 'ne': .5899, 'se': 1, 's': .9341, 'co': .9423}

p_max = {'mu': 37000, 'sigma': 7500}
dk = {'23': {'min': 0, 'max': 99},
      '22': {'min': 100, 'max': 249},
      '55': {'min': 250, 'max': 953}}
br = {'min': 0, 'max': 1}

# Policy characteristics ---------------------------------------------
# Fixed e_max
levels = linspace(.1, .9, 9)

e_max = {round(levels[i], 1): round(v, 1) for i, v in enumerate(reversed(linspace(.1, .9, 9)))}
# Tax
tax = {round(levels[i], 1): round(v, 4) for i, v in enumerate(linspace(0, .03, 9))}
# Support green vehicles sales -- 'rebate'
p_d = {round(levels[i], 1): round(v, 3) for i, v in enumerate(reversed(linspace(0, .125, 9)))}

freight = {'co': {'co': 143, 'ne': 440, 'n': 44, 'se': 232, 's': 273},
           'ne': {'co': 440, 'ne': 154, 'n': 44, 'se': 386, 's': 573},
           'n': {'co': 441, 'ne': 709, 'n': 44, 'se': 602, 's': 642},
           'se': {'co': 232, 'ne': 386, 'n': 44, 'se': 96, 's': 208},
           's': {'co': 273, 'ne': 573, 'n': 44, 'se': 208, 's': 84}}


def discount_tax_table(e_bench, my_e):
    # e_bench é o valor geral no periodo anterior, my_e é o da firma
    # Also notice that given that no cars are sold (given market restrictions, emissions are 0)
    e = my_e/e_bench if e_bench > 0 else 0
    # Parameter support table to get discount or tax increase values
    intervals = [.7, .85, .95, 1, 1.05, 1.15, 1.3, 1.5]
    values = [-1, -.75, -.5, -.25, 0, .25, .5, .75, 1]
    index = bisect.bisect_left(intervals, e)
    return values[index]
