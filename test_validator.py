#!/usr/bin/env python3
"""
Test script for the solution validator
Creates known test cases and validates them
"""

from validate_solutions import SolutionValidator

def test_validator():
    """Test the validator with known cases"""
    print("🧪 Testing Solution Validator 🧪")
    print("=" * 40)
    
    validator = SolutionValidator()
    
    # Test 1: Valid simple move (King moves one square)
    print("\n1. Testing valid King move...")
    initial = "KBRKBRRKKRBxNNNN"  # King at position 0, empty at position 11
    next_board = "xBRKBRRKKRBKNNNN"  # King moves to position 11, empty at position 0
    
    is_valid, msg = validator.is_valid_move(initial, next_board)
    print(f"   Result: {'✅ PASS' if is_valid else '❌ FAIL'} - {msg}")
    
    # Test 2: Invalid move (piece jumps illegally)
    print("\n2. Testing invalid move (illegal jump)...")
    initial = "KBRKBRRKKRBxNNNN"
    invalid_next = "xBRKBRRKKRxKNNNN"  # King tries to jump multiple squares
    
    is_valid, msg = validator.is_valid_move(initial, invalid_next)
    print(f"   Result: {'✅ PASS' if not is_valid else '❌ FAIL'} - {msg}")
    
    # Test 3: Goal state detection
    print("\n3. Testing goal state detection...")
    goal_board = "NNNNxBRKBRRKKRRB"  # All knights in top row
    not_goal = "KBRKBRRKKRBxNNNN"   # Knights not in top row
    
    is_goal1 = validator.is_goal_state(goal_board)
    is_goal2 = validator.is_goal_state(not_goal)
    
    print(f"   Goal board: {'✅ PASS' if is_goal1 else '❌ FAIL'}")
    print(f"   Non-goal board: {'✅ PASS' if not is_goal2 else '❌ FAIL'}")
    
    # Test 4: Simple 2-step solution path
    print("\n4. Testing simple solution path...")
    initial = "KBRKBRRKKRBxNNNN"
    solution_path = "KBRKBRRKKRBxNNNN;KBRKBRRKKRxBNNNN;NNNNBRRKKRxBKBRK"
    
    is_valid, msg, stats = validator.validate_solution_path(initial, solution_path)
    print(f"   Result: {'✅ PASS' if is_valid else '❌ FAIL'} - {msg}")
    if stats:
        print(f"   Stats: {stats['moves_count']} moves, goal: {stats.get('goal_achieved', False)}")
    
    # Test 5: Piece movement validation
    print("\n5. Testing different piece movements...")
    
    # Rook horizontal move
    print("   5a. Rook horizontal move:")
    rook_test = validator.rook_moves(0, 0, 0, 3)
    print(f"       {'✅ PASS' if rook_test else '❌ FAIL'}")
    
    # Bishop diagonal move  
    print("   5b. Bishop diagonal move:")
    bishop_test = validator.bishop_moves(0, 0, 2, 2)
    print(f"       {'✅ PASS' if bishop_test else '❌ FAIL'}")
    
    # Knight L-shaped move
    print("   5c. Knight L-shaped move:")
    knight_test = validator.knight_moves(0, 0, 2, 1)
    print(f"       {'✅ PASS' if knight_test else '❌ FAIL'}")
    
    # King one-square move
    print("   5d. King one-square move:")
    king_test = validator.king_moves(0, 0, 1, 1)
    print(f"       {'✅ PASS' if king_test else '❌ FAIL'}")
    
    print(f"\n{'='*40}")
    print("🎯 Validator tests completed!")

if __name__ == "__main__":
    test_validator() 