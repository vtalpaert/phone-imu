# dependencies
import numpy as np
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


if __name__ == "__main__":
    # this is a demo not a proper test
    x = list(range(100))
    y = [t % 50 for t in x]
    x2 = list(range(0, 100, 2))
    y2 = [t % 20 for t in x2]
    x_y_pairs = [(x, y), (x2, y2)]
    plot(x_y_pairs, legend=('1', '2'), block=True, title='Test')
