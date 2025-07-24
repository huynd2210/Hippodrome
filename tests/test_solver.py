import pytest
from hippodrome_solver import HippodromeSolver

def test_simple_board():
    solver = HippodromeSolver('RRBBNNNN')
    solution = solver.solve()
    assert solution is not None

def test_complex_board():
    solver = HippodromeSolver('RRBQRBRBQBKNNNN')
    solution = solver.solve()
    assert solution is not None

