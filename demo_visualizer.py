#!/usr/bin/env python3
"""
Demo script for the Hippodrome Solution Visualizer
Shows the first few steps of a solution automatically
"""

import csv
import time
from visualize_solution import print_board, parse_solution_path

def demo_solution(csv_file: str, config_id: int, max_steps: int = 5):
    """
    Demo a solution by showing the first few steps automatically
    
    Args:
        csv_file: Path to the CSV file
        config_id: Configuration ID to demo
        max_steps: Maximum number of steps to show
    """
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                if int(row['ID']) == config_id:
                    initial_board = row['Initial Board']
                    solution_path = row['Solution Path']
                    moves = int(row['Moves']) if row['Moves'] != '-1' else 0
                    time_ms = float(row['Time (ms)'])
                    
                    print(f"🏇 DEMO: Hippodrome Solution Visualizer 🏇")
                    print(f"{'='*50}")
                    print(f"Config ID: {config_id}")
                    print(f"Total Moves: {moves}")
                    print(f"Solve Time: {time_ms:.2f}ms")
                    print(f"Showing first {max_steps} steps...")
                    print(f"{'='*50}")
                    
                    # Parse solution
                    board_states = parse_solution_path(solution_path)
                    
                    # Show first few steps
                    for i, board_state in enumerate(board_states[:max_steps]):
                        step_num = i + 1
                        print_board(board_state, step_num, len(board_states))
                        
                        if board_state.startswith("NNNN"):
                            print("\n🎉 GOAL ACHIEVED! All knights are in the top row!")
                            break
                        
                        if i < min(max_steps - 1, len(board_states) - 1):
                            print("\n⏯️  Moving to next step...")
                            time.sleep(1.5)
                    
                    if len(board_states) > max_steps:
                        print(f"\n... and {len(board_states) - max_steps} more steps to complete the solution!")
                    
                    print("\n✨ Demo complete!")
                    print(f"💡 To see the full solution interactively, run:")
                    print(f"   python visualize_solution.py {csv_file} {config_id}")
                    
                    return
            
            print(f"Config ID {config_id} not found in {csv_file}")
            
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Demo the first solution
    demo_solution("solutions_csv/first_5_solutions.csv", 0, max_steps=5) 