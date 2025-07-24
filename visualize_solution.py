#!/usr/bin/env python3
"""
Hippodrome Solution Visualizer
Reads solution CSV and visualizes the board states step by step
"""

import csv
import sys
import time
from typing import List, Optional

def print_board(board_state: str, step_num: int = None, total_steps: int = None) -> None:
    """
    Print a visual representation of the 4x4 board
    
    Args:
        board_state: 16-character string representing the board
        step_num: Current step number (optional)
        total_steps: Total number of steps (optional)
    """
    if len(board_state) != 16:
        print(f"Error: Board state must be 16 characters, got {len(board_state)}")
        return
    
    # Print step header if provided
    if step_num is not None and total_steps is not None:
        print(f"\n=== Step {step_num}/{total_steps} ===")
    elif step_num is not None:
        print(f"\n=== Step {step_num} ===")
    
    print("┌───┬───┬───┬───┐")
    for row in range(4):
        print("│", end="")
        for col in range(4):
            char = board_state[row * 4 + col]
            # Replace 'x' with space for better visualization
            display_char = ' ' if char == 'x' else char
            print(f" {display_char} │", end="")
        print()
        
        if row < 3:
            print("├───┼───┼───┼───┤")
        else:
            print("└───┴───┴───┴───┘")

def parse_solution_path(solution_path: str) -> List[str]:
    """
    Parse the solution path string into individual board states
    
    Args:
        solution_path: Semicolon-separated board states
        
    Returns:
        List of board state strings
    """
    if not solution_path or solution_path.strip() == "":
        return []
    
    return [state.strip() for state in solution_path.split(';') if state.strip()]

def visualize_solution(config_id: int, initial_board: str, solution_path: str, 
                      moves: int, time_ms: float, interactive: bool = True) -> None:
    """
    Visualize a complete solution step by step
    
    Args:
        config_id: Configuration ID
        initial_board: Initial board state
        solution_path: Complete solution path
        moves: Number of moves
        time_ms: Time taken to solve
        interactive: Whether to wait for user input between steps
    """
    print(f"\n{'='*60}")
    print(f"SOLUTION VISUALIZATION - Config ID: {config_id}")
    print(f"Moves: {moves} | Time: {time_ms:.2f}ms")
    print(f"{'='*60}")
    
    # Parse the solution path
    board_states = parse_solution_path(solution_path)
    
    if not board_states:
        print("No solution path found!")
        return
    
    total_steps = len(board_states)
    
    # Show each step
    for i, board_state in enumerate(board_states):
        step_num = i + 1
        print_board(board_state, step_num, total_steps)
        
        # Show goal achievement
        if board_state.startswith("NNNN"):
            print("\n🎉 GOAL ACHIEVED! All knights are in the top row!")
        
        # Interactive mode - wait for user input
        if interactive and i < total_steps - 1:
            user_input = input("\nPress Enter for next step, 'q' to quit, 'a' for auto-play: ").strip().lower()
            if user_input == 'q':
                print("Visualization stopped by user.")
                return
            elif user_input == 'a':
                interactive = False
                print("Switching to auto-play mode...")
        elif not interactive and i < total_steps - 1:
            time.sleep(0.5)  # Auto-play delay
    
    print(f"\n✅ Solution complete! Solved in {moves} moves.")

def load_and_visualize_solutions(csv_file: str, config_id: Optional[int] = None) -> None:
    """
    Load solutions from CSV and visualize them
    
    Args:
        csv_file: Path to the CSV file
        config_id: Specific config ID to visualize (None for all)
    """
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            solutions_found = False
            
            for row in reader:
                row_id = int(row['ID'])
                
                # Skip if specific config requested and this isn't it
                if config_id is not None and row_id != config_id:
                    continue
                
                solutions_found = True
                initial_board = row['Initial Board']
                solution_path = row['Solution Path']
                moves = int(row['Moves']) if row['Moves'] != '-1' else 0
                time_ms = float(row['Time (ms)'])
                
                # Check if solution exists
                if moves <= 0 or not solution_path:
                    print(f"\nConfig ID {row_id}: No solution found")
                    continue
                
                # Visualize this solution
                visualize_solution(row_id, initial_board, solution_path, moves, time_ms)
                
                # Ask if user wants to continue to next solution
                if config_id is None:
                    user_input = input("\nVisualize next solution? (y/n/q): ").strip().lower()
                    if user_input in ['n', 'q']:
                        break
            
            if not solutions_found:
                if config_id is not None:
                    print(f"No solution found for config ID {config_id}")
                else:
                    print("No solutions found in the CSV file")
                    
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found!")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def main():
    """Main function"""
    print("🏇 Hippodrome Solution Visualizer 🏇")
    print("=" * 40)
    
    # Default CSV file
    csv_file = "solutions_csv/first_5_solutions.csv"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    config_id = None
    if len(sys.argv) > 2:
        try:
            config_id = int(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid config ID '{sys.argv[2]}'. Must be an integer.")
            return
    
    print(f"Reading solutions from: {csv_file}")
    if config_id is not None:
        print(f"Showing only config ID: {config_id}")
    
    load_and_visualize_solutions(csv_file, config_id)

if __name__ == "__main__":
    main() 