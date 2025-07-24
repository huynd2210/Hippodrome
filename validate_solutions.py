#!/usr/bin/env python3
"""
Hippodrome Solution Validator
Reads solution CSV files and validates the correctness of each solution
"""

import csv
import sys
from typing import List, Tuple, Dict, Optional

class SolutionValidator:
    def __init__(self):
        self.piece_moves = {
            'K': self.king_moves,    # King: one square in any direction
            'R': self.rook_moves,    # Rook: horizontal/vertical lines
            'B': self.bishop_moves,  # Bishop: diagonal lines
            'N': self.knight_moves   # Knight: L-shaped moves
        }
    
    def board_to_grid(self, board_str: str) -> List[List[str]]:
        """Convert 16-character string to 4x4 grid"""
        if len(board_str) != 16:
            raise ValueError(f"Board must be 16 characters, got {len(board_str)}")
        
        grid = []
        for row in range(4):
            grid.append(list(board_str[row*4:(row+1)*4]))
        return grid
    
    def grid_to_board(self, grid: List[List[str]]) -> str:
        """Convert 4x4 grid to 16-character string"""
        return ''.join(''.join(row) for row in grid)
    
    def find_empty_space(self, board_str: str) -> Tuple[int, int]:
        """Find the position of the empty space ('x')"""
        for i, char in enumerate(board_str):
            if char == 'x':
                return (i // 4, i % 4)
        raise ValueError("No empty space found in board")
    
    def find_piece_positions(self, board_str: str) -> Dict[str, List[Tuple[int, int]]]:
        """Find positions of all pieces on the board"""
        positions = {'K': [], 'R': [], 'B': [], 'N': [], 'x': []}
        
        for i, char in enumerate(board_str):
            if char in positions:
                row, col = i // 4, i % 4
                positions[char].append((row, col))
        
        return positions
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < 4 and 0 <= col < 4
    
    def king_moves(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """King moves one square in any direction"""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff) > 0
    
    def rook_moves(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Rook moves horizontally or vertically"""
        return from_row == to_row or from_col == to_col
    
    def bishop_moves(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Bishop moves diagonally"""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return row_diff == col_diff and row_diff > 0
    
    def knight_moves(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Knight moves in L-shape"""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def is_path_clear(self, board_str: str, from_row: int, from_col: int, 
                      to_row: int, to_col: int, piece: str) -> bool:
        """Check if path is clear for rook/bishop moves (knights can jump)"""
        if piece in ['K', 'N']:  # King and Knight don't need clear path
            return True
        
        grid = self.board_to_grid(board_str)
        
        # Calculate direction
        row_dir = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_dir = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        # Check each square in the path (excluding start and end)
        current_row, current_col = from_row + row_dir, from_col + col_dir
        
        while (current_row, current_col) != (to_row, to_col):
            if grid[current_row][current_col] != 'x':
                return False
            current_row += row_dir
            current_col += col_dir
        
        return True
    
    def is_valid_move(self, from_board: str, to_board: str) -> Tuple[bool, str]:
        """Validate a single move from one board state to another"""
        try:
            # Find the differences between boards
            differences = []
            for i in range(16):
                if from_board[i] != to_board[i]:
                    differences.append(i)
            
            # Should be exactly 2 differences (piece moves from one place to another)
            if len(differences) != 2:
                return False, f"Invalid move: {len(differences)} positions changed (expected 2)"
            
            pos1, pos2 = differences
            from_row1, from_col1 = pos1 // 4, pos1 % 4
            from_row2, from_col2 = pos2 // 4, pos2 % 4
            
            # One position should become empty, the other should get the piece
            char1_from, char1_to = from_board[pos1], to_board[pos1]
            char2_from, char2_to = from_board[pos2], to_board[pos2]
            
            # Determine which piece moved
            if char1_to == 'x' and char2_from == 'x':
                # Piece moved from pos1 to pos2
                piece = char1_from
                from_row, from_col = from_row1, from_col1
                to_row, to_col = from_row2, from_col2
                if char2_to != piece:
                    return False, f"Piece mismatch: {piece} -> {char2_to}"
            elif char2_to == 'x' and char1_from == 'x':
                # Piece moved from pos2 to pos1
                piece = char2_from
                from_row, from_col = from_row2, from_col2
                to_row, to_col = from_row1, from_col1
                if char1_to != piece:
                    return False, f"Piece mismatch: {piece} -> {char1_to}"
            else:
                return False, f"Invalid move pattern: ({char1_from}->{char1_to}), ({char2_from}->{char2_to})"
            
            # Validate the piece can make this move
            if piece not in self.piece_moves:
                return False, f"Unknown piece: {piece}"
            
            move_validator = self.piece_moves[piece]
            if not move_validator(from_row, from_col, to_row, to_col):
                return False, f"{piece} cannot move from ({from_row},{from_col}) to ({to_row},{to_col})"
            
            # Check if path is clear (for rook/bishop)
            if not self.is_path_clear(from_board, from_row, from_col, to_row, to_col, piece):
                return False, f"Path blocked for {piece} from ({from_row},{from_col}) to ({to_row},{to_col})"
            
            return True, "Valid move"
            
        except Exception as e:
            return False, f"Error validating move: {str(e)}"
    
    def is_goal_state(self, board_str: str) -> bool:
        """Check if board state achieves the goal (all knights in top row)"""
        top_row = board_str[:4]
        return top_row == "NNNN"
    
    def validate_solution_path(self, initial_board: str, solution_path: str) -> Tuple[bool, str, Dict]:
        """Validate complete solution path"""
        try:
            if not solution_path or solution_path.strip() == "":
                return False, "Empty solution path", {"steps_validated": 0}
            
            # Parse solution path
            steps = [step.strip() for step in solution_path.split(';') if step.strip()]
            
            if not steps:
                return False, "No valid steps in solution path", {"steps_validated": 0}
            
            # First step should match initial board
            if steps[0] != initial_board:
                return False, f"First step doesn't match initial board: '{steps[0]}' != '{initial_board}'", {"steps_validated": 0}
            
            stats = {
                "total_steps": len(steps),
                "steps_validated": 0,
                "moves_count": len(steps) - 1,
                "goal_achieved": False,
                "final_board": steps[-1] if steps else ""
            }
            
            # Validate each move in the sequence
            for i in range(len(steps) - 1):
                current_board = steps[i]
                next_board = steps[i + 1]
                
                is_valid, error_msg = self.is_valid_move(current_board, next_board)
                if not is_valid:
                    return False, f"Invalid move at step {i+1}->{i+2}: {error_msg}", stats
                
                stats["steps_validated"] = i + 1
            
            # Check if goal is achieved
            final_board = steps[-1]
            stats["goal_achieved"] = self.is_goal_state(final_board)
            stats["final_board"] = final_board
            
            if not stats["goal_achieved"]:
                return False, f"Goal not achieved. Final board: {final_board}", stats
            
            return True, "Solution is valid!", stats
            
        except Exception as e:
            return False, f"Error validating solution: {str(e)}", {"steps_validated": 0}
    
    def validate_csv_file(self, csv_file: str) -> Dict:
        """Validate all solutions in a CSV file"""
        results = {
            "file": csv_file,
            "total_solutions": 0,
            "valid_solutions": 0,
            "invalid_solutions": 0,
            "no_solution": 0,
            "details": []
        }
        
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    config_id = int(row['ID'])
                    initial_board = row['Initial Board']
                    solution_path = row['Solution Path']
                    reported_moves = int(row['Moves']) if row['Moves'] != '-1' else -1
                    solve_time = float(row['Time (ms)'])
                    
                    results["total_solutions"] += 1
                    
                    # Skip if no solution reported
                    if reported_moves == -1 or not solution_path:
                        results["no_solution"] += 1
                        results["details"].append({
                            "id": config_id,
                            "status": "no_solution",
                            "error": "No solution provided",
                            "reported_moves": reported_moves,
                            "actual_moves": 0,
                            "solve_time": solve_time
                        })
                        continue
                    
                    # Validate the solution
                    is_valid, error_msg, stats = self.validate_solution_path(initial_board, solution_path)
                    
                    detail = {
                        "id": config_id,
                        "status": "valid" if is_valid else "invalid",
                        "error": error_msg if not is_valid else "",
                        "reported_moves": reported_moves,
                        "actual_moves": stats.get("moves_count", 0),
                        "solve_time": solve_time,
                        "goal_achieved": stats.get("goal_achieved", False),
                        "steps_validated": stats.get("steps_validated", 0)
                    }
                    
                    # Check if reported moves match actual moves
                    if is_valid and reported_moves != stats.get("moves_count", 0):
                        is_valid = False
                        detail["status"] = "invalid"
                        detail["error"] = f"Move count mismatch: reported {reported_moves}, actual {stats.get('moves_count', 0)}"
                    
                    if is_valid:
                        results["valid_solutions"] += 1
                    else:
                        results["invalid_solutions"] += 1
                    
                    results["details"].append(detail)
        
        except FileNotFoundError:
            results["error"] = f"File '{csv_file}' not found"
        except Exception as e:
            results["error"] = f"Error reading file: {str(e)}"
        
        return results
    
    def print_validation_summary(self, results: Dict) -> None:
        """Print a summary of validation results"""
        print(f"\n{'='*60}")
        print(f"SOLUTION VALIDATION RESULTS")
        print(f"File: {results['file']}")
        print(f"{'='*60}")
        
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        total = results["total_solutions"]
        valid = results["valid_solutions"]
        invalid = results["invalid_solutions"]
        no_solution = results["no_solution"]
        
        print(f"📊 Summary:")
        print(f"  Total solutions: {total}")
        print(f"  ✅ Valid: {valid}")
        print(f"  ❌ Invalid: {invalid}")
        print(f"  ⏭️  No solution: {no_solution}")
        
        if total > 0:
            success_rate = (valid / total) * 100
            print(f"  📈 Success rate: {success_rate:.1f}%")
        
        print(f"\n{'='*60}")
        
        # Show invalid solutions
        if invalid > 0:
            print(f"❌ INVALID SOLUTIONS:")
            for detail in results["details"]:
                if detail["status"] == "invalid":
                    print(f"  Config {detail['id']}: {detail['error']}")
                    print(f"    Reported moves: {detail['reported_moves']}, Actual: {detail['actual_moves']}")
                    print(f"    Steps validated: {detail['steps_validated']}")
        
        # Show configurations with no solutions
        if no_solution > 0:
            print(f"\n⏭️  NO SOLUTIONS:")
            no_sol_ids = [str(d['id']) for d in results["details"] if d["status"] == "no_solution"]
            print(f"  Config IDs: {', '.join(no_sol_ids)}")
        
        # Show valid solutions summary
        if valid > 0:
            print(f"\n✅ VALID SOLUTIONS:")
            valid_details = [d for d in results["details"] if d["status"] == "valid"]
            move_counts = [d["actual_moves"] for d in valid_details]
            solve_times = [d["solve_time"] for d in valid_details]
            
            print(f"  Move range: {min(move_counts)}-{max(move_counts)} moves")
            print(f"  Average moves: {sum(move_counts)/len(move_counts):.1f}")
            print(f"  Time range: {min(solve_times):.1f}-{max(solve_times):.1f}ms")
            print(f"  Average time: {sum(solve_times)/len(solve_times):.1f}ms")

def main():
    """Main function"""
    print("🔍 Hippodrome Solution Validator 🔍")
    
    # Default CSV file
    csv_file = "solutions_csv/first_5_solutions.csv"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    validator = SolutionValidator()
    results = validator.validate_csv_file(csv_file)
    validator.print_validation_summary(results)
    
    # Return appropriate exit code
    if "error" in results:
        return 1
    elif results["invalid_solutions"] > 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    exit(main()) 