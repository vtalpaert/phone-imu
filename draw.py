# dependencies
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style='darkgrid')  # seaborn style one of darkgrid, whitegrid, dark, white, ticks


def plot(x_y_pairs, legend=None, fig=0, block=False, title=''):
    plt.figure(fig)
    for x, y in x_y_pairs:
        plt.plot(x, y)
    if title:
        plt.title(title)
    if legend:
        plt.legend(legend)
    plt.xlabel('timestamp')
    plt.ylabel('value')
    plt.show(block=block)


def plot_time_series(data, fig=1, xlabel='', ylabel='', title=''):
    df = pd.DataFrame(data, columns = ['index', 'value', 'legend'])
    df = df.set_index(df.index)
    print(df)
    plt.figure(fig)
    sns.lineplot(x='index', y='value', hue='legend', data=df)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    if title:
        plt.title(title)
    plt.show(block=True)

if __name__ == "__main__":
    # this is a demo not a proper test
    x = list(range(100))
    y = [t % 50 for t in x]
    x2 = list(range(0, 100, 2))
    y2 = [t % 20 for t in x2]
    x_y_pairs = [(x, y), (x2, y2)]
    plot(x_y_pairs, legend=('1', '2'), block=False, title='Test')

    data = {
        'index': [1, 1, 1, 4, 5, 4],
        'value': [0, 10, 11, 5, 4, 4],
        'legend': ['first', 'first', 'second', 'first', 'second', 'first']
    }
    plot_time_series(data, xlabel='timestamp', title='Another test with confidence interval')
