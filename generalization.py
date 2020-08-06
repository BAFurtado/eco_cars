import model

# Which figures do we want?
# Which data is necessary to save to produce those figures (everything related to benchmarket)?
# All data needs to be collected for all 'Ts'
# 1. EMISSIONS
# 2. Green market-share increase
# 3. Public income? (how to calculate net benefits)


def running(n=10):
    # Available policies are: 'max_e', 'tax', 'discount', 'green_support'
    # Available levels are: 'low' and 'high'
    pol, level = None, None
    # pol = 'green_support'
    # level = 'low'
    p = {'policy': pol, 'level': level}
    v = False
    for i in range(n):
        s = model.main(p, v)


if __name__ == '__main__':
    m = 10
    running(m)
