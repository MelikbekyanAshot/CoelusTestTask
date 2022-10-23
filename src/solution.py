"""Script contains tiling task solution."""
from typing import Tuple, List
import itertools
import random
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
        rectangle_shapes (List[Tuple[int, int]]): shapes of given rectangles."""

    def __init__(self, table_size: Tuple[int, int],
                 rectangle_shapes: List[Tuple[int, int]], p_shapes: List[Tuple[int, int]]):
        self.model = cp_model.CpModel()
        self.table_size = table_size
        self.rectangle_shapes = rectangle_shapes
        self.p_shapes = p_shapes

    def solve(self, plot_solution: bool) -> bool:
        """Iterates through all possible rectangle rotations to find solution.
        Args:
            plot_solution (bool): defines if solution should be plotted.

        Returns:
            bool: True if there is any solution, False otherwise."""
        if not self.__check_area_compatibility():
            return False

        rect_shape_combinations = [list(itertools.permutations(rectangle_shape))
                                   for rectangle_shape in self.rectangle_shapes]
        rect_shape_combinations = set(itertools.product(*rect_shape_combinations))

        directions = ['top', 'left', 'right', 'bottom']
        directions = list(itertools.product(directions, repeat=len(self.p_shapes)))
        random.shuffle(directions)
        p_combinations = [tuple(zip(self.p_shapes, direction)) for direction in directions]
        for rect_shape in rect_shape_combinations:
            for p_comb in p_combinations:
                if self.__find_solution(rect_shape, p_comb, plot_solution):
                    return True
        return False

    def __check_area_compatibility(self):
        """Checks if table area is enough to pack all rectangles in it.
        Improves execution time for impossible cases.

        Returns:
            bool: True if there is enough area for all figures, False otherwise."""
        available_area = self.table_size[0] * self.table_size[1]
        rectangles_area = sum(width * height for width, height in self.rectangle_shapes)
        p_polyominoes_area = sum(
            (width * height) - (width - 2) * (height - 1) for width, height in self.p_shapes)
        return available_area >= rectangles_area + p_polyominoes_area

    def __find_solution(self, rectangle_shapes: Tuple[Tuple[int, int]],
                        p_polyomino_shapes: Tuple[Tuple[Tuple[int, int], str]],
                        plot_solution: bool) -> bool:
        """Tries to find tiling problem solution with defined rectangle's shapes.
        Args:
            rectangle_shapes (Tuple[Tuple[int, int]]):
            p_polyomino_shapes (Tuple[Tuple[Tuple[int, int], str]]):
            plot_solution (bool): defines if solution should be plotted.
        Returns:
            bool: True if there is a task solution, False otherwise."""
        table_width, table_height = self.table_size

        # Create rectangles with defined shape
        rectangle_areas = [rectangle_width * rectangle_height
                           for (rectangle_width, rectangle_height) in rectangle_shapes]
        rectangle_polyominoes = [[] for _ in rectangle_shapes]
        for idx, size in enumerate(rectangle_areas):
            for i in range(size):
                rectangle_polyominoes[idx] \
                    .append([self.model.NewIntVar(0, table_width - 1, f'r{i}c{i}x'),
                             self.model.NewIntVar(0, table_height - 1, f'r{i}c{i}y')])

        for (rectangle_width, rectangle_height), polyomino \
                in zip(rectangle_shapes, rectangle_polyominoes):
            self.__add_rectangle(polyomino, rectangle_width, rectangle_height)

        # Create p-polyomonoes with defined shape and direction
        p_polyomino_areas = [(width * height) - (height - 1) * (width - 2)
                             for (height, width), _ in list(p_polyomino_shapes)]
        p_polyominoes = [[] for _ in p_polyomino_shapes]
        for idx, size in enumerate(p_polyomino_areas):
            for i in range(size):
                p_polyominoes[idx] \
                    .append([self.model.NewIntVar(0, table_width - 1, f'p{i}c{i}x'),
                             self.model.NewIntVar(0, table_height - 1, f'p{i}c{i}y')])

        for ((p_height, p_width), direction), polyomino in zip(p_polyomino_shapes, p_polyominoes):
            self.__add_p_polyomino(polyomino, p_height, p_width, direction)

        # No blocks can overlap
        active_cells = set(np.arange(table_width * table_height))
        ranges = [(next(g), list(g)[-1]) for g in
                  mit.consecutive_groups(active_cells)]
        block_addresses = []
        all_polyominoes = p_polyominoes + rectangle_polyominoes

        for index, polyomino in enumerate(all_polyominoes):
            for cell in polyomino:
                block_address = self.model.NewIntVarFromDomain(
                    cp_model.Domain.FromIntervals(ranges), f'{index}')
                self.model.Add(cell[0] + cell[1] * table_width == block_address)
                block_addresses.append(block_address)

        self.model.AddAllDifferent(block_addresses)

        # Solve tiling problem
        solver = cp_model.CpSolver()
        if plot_solution:
            solution_printer = SolutionPrinter(all_polyominoes,
                                               table_width, table_height,
                                               rectangle_areas, p_polyomino_areas)
            status = solver.Solve(self.model, solution_printer)
        else:
            status = solver.Solve(self.model)
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return True
        return False

    def __add_rectangle(self, polyomino: List,
                        rectangle_height: int, rectangle_width: int) -> None:
        """Adds constraints of rectangle shape to model.
        Args:
            polyomino (List[cp_model.IntVar]): list of cp_model.IntVar objects.
            rectangle_height (int): height of rectangle.
            rectangle_width (int): width of rectangle."""
        for cell in polyomino:
            self.model.Add(cell[1] < polyomino[0][1] + rectangle_width)
            self.model.Add(cell[0] < polyomino[0][0] + rectangle_height)
            self.model.Add(cell[1] >= polyomino[0][1])
            self.model.Add(cell[0] >= polyomino[0][0])

    def __add_p_polyomino(self, polyomino: List[cp_model.IntVar],
                          p_polyomino_height: int, p_polyomino_width: int,
                          direction: str) -> None:
        """Adds constraints of p-polyomino shape to model.
        Args:
            polyomino (List[cp_model.IntVar]): list of cp_model.IntVar objects.
            p_polyomino_height (int): height of p-polyomino.
            p_polyomino_width (int): width of p-polyomino.
            direction (str): direction of p-polyomino's open area."""
        if direction in ['bottom', 'top']:
            self.__add_vertical_oriented_p_polyomino(polyomino,
                                                     p_polyomino_height, p_polyomino_width,
                                                     direction)
        elif direction in ['left', 'right']:
            self.__add_horizontal_oriented_p_polyomino(polyomino,
                                                       p_polyomino_height, p_polyomino_width,
                                                       direction)

    def __add_vertical_oriented_p_polyomino(self, polyomino: List,
                                            p_polyomino_height: int, p_polyomino_width: int,
                                            direction: str) -> None:
        """Adds constraints of vertical oriented p-polyomino shape to model.
        Args:
            polyomino (List[cp_model.IntVar]): list of cp_model.IntVar objects.
            p_polyomino_height (int): height of p-polyomino.
            p_polyomino_width (int): width of p-polyomino.
            direction (str): direction of p-polyomino's open area."""
        bias = 0 if direction == 'bottom' else p_polyomino_height - 1
        for cell in polyomino[1:p_polyomino_height]:
            self.model.Add(cell[0] == polyomino[0][0])
            self.model.Add(cell[1] < polyomino[0][1] + p_polyomino_height)
            self.model.Add(cell[1] >= polyomino[0][1])
        for cell in polyomino[p_polyomino_height:2 * p_polyomino_height]:
            self.model.Add(cell[0] == polyomino[0][0] + p_polyomino_width - 1)
            self.model.Add(cell[1] < polyomino[0][1] + p_polyomino_height)
            self.model.Add(cell[1] >= polyomino[0][1])
        for cell in polyomino[2 * p_polyomino_height:]:
            self.model.Add(cell[1] == polyomino[0][1] + bias)
            self.model.Add(cell[0] < polyomino[0][0] + p_polyomino_width)
            self.model.Add(cell[0] >= polyomino[0][0])

    def __add_horizontal_oriented_p_polyomino(self, polyomino: List,
                                              p_polyomino_height: int, p_polyomino_width: int,
                                              direction: str) -> None:
        """Adds constraints of horizontal oriented p-polyomino shape to model.
        Args:
            polyomino (List[cp_model.IntVar]): list of cp_model.IntVar objects.
            p_polyomino_height (int): height of p-polyomino.
            p_polyomino_width (int): width of p-polyomino.
            direction (str): direction of p-polyomino's open area."""
        bias = 0 if direction == 'right' else p_polyomino_height - 1
        for cell in polyomino[1:p_polyomino_height]:
            self.model.Add(cell[1] == polyomino[0][1])
            self.model.Add(cell[0] < polyomino[0][0] + p_polyomino_height)
            self.model.Add(cell[0] >= polyomino[0][0])
        for cell in polyomino[p_polyomino_height:2 * p_polyomino_height]:
            self.model.Add(cell[1] == polyomino[0][1] + p_polyomino_width - 1)
            self.model.Add(cell[0] < polyomino[0][0] + p_polyomino_height)
            self.model.Add(cell[0] >= polyomino[0][0])
        for cell in polyomino[2 * p_polyomino_height:]:
            self.model.Add(cell[0] == polyomino[0][0] + bias)
            self.model.Add(cell[1] < polyomino[0][1] + p_polyomino_width)
            self.model.Add(cell[1] >= polyomino[0][1])
