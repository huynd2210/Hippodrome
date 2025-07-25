#!/usr/bin/env python3
"""
Test script to verify the lazy-loading system is working correctly.
"""

import sqlite3
import os

def test_targets_index():
    """Test if the targets index database is working"""
    print("🔍 Testing targets index...")
    
    if not os.path.exists("targets_index.db"):
        print("❌ targets_index.db not found")
        return False
    
    try:
        conn = sqlite3.connect("targets_index.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, total_solutions FROM targets")
        targets = cursor.fetchall()
        
        print(f"✅ Found {len(targets)} targets:")
        for name, count in targets:
            print(f"   • {name}: {count:,} solutions")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing targets index: {e}")
        return False

def test_target_database(target_name):
    """Test a specific target database"""
    db_file = f"hippodrome_{target_name.replace('-', '_')}.db"
    
    print(f"\n🔍 Testing {target_name} database ({db_file})...")
    
    if not os.path.exists(db_file):
        print(f"❌ {db_file} not found")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Test metadata
        cursor.execute("SELECT key, value FROM metadata")
        metadata = dict(cursor.fetchall())
        
        print(f"✅ Metadata:")
        print(f"   • Target: {metadata.get('target_name', 'Unknown')}")
        print(f"   • Positions: {metadata.get('target_positions', 'Unknown')}")
        print(f"   • Description: {metadata.get('target_description', 'Unknown')}")
        print(f"   • Total solutions: {metadata.get('total_solutions', 'Unknown')}")
        
        # Test some queries
        cursor.execute("SELECT COUNT(*) FROM solutions")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(moves), MAX(moves), AVG(moves) FROM solutions WHERE moves > 0")
        min_moves, max_moves, avg_moves = cursor.fetchone()
        
        print(f"✅ Query results:")
        print(f"   • Total records: {count:,}")
        print(f"   • Move range: {min_moves} - {max_moves} (avg: {avg_moves:.1f})")
        
        # Test random solution
        cursor.execute("SELECT id, moves FROM solutions ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        if result:
            print(f"✅ Random solution: ID {result[0]}, {result[1]} moves")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing {target_name} database: {e}")
        return False

def test_api_simulation():
    """Simulate API calls to test the system"""
    print("\n🔍 Testing API simulation...")
    
    try:
        # Test targets endpoint simulation
        conn = sqlite3.connect("targets_index.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, positions, description, total_solutions FROM targets")
        targets = cursor.fetchall()
        conn.close()
        
        print(f"✅ API /targets simulation: {len(targets)} targets available")
        
        # Test specific target database access
        for target_name, positions, description, total_solutions in targets:
            db_file = f"hippodrome_{target_name.replace('-', '_')}.db"
            if os.path.exists(db_file):
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM solutions ORDER BY RANDOM() LIMIT 1")
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    print(f"✅ API /random?target={target_name} simulation: ID {result[0]}")
                else:
                    print(f"⚠️ No solutions in {target_name} database")
            else:
                print(f"❌ Database missing for {target_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in API simulation: {e}")
        return False

def main():
    print("🎯 Lazy-Loading System Test")
    print("=" * 40)
    
    # Change to the correct directory
    os.chdir(os.path.dirname(__file__) if os.path.dirname(__file__) else '.')
    
    success_count = 0
    total_tests = 0
    
    # Test targets index
    total_tests += 1
    if test_targets_index():
        success_count += 1
    
    # Test individual target databases
    target_names = ["first-column", "last-column", "corners"]
    for target_name in target_names:
        total_tests += 1
        if test_target_database(target_name):
            success_count += 1
    
    # Test API simulation
    total_tests += 1
    if test_api_simulation():
        success_count += 1
    
    print(f"\n🎯 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✅ Lazy-loading system is working correctly!")
        print("🚀 Ready to start the Flask app with: python app_lazy.py")
    else:
        print("❌ Some tests failed. Check the database setup.")
    
    return success_count == total_tests

if __name__ == "__main__":
    main() 