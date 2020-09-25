import matplotlib.pyplot as plt
from numpy import linspace
import pandas as pd
import time

import model

# 1. Emissions index
# 2. Green market-share
# 3. Public expenditure
# 4. New firms market-share

# Generalization guidelines
notes = {'green_market_share': ['Green market percentage (%)', 'yellowgreen'],
         'new_firms_share': ['Share of new firms (%)', 'dimgrey'],
         'emissions_index': ['Emissions index', 'darkblue'],
         'public_cumulative': ['Total public expenditure index', 'firebrick']}
policies_titles = {None: ['Benchmark', 'black'],
                   'tax': ['Tax scheme', 'firebrick'],
                   'discount': ['Discount', 'yellowgreen'],
                   'green_support': ['Green support', 'green'],
                   'max_e': ["Restriction on cars' emissions", 'dimgrey']}
verbose = True
seed = False


def processing_averages(pol_results):
    # Receives a specific policy dictionary of results of runs and processes the averages
    averages = dict()
    cols = ['green_market_share', 'new_firms_share', 'emissions_index', 'public_cumulative']
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
        plt.show()
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
        plt.show()
    return results


def policies(n=10):
    levels = [round(lev, 1) for lev in linspace(.1, .9, 9)]
    pols = [None, 'tax', 'discount', 'green_support', 'max_e']
    results = dict()
    for pol in pols:
        results[pol] = dict()
        for level in levels:
            p = {'policy': pol, 'level': level}
            # For each run policy, when dictionary with all runs is saved.
            # Thus, result collected is a dictionary of dictionaries containing DataFrames
            results[pol][level] = dict()
            for i in range(n):
                s = model.main(p, verbose, seed=seed)
                results[pol][level][i] = s.report.loc[39]
    return results, levels, n


def benchmark(n=10):
    pol, level = None, None
    p = {'policy': None, 'level': None}
    # For each run policy, when dictionary with all runs is saved.
    # Thus, result collected is a dictionary of dictionaries containing DataFrames
    results = {pol: dict()}
    for i in range(n):
        s = model.main(p, verbose, seed=seed)
        results[pol][i] = s.report
    plotting(results, n)


if __name__ == '__main__':
    t0 = time.time()
    m = 3
    benchmark(m)
    # r, l, m = policies(m)
    # plot_policies(r, l, m)
    print(f'This run took {time.time() - t0:.2f} seconds!')
