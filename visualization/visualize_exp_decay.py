import numpy as np
import matplotlib.pyplot as plt
from typing import Sequence


def visualize_exp_decay(x_range: tuple[float, float] = (0.0, 1.0),
                        num_points: int = 400,
                        a_values: Sequence[float] = (2.0, 5.0),
                        title: str = 'Visualization of y = exp(-ax)',
                        xlabel: str = 'x',
                        ylabel: str = 'y = exp(-ax)',
                        figsize: tuple[int, int] = (8, 6),
                        grid: bool = True):
    """
    Visualizes the function y = exp(-ax) for different values of 'a'.

    Args:
        x_range: A tuple specifying the start and end of the x-axis range (default: (0.0, 1.0)).
        num_points: The number of points to generate within the x-range for plotting (default: 400).
        a_values: A sequence (like a list or tuple) of 'a' values to plot (default: (2.0, 5.0)).
        title: The title of the plot (default: 'Visualization of y = exp(-ax)').
        xlabel: The label for the x-axis (default: 'x').
        ylabel: The label for the y-axis (default: 'y = exp(-ax)').
        figsize: A tuple specifying the width and height of the figure in inches (default: (8, 6)).
        grid: A boolean indicating whether to display a grid on the plot (default: True).
    """
    start_x, end_x = x_range
    x = np.linspace(start_x, end_x, num_points)

    plt.figure(figsize=figsize)

    for a in a_values:
        y = np.exp(-a * x)
        plt.plot(x, y, label=f'a = {a}')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    if grid:
        plt.grid(True)
    plt.show()


if __name__ == '__main__':
    visualize_exp_decay(x_range=(0.0, 0.2),
                        num_points=200,
                        a_values=[2.0, 5.0, 10.0],
                        )
