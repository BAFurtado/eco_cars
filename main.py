import datetime
import json
import os
import time

import matplotlib.pyplot as plt
import pandas as pd
from joblib import Parallel, delayed
from numpy import linspace

import model

# 1. Emissions index
# 2. Green market-share
# 3. Public expenditure
# 4. New firms market-share

# Generalization guidelines
notes = {'green_market_share': ['Green market percentage (%)', 'yellowgreen'],
         'new_firms_share': ['Share of new firms (%)', 'dimgrey'],
         'emissions_index': ['Emissions index', 'darkblue'],
         'public': ['Annual public expenditure', 'firebrick']}
policies_titles = {None: ['Baseline', 'black'],
                   'tax': ['Tax scheme', 'firebrick'],
                   'p_d': ['P&D cashback', 'green'],
                   'e_max': ["Restriction on cars' emissions", 'dimgrey']}
verbose = False
seed = False


def processing_averages(pol_results):
    # Receives a specific policy dictionary of results of runs and processes the averages
    averages = dict()
    # cols = ['green_market_share', 'new_firms_share', 'emissions_index', 'public_cumulative']
    cols = ['green_market_share', 'new_firms_share', 'emissions_index']
    for col in cols:
        averages[col] = pd.DataFrame()
    for run in pol_results:
        for col in cols:
            averages[col].loc[:, run] = pol_results[run][col]
    for col in cols:
        averages[col] = averages[col].mean(axis=1)
    return averages


def plot_details(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    # ax.yaxis.set_major_formatter(plt.FuncFormatter('{:.0f}'.format))
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.tick_params(axis='both', which='both', bottom=False, top=False,
                    labelbottom=True, left=False, right=False, labelleft=True)
    return ax


def plotting(results, n):
    """ This function has been deprecated. None run is included above"""
    # Receives a dictionary of results for policies and inside Ts runs with DataFrame reports
    for pol in results:
        res = processing_averages(results[pol])
        fig, ax = plt.subplots()
        for key in res:
            ax.plot(res[key].index, res[key], label=notes[key][0], color=notes[key][1])
        ax.legend(frameon=False)
        ax = plot_details(ax)
        ax.set(xlabel='T periods', ylabel='value',
               title=f'Results after {n} runs using policy: {policies_titles[pol][0]}')
        plt.savefig(f'results/{pol}.png', bbox_inches='tight')
        # plt.show()
    return res


def plot_policies(results, levels, n):
    # Receives a dictionary of results for policies
    # Each with all 9 levels
    # Each witn an 'n' number of runs
    # Inside each run, a DataFrame with reported results
    for graph in notes:
        fig, ax = plt.subplots()
        benchmark_values = list()
        for pol in policies_titles:
            x_s, y_s = list(), list()
            for i, level in enumerate(levels):
                x_s.append(level)
                # Calculate values for graph relative to benchmark and add to list
                y_output = sum([results[pol][level][key].loc[graph] for key in results[pol][level]]) / n
                if pol is None:
                    benchmark_values.append(y_output)
                else:
                    y_output = y_output/benchmark_values[i] if benchmark_values[i] != 0 else 0
                y_s.append(y_output)
            # Plot each policy line
            if pol is None:
                y_s = [b / b if b != 0 else 1 for b in benchmark_values]
            ax.plot(x_s, y_s, label=policies_titles[pol][0], color=policies_titles[pol][1])
        # Finish touches
        ax.legend(frameon=False)
        ax = plot_details(ax)
        ax.set(xlabel='Policy strength', ylabel='value', title=f'Results for {notes[graph][0]} after {n} runs')
        plt.savefig(f'policy_stringent_figures/{graph}.png', bbox_inches='tight')
        # plt.show()
    return results


def policies(path, timestamp, n=10, n_jobs=1, save=None, param=None, value=None):
    levels = [round(lev, 1) for lev in linspace(0, 1, 10)]
    pols = [None, 'tax', 'p_d', 'e_max']

    if not os.path.exists(path):
        os.mkdir(path)
    fullpath = os.path.join(path, timestamp)
    if save:
        os.mkdir(fullpath)

    # A dictionary of general results
    results = dict()
    for pol in pols:
        # A dictionary for each policy results
        results[pol] = dict()
        # Run for all levels specified
        for level in levels:
            p = {'policy': pol, 'level': level}
            # For each run policy, when dictionary with all runs is saved.
            # Thus, result collected is a dictionary of dictionaries containing DataFrames
            results[pol][level] = dict()
            # Run in parallel is the number of repetitions per level
            with Parallel(n_jobs=n_jobs) as parallel:
                s = parallel(delayed(model.main)(p, verbose, seed, param, value) for i in range(n))
                for i in range(n):
                    results[pol][level][i] = s[i].report.loc[39]
                    if save:
                        s[i].report.to_csv(f'{fullpath}/{pol}_{level}_{i}.csv', sep=';', index=False)

            # for i in range(n):
            #     s = model.main(p, verbose, seed=seed)
            #     results[pol][level][i] = s.report.loc[39]
    return results, levels, n


def benchmark(n=10):
    """ This function has been deprecated. None run is included above"""
    pol, level = None, None
    p = {'policy': pol, 'level': level}
    # For each run policy, when dictionary with all runs is saved.
    # Thus, result collected is a dictionary of dictionaries containing DataFrames
    results = {pol: dict()}
    for i in range(n):
        s = model.main(p, verbose, seed=False)
        results[pol][i] = s.report
    plotting(results, n)


def save_results_as_json(path, results):
    if not os.path.exists(path):
        os.mkdir(path)
    timestamp = datetime.datetime.utcnow().isoformat().replace(':', '_')
    with open(os.path.join(path, f'{timestamp}.json'), 'w') as f:
        json.dump(results, f, default=str)


def sensitivity(parameter, min_value, max_value, n_intervals, _type, path, timestamp, n=10, n_jobs=1, save=None):
    values = linspace(min_value, max_value, n_intervals)

    for value in values:
        if _type == 'i':
            value = int(value)
        else:
            value = f'{value:.4f}'
            value = float(value)
        new_path = os.path.join(path, f'{parameter}={value}')
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        policies(new_path, timestamp, n, n_jobs, save, parameter, value)


if __name__ == '__main__':
    save_summary = True
    save_data = True
    p = r'output'
    t0 = time.time()
    m = 100
    # Number of cpus that will run simultaneously
    cpus = 8
    # benchmark(m)
    t = datetime.datetime.utcnow().isoformat().replace(':', '_')

    # paramaters_to_test = {'prob_adoption': {'min': .2, 'max': .3, 'interval': 3, '_type': 'f'},
    #                       'mu_max': {'min': .05, 'max': .2, 'interval': 4, '_type': 'f'},
    #                       'rd_min': {'min': 10000, 'max': 90000, 'interval': 5, '_type': 'i'},
    #                       'epsilon': {'min': .05, 'max': .2, 'interval': 3, '_type': 'f'},
    #                       'omega': {'min': .3, 'max': .7, 'interval': 3, '_type': 'f'},
    #                       'time_adoption': {'min': 5, 'max': 15, 'interval': 3, '_type': 'i'},
    #                       'lambda': {'min': .05, 'max': .35, 'interval': 3, '_type': 'f'},
    #                       'number_characteristics': {'min': 2, 'max': 5, 'interval': 4, '_type': 'i'}
    #                       }
    #
    # for param in paramaters_to_test:
    #     sensitivity(param, paramaters_to_test[param]['min'],
    #                 paramaters_to_test[param]['max'],
    #                 paramaters_to_test[param]['interval'],
    #                 paramaters_to_test[param]['_type'],
    #                 p, t, m, cpus, save_data)

    # IF SENSITIVITY, UNCHECK THE NEXT LINE
    # sensitivity('number_characteristics', 2, 5, 4, 'i', p, t, m, cpus, save_data)

    # OTHERWISE, UNCHECK NEXT THREE LINES
    r, l, m = policies(p, t, m, cpus, save_data)
    if save_summary:
        save_results_as_json(p, r)
    #
    plot_policies(r, l, m)
    print(f'This run took {time.time() - t0:.2f} seconds!')
