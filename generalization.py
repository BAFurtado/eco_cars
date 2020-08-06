import matplotlib.pyplot as plt
import pandas as pd

import model


# Which figures do we want?
# Which data is necessary to save to produce those figures (everything related to benchmarket)?
# All data needs to be collected for all 'Ts'
# 1. EMISSIONS
# 2. Green market-share increase
# 3. Public income? (how to calculate net benefits)


def processing_averages(pol_results):
    # Receives a specific policy dictionary of results of runs and processes the averages
    averages = dict()
    cols = ['green_market_share', 'new_firms_share', 'emissions_index', 'public']
    for col in cols:
        averages[col] = pd.DataFrame()
    for run in pol_results:
        for col in cols:
            averages[col].loc[:, run] = pol_results[run][col]
    for col in cols:
        averages[col] = averages[col].mean(axis=1)
    return averages


def plotting(results):
    # Receives a dictionary of results for policies and inside Ts runs with DataFrame reports
    for pol in results:
        res = processing_averages(results[pol])
        fig, ax = plt.subplots()
        for key in res:
            ax.plot(res[key].index, res[key])
        plt.show()
    return res


def running(n=10):
    # Available policies are: 'max_e', 'tax', 'discount', 'green_support'
    # Available levels are: 'low' and 'high'
    pol, level = None, None
    # pol = 'green_support'
    # level = 'low'
    p = {'policy': pol, 'level': level}
    v = False
    # For each run policy, when dictionary with all runs is saved.
    # Thus, result collected is a dictionary of dictionaries containing DataFrames
    results = {pol: dict()}
    for i in range(n):
        s = model.main(p, v)
        results[pol][i] = s.report
    return results


if __name__ == '__main__':
    m = 2
    r = running(m)
    a = plotting(r)
