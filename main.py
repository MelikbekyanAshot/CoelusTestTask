"""Main script"""
from src.solution import Solution

if __name__ == '__main__':
    while True:
        table_width, table_height = map(int, input('Enter table\'s width and height: ').split())
        table_size = (table_width, table_height)

        rectangle_type_amount = int(input('Enter total rectangles type amount: '))
        rectangle_shapes_raw = [map(int, input('Enter width, height and amount of rectangles: ').split())
                                for _ in range(rectangle_type_amount)]
        rectangle_shapes = [(w, h) for w, h, k in rectangle_shapes_raw for _ in range(k)]

        p_polyomino_type_amount = int(input('Enter total p-polyominoes type amount: '))
        p_polyominoes_raw = [map(int, input('Enter width, height and amount of p-polyominoes: ').split())
                             for _ in range(p_polyomino_type_amount)]
        p_polyomino_shapes = [(h, w) for w, h, k in p_polyominoes_raw for _ in range(k)]
        print(
            f'You entered:\ntable size: {table_size}\nrectangles: {rectangle_shapes}\np-polyominoes: {p_polyomino_shapes}')
        s = Solution(table_size, rectangle_shapes, p_polyomino_shapes)
        if s.solve():
            print('Solution is found!')
        else:
            print('Solution is not found!')
