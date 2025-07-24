#!/usr/bin/env python3
"""
Batch Hippodrome Solution Validator
Validates all CSV files in the solutions_csv directory
"""

import os
import glob
from validate_solutions import SolutionValidator

def main():
    """Validate all CSV files in solutions_csv directory"""
    print("🔍 Batch Hippodrome Solution Validator 🔍")
    print("=" * 50)
    
    # Find all CSV files in solutions_csv directory
    csv_pattern = "solutions_csv/*.csv"
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found matching pattern: {csv_pattern}")
        return 1
    
    print(f"Found {len(csv_files)} CSV files to validate:")
    for csv_file in sorted(csv_files):
        print(f"  - {csv_file}")
    print()
    
    validator = SolutionValidator()
    total_files = len(csv_files)
    successful_files = 0
    total_solutions = 0
    total_valid = 0
    total_invalid = 0
    total_no_solution = 0
    
    # Validate each file
    for i, csv_file in enumerate(sorted(csv_files)):
        print(f"\n[{i+1}/{total_files}] Validating {csv_file}...")
        
        results = validator.validate_csv_file(csv_file)
        
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            continue
        
        # Accumulate statistics
        file_total = results["total_solutions"]
        file_valid = results["valid_solutions"]
        file_invalid = results["invalid_solutions"]
        file_no_solution = results["no_solution"]
        
        total_solutions += file_total
        total_valid += file_valid
        total_invalid += file_invalid
        total_no_solution += file_no_solution
        
        # Quick summary for this file
        if file_invalid == 0:
            successful_files += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"  {status} - {file_valid}/{file_total} valid solutions")
        
        # Show problems if any
        if file_invalid > 0:
            invalid_ids = [str(d['id']) for d in results["details"] if d["status"] == "invalid"]
            print(f"    Invalid configs: {', '.join(invalid_ids)}")
        
        if file_no_solution > 0:
            no_sol_ids = [str(d['id']) for d in results["details"] if d["status"] == "no_solution"]
            print(f"    No solution configs: {', '.join(no_sol_ids)}")
    
    # Overall summary
    print(f"\n{'='*60}")
    print(f"OVERALL VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"📁 Files processed: {total_files}")
    print(f"✅ Files passed: {successful_files}")
    print(f"❌ Files failed: {total_files - successful_files}")
    print()
    print(f"🧩 Total solutions: {total_solutions}")
    print(f"✅ Valid solutions: {total_valid}")
    print(f"❌ Invalid solutions: {total_invalid}")
    print(f"⏭️  No solutions: {total_no_solution}")
    
    if total_solutions > 0:
        success_rate = (total_valid / total_solutions) * 100
        print(f"📈 Overall success rate: {success_rate:.1f}%")
    
    print(f"{'='*60}")
    
    # Final verdict
    if total_invalid == 0:
        print("🎉 All solutions are VALID! 🎉")
        return 0
    else:
        print(f"⚠️  Found {total_invalid} invalid solutions across {total_files - successful_files} files")
        return 1

if __name__ == "__main__":
    exit(main()) 