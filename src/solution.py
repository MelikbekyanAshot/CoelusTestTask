"""Script contains tiling task solution."""
from typing import Tuple, List
import itertools
import warnings
import numpy as np
import more_itertools as mit
from ortools.sat.python import cp_model
from src.solution_printer import SolutionPrinter

warnings.filterwarnings("ignore", category=UserWarning)


class Solution:
    """Implements algorithm of tiling task solution with CP-SAT.
    Attributes:
        model (cp_model.CpModel): model used for task solution.
        table_size (Tuple[int, int]): width and height of table.
        rectangle_shapes (List[Tuple[int, int]]): """

    def __init__(self, table_size: Tuple[int, int], rectangle_shapes: List[Tuple[int, int]]):
        self.model = cp_model.CpModel()
        self.table_size = table_size
        self.rectangle_shapes = rectangle_shapes

    def solve(self):
        """Iterates through all possible rectangle rotations to find solution."""
        if not self.__check_area_compatibility():
            return False
        all_rect_shape_combinations = [list(itertools.permutations(rectangle_size))
                                       for rectangle_size in self.rectangle_shapes]
        all_rect_shape_combinations = list(itertools.product(*all_rect_shape_combinations))
        for rect_shape in all_rect_shape_combinations:
            if self.__find_solution(rect_shape):
                return True
        return False

    def __check_area_compatibility(self):
        """Checks if table area is enough to pack all rectangles in it.
        Improves execution time for impossible cases.

        Returns:
            bool: True if there is enough area for all figures, False otherwise."""
        total_area = self.table_size[0] * self.table_size[1]
        rectangles_area = sum(width * height for width, height in self.rectangle_shapes)
        return total_area >= rectangles_area

    def __find_solution(self, rectangle_shapes) -> bool:
        """Tries to find tiling problem solution with defined rectangle's shapes.
        Args:
            rectangle_shapes (Tuple[Tuple[int, int]]):
        Returns:
            bool: True if there is a task solution, False otherwise."""
        rectangle_sizes = [rectangle_width * rectangle_height
                           for (rectangle_width, rectangle_height) in rectangle_shapes]
        table_width, table_height = self.table_size

        # Create rectangles with defined shape
        polyominoes = [[] for s in rectangle_shapes]
        for idx, size in enumerate(rectangle_sizes):
            for i in range(size):
                polyominoes[idx].append([self.model.NewIntVar(0, table_width - 1, f'p{i}c{i}x'),
                                         self.model.NewIntVar(0, table_height - 1, f'p{i}c{i}y')])

        for (rectangle_width, rectangle_height), polyomino in zip(rectangle_shapes, polyominoes):
            self.__add_rectangle(polyomino, rectangle_width, rectangle_height)

        # No blocks can overlap
        active_cells = set(np.arange(table_width * table_height))  # Cells where polyominoes can be fitted
        ranges = [(next(g), list(g)[-1]) for g in
                  mit.consecutive_groups(active_cells)]  # All intervals in the stack of active cells
        block_addresses = []
        for index, polyomino in enumerate(polyominoes):
            for cell in polyomino:
                block_address = self.model.NewIntVarFromDomain(
                    cp_model.Domain.FromIntervals(ranges), f'{index}')
                self.model.Add(cell[0] + cell[1] * table_width == block_address)
                block_addresses.append(block_address)

        self.model.AddAllDifferent(block_addresses)

        # Solve tiling problem
        solver = cp_model.CpSolver()
        solution_printer = SolutionPrinter(polyominoes,
                                           table_width, table_height,
                                           rectangle_sizes, [])
        status = solver.Solve(self.model, solution_printer)
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return True
        return False

    def __add_rectangle(self, polyomino: List, rectangle_height: int, rectangle_width: int) -> None:
        """Adds constraint with rectangle shape to model.
        Args:
            polyomino (List[cp_model.IntVar]): list of cp_model.IntVar's objects.
            rectangle_height (int): height of rectangle.
            rectangle_width (int): width of rectangle."""
        for cell in polyomino:
            self.model.Add(cell[1] < polyomino[0][1] + rectangle_width)
            self.model.Add(cell[0] < polyomino[0][0] + rectangle_height)
            self.model.Add(cell[1] >= polyomino[0][1])
            self.model.Add(cell[0] >= polyomino[0][0])
