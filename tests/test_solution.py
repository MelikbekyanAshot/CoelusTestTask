"""Script for testing."""
import unittest
from src.solution import Solution


class TestSolution(unittest.TestCase):
    """Class for unit test."""
    def test_positive(self):
        """Positive case with possibility to fit polyominoes."""
        self.assertEqual(Solution(table_size=(6, 6),
                                  rectangle_shapes=[(2, 2), (2, 2)],
                                  p_shapes=[(3, 4), (2, 3)]).solve(plot_solution=False),
                         True)

    def test_negative(self):
        """Negative case with no possibility to fit polyominoes."""
        self.assertEqual(Solution(table_size=(4, 4),
                                  rectangle_shapes=[(2, 5)],
                                  p_shapes=[(2, 3)]).solve(plot_solution=False),
                         False)

    def test_not_enough_area(self):
        """Case with not enough area to place polyominoes in."""
        self.assertEqual(Solution(table_size=(3, 3),
                                  rectangle_shapes=[(2, 2), (2, 2)],
                                  p_shapes=[(3, 4), (2, 3)]).solve(plot_solution=False),
                         False)

    def test_only_rectangles(self):
        """Case without p-polyominoes."""
        self.assertEqual(Solution(table_size=(4, 6),
                                  rectangle_shapes=[(4, 2), (2, 2), (4, 2), (2, 2)],
                                  p_shapes=[]).solve(plot_solution=False),
                         True)

    def test_only_p_polyominoes(self):
        """Case without rectangles."""
        self.assertEqual(Solution(table_size=(4, 6),
                                  rectangle_shapes=[],
                                  p_shapes=[(4, 3), (3, 2)]).solve(plot_solution=False),
                         True)


if __name__ == "__main__":
    unittest.main()
