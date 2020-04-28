# python base modules
from collections import deque

# dependencies
from gevent import time
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


class LivePlot:
    # from https://stackoverflow.com/a/40139416

    def __init__(
            self,
            xsize = 100,
            n_values=1,
            blit = True,
            fig=2,
            title='',
            xlabel='',
            ylabel='',
            show_frame_rate = True,
            ylim_low = -12,
            ylim_high = 12):
        """blit is the fastest
        """
        self.blit, self.frame_rate, self.n_values = blit, show_frame_rate, n_values
        self.x = np.array(list(range(xsize)))
        self.fig = plt.figure(fig)
        self.ax = self.fig.add_subplot(1, 1, 1, label="main")
        self.values = {}
        for i in range(n_values):
            self.values[i] = {'y': deque(xsize*[0], maxlen=xsize)}
            self.values[i]['line'], = self.ax.plot([], lw=3)
        if self.frame_rate:
            self.text = self.ax.text(0.8,0.5, "")

        self.ax.set_xlim(self.x.min(), self.x.max())
        self.ax.set_ylim([ylim_low, ylim_high])

        self.fig.canvas.draw()   # note that the first draw comes before setting data

        if self.blit:
            # cache the background
            self.axbackground = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show(block=False)
        self.t_start = time.time()
        self.i = 0

    def update(self, values):
        for i, value in zip(range(self.n_values), values):
            self.values[i]['y'].append(value)

    def draw(self):
        for i in range(self.n_values):
            self.values[i]['line'].set_data(self.x, np.array(self.values[i]['y']))
        if self.frame_rate:
            tx = 'Mean Frame Rate:\n {fps:.3f}FPS'.format(fps= ((self.i+1) / (time.time() - self.t_start)) ) 
            self.text.set_text(tx)
        if self.blit:
            # restore background
            self.fig.canvas.restore_region(self.axbackground)
            # redraw just the points
            for i in range(self.n_values):
                self.ax.draw_artist(self.values[i]['line'])
            if self.frame_rate:
                self.ax.draw_artist(self.text)
            # fill in the axes rectangle
            self.fig.canvas.blit(self.ax.bbox)
        else:
            # redraw everything
            self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        #alternatively you could use
        #plt.pause(0.000000000001) 
        # however plt.pause calls canvas.draw(), as can be read here:
        #http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
        self.i += 1

    def close(self):
        plt.close(self.fig)


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
