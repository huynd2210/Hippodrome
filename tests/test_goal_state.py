
import pytest
from hippodrome_solver import is_goal_state, string_to_board

instantiation_count = 0

@pytest.fixture(scope="module")
def solver():
    """
    This fixture is not used by the tests in this module, but it is included
    to demonstrate how a single solver instance could be reused across tests.
    """
    global instantiation_count
    instantiation_count += 1
    return None

def test_goal_state_success(solver):
    """
    Tests a board configuration that is a valid goal state.
    """
    board_str = "NNNN            "
    board = string_to_board(board_str)
    assert is_goal_state(board)

def test_goal_state_failure_fewer_than_four_Ns(solver):
    """
    Tests a board configuration that is not a valid goal state because it has
    fewer than four 'N's in the first row.
    """
    board_str = "NNN             "
    board = string_to_board(board_str)
    assert not is_goal_state(board)

def test_goal_state_failure_Ns_in_other_rows(solver):
    """
    Tests a board configuration that is not a valid goal state because the
    'N's are scattered across other rows.
    """
    board_str = "N  N  N  N      "
    board = string_to_board(board_str)
    assert not is_goal_state(board)

def test_single_solver_instance(solver):
    """
    Tests that only a single solver instance is created.
    """
    assert instantiation_count == 1

