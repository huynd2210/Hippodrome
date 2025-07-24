#!/usr/bin/env python3
"""
Quick test script to verify the SQLite-powered Hippodrome API is working correctly.
"""

import sqlite3
import os
import json

def test_database():
    """Test basic database functionality"""
    print("🔍 Testing SQLite Database...")
    
    if not os.path.exists("hippodrome_solutions.db"):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect("hippodrome_solutions.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test basic queries
        cursor.execute('SELECT COUNT(*) as count FROM solutions')
        total = cursor.fetchone()['count']
        print(f"✅ Total solutions: {total:,}")
        
        # Test random selection
        cursor.execute('SELECT id, initial_board, moves FROM solutions ORDER BY RANDOM() LIMIT 1')
        random_solution = cursor.fetchone()
        print(f"✅ Random solution: ID {random_solution['id']}, Board: {random_solution['initial_board'][:20]}..., Moves: {random_solution['moves']}")
        
        # Test extremes
        cursor.execute('SELECT id, moves FROM solutions ORDER BY moves DESC LIMIT 1')
        hardest = cursor.fetchone()
        print(f"✅ Hardest puzzle: ID {hardest['id']} ({hardest['moves']} moves)")
        
        cursor.execute('SELECT id, moves FROM solutions ORDER BY moves ASC LIMIT 1')
        easiest = cursor.fetchone()
        print(f"✅ Easiest puzzle: ID {easiest['id']} ({easiest['moves']} moves)")
        
        # Test filtering
        cursor.execute('SELECT COUNT(*) as count FROM solutions WHERE moves BETWEEN 25 AND 30')
        filtered_count = cursor.fetchone()['count']
        print(f"✅ Solutions with 25-30 moves: {filtered_count:,}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_functions():
    """Test the API functions directly"""
    print("\n🔍 Testing API Functions...")
    
    try:
        # Import app functions
        import sys
        sys.path.append('.')
        from app import get_db_connection, parse_solution_path
        
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM solutions')
        count = cursor.fetchone()[0]
        print(f"✅ API database connection: {count:,} solutions")
        conn.close()
        
        # Test solution path parsing
        test_path = "KBRKBRRKRBKNNNN;KBRKBRRKRBKNNNN;KBRKBRRKRBKNNNN"
        parsed = parse_solution_path(test_path)
        print(f"✅ Solution path parsing: {len(parsed)} steps")
        
        return True
        
    except Exception as e:
        print(f"❌ API function test failed: {e}")
        return False

def show_database_info():
    """Show detailed database information"""
    print("\n📊 Database Information:")
    
    try:
        conn = sqlite3.connect("hippodrome_solutions.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Database size
        db_size = os.path.getsize("hippodrome_solutions.db") / (1024 * 1024)
        print(f"   Database file size: {db_size:.1f} MB")
        
        # Statistics
        cursor.execute('SELECT COUNT(*) as total FROM solutions')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT MIN(moves) as min_moves, MAX(moves) as max_moves, AVG(moves) as avg_moves FROM solutions')
        stats = cursor.fetchone()
        
        cursor.execute('SELECT moves, COUNT(*) as count FROM solutions GROUP BY moves ORDER BY count DESC LIMIT 5')
        popular_moves = cursor.fetchall()
        
        print(f"   Total solutions: {total:,}")
        print(f"   Move range: {stats['min_moves']} - {stats['max_moves']} (avg: {stats['avg_moves']:.1f})")
        print(f"   Most common move counts:")
        
        for move_stat in popular_moves:
            print(f"     {move_stat['moves']} moves: {move_stat['count']:,} puzzles")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Could not retrieve database info: {e}")

if __name__ == "__main__":
    print("🎯 Hippodrome SQLite Backend Test")
    print("=" * 40)
    
    success = True
    
    if not test_database():
        success = False
    
    if not test_api_functions():
        success = False
    
    show_database_info()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed! SQLite backend is ready!")
        print("🚀 You can now start the server with: python app.py")
        print("🌐 Then visit: http://localhost:5000")
    else:
        print("❌ Some tests failed. Check the output above.") 