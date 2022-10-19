import sys
from typing import Tuple, List
from ortools.sat.python import cp_model
import numpy as np
import more_itertools as mit
import matplotlib.pyplot as plt
import random


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """ Plot a solution. """

    def __init__(self, variables, width, height, rectangle_sizes, p_sizes):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.count = 0
        self.width = width
        self.height = height
        self.rectangle_sizes = rectangle_sizes
        self.p_sizes = p_sizes

    def on_solution_callback(self):
        labels = np.arange(len(self.rectangle_sizes) + len(self.p_sizes))  # Label of each polyomino
        colors = ['#' + ''.join(random.choices('0123456789abcdef', k=6)) for _ in range(len(labels))]
        cdict = dict(zip(labels, colors))  # Color dictionary for plotting
        self.count += 1
        plt.figure(figsize=(2, 2))
        plt.grid(True)
        plt.axis([0, self.width, self.height, 0])
        plt.yticks(np.arange(0, self.height, 1.0))
        plt.xticks(np.arange(0, self.width, 1.0))

        for i, p in enumerate(self.variables):
            for c in p:
                x = self.Value(c[0])
                y = self.Value(c[1])
                rect = plt.Rectangle((x, y), 1, 1, fc=cdict[i])
                plt.gca().add_patch(rect)
        plt.show()


class Solution:
    def __init__(self, model, table_size, rectangle_shapes):
        self.model = model
        self.rectangle_shapes = rectangle_shapes
        self.table_size = table_size

    def add_rectangle(self, polyomino, h, w):
        X, Y = 0, 1
        for p in polyomino:
            self.model.Add(p[Y] < polyomino[0][Y] + h)
            self.model.Add(p[X] < polyomino[0][X] + w)
            self.model.Add(p[Y] >= polyomino[0][Y])
            self.model.Add(p[X] >= polyomino[0][X])

    def solve(self):
        rectangle_sizes = [w * h for w, h in self.rectangle_shapes]
        W, H = self.table_size
        active_cells = set(np.arange(W * H))  # Cells where polyominoes can be fitted
        ranges = [(next(g), list(g)[-1]) for g in
                  mit.consecutive_groups(active_cells)]  # All intervals in the stack of active cells
        pminos = [[] for s in self.rectangle_shapes]
        for idx, s in enumerate(rectangle_sizes):
            for i in range(s):
                pminos[idx].append([self.model.NewIntVar(0, W - 1, 'p%i' % idx + 'c%i' % i + 'x'),
                                    self.model.NewIntVar(0, H - 1, 'p%i' % idx + 'c%i' % i + 'y')])

        for (h, w), pmino in zip(self.rectangle_shapes, pminos):
            self.add_rectangle(pmino, h, w)

        # No blocks can overlap:
        block_addresses = []
        n = 0
        for p in pminos:
            for c in p:
                n += 1
                block_address = self.model.NewIntVarFromDomain(cp_model.Domain.FromIntervals(ranges), '%i' % n)
                self.model.Add(c[0] + c[1] * W == block_address)
                block_addresses.append(block_address)

        self.model.AddAllDifferent(block_addresses)

        # Solve and print solutions as we find them
        solver = cp_model.CpSolver()

        solution_printer = SolutionPrinter(pminos, W, H, rectangle_sizes, [])
        status = solver.Solve(self.model, solution_printer)

        print('Status = %s' % solver.StatusName(status))
        print('Number of solutions found: %i' % solution_printer.count)


if __name__ == '__main__':
    model = cp_model.CpModel()
    table_size = (10, 8)
    rectangle_sizes = [(4, 5), (1, 5), (4, 2), (1, 1), (2, 6)]
    s = Solution(model, table_size, rectangle_sizes)
    s.solve()
