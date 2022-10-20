"""Script for plotting solution."""
import numpy as np
import matplotlib.pyplot as plt
import random
from ortools.sat.python import cp_model


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """ Plots solution. """
    def __init__(self, variables, width, height, rectangle_sizes, p_sizes):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.count = 0
        self.width = width
        self.height = height
        self.rectangle_sizes = rectangle_sizes
        self.p_sizes = p_sizes

    def on_solution_callback(self):
        """Plots solution of tiling task."""
        labels = np.arange(len(self.rectangle_sizes) + len(self.p_sizes))  # Label of each polyomino
        colors = ['#' + ''.join(random.choices('0123456789abcdef', k=6)) for _ in range(len(labels))]
        cdict = dict(zip(labels, colors))  # Color dictionary for plotting
        self.count += 1
        plt.figure(figsize=(2, 2))
        plt.title('Solution')
        plt.grid(True)
        plt.axis([0, self.width, self.height, 0])
        plt.yticks(np.arange(0, self.height, 1.0))
        plt.xticks(np.arange(0, self.width, 1.0))

        for i, p in enumerate(self.variables):
            for c in p:
                rect = plt.Rectangle((self.Value(c[0]), self.Value(c[1])), 1, 1, fc=cdict[i])
                plt.gca().add_patch(rect)
        plt.show()
