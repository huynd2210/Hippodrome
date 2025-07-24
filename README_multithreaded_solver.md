# 🚀 Multi-Threaded Hippodrome Solver

The hippodrome solver now supports **multi-threading** for parallel processing of puzzle configurations, dramatically improving performance for large ranges.

## 🎯 **Core Features**

### ✅ **Parallel Processing**
- Multiple threads solve different puzzles simultaneously
- Automatic work distribution across threads
- Thread-safe output and result collection

### ✅ **Flexible Threading**
- Specify any number of threads via command line
- Automatic thread count optimization (won't exceed available work)
- Falls back to single-threaded mode when needed

### ✅ **Smart File Management**
- Multi-threaded runs append thread count to filename
- Example: `configs_10_to_15_solutions_4t.csv`
- Single-threaded files maintain original naming

## 🚀 **Usage Examples**

### **Basic Multi-Threading**
```bash
# Process configs 5-10 using 3 threads
.\hippodrome_solver_working.exe 5->10 3

# Process 50 configs using 8 threads
.\hippodrome_solver_working.exe 0->49 8

# Process all configs using 16 threads (careful - this is huge!)
.\hippodrome_solver_working.exe all 16
```

### **Performance Comparison**
```bash
# Single-threaded (baseline)
.\hippodrome_solver_working.exe 50->65 1

# Multi-threaded (4 threads)
.\hippodrome_solver_working.exe 50->65 4
```

## 📊 **Performance Results**

Based on testing with configs 50-65 (16 configurations):

| Mode | Threads | Total Time | Avg per Config | Speedup |
|------|---------|------------|----------------|---------|
| Single | 1 | ~650ms | ~40ms | 1.0x |
| Multi | 4 | ~488ms | ~30ms | **1.33x** |

**Note**: Speedup varies based on:
- Number of configs vs. threads
- Individual puzzle complexity
- System CPU cores
- Thread overhead vs. parallelization benefits

## 🎮 **Command Line Interface**

### **Full Syntax**
```bash
.\hippodrome_solver_working.exe [range] [threads]
```

### **Examples with Thread Counts**
```bash
# Default: 5 configs, single-threaded
.\hippodrome_solver_working.exe

# Single config, single-threaded  
.\hippodrome_solver_working.exe 42

# Range with 2 threads
.\hippodrome_solver_working.exe 10->20 2

# Large range with 8 threads
.\hippodrome_solver_working.exe 100->500 8

# All configs with maximum parallelism
.\hippodrome_solver_working.exe all 12
```

## 🧵 **Threading Architecture**

### **Work Distribution**
The solver automatically distributes work evenly:

**Example**: 16 configs with 4 threads:
- Thread 0: configs 50-53 (4 configs)
- Thread 1: configs 54-57 (4 configs)  
- Thread 2: configs 58-61 (4 configs)
- Thread 3: configs 62-65 (4 configs)

**Example**: 10 configs with 3 threads:
- Thread 0: configs 0-3 (4 configs)
- Thread 1: configs 4-6 (3 configs)
- Thread 2: configs 7-9 (3 configs)

### **Thread Safety**
- **Console Output**: Mutex-protected for clean display
- **Result Collection**: Thread-safe result aggregation
- **Progress Tracking**: Atomic counters for accurate progress
- **CSV Writing**: Single-threaded final output phase

## 🎯 **Output Format**

### **Console Output**
```
Processing configs 50 to 65 (16 configs) out of 415801 total configs
Using 4 thread(s)
Output file: configs_50_to_65_solutions_4t.csv

Thread 0 will process configs 50 to 53 (4 configs)
Thread 1 will process configs 54 to 57 (4 configs)
Thread 2 will process configs 58 to 61 (4 configs)
Thread 3 will process configs 62 to 65 (4 configs)

Starting 4 threads...

Thread 2 processing config 1 (Index: 58, ID: 58) [3/16 total]
[Board visualization...]
Thread 2 - ID: 58, Moves: 27, Time: 6.89 ms
Solution found with 27 moves!
----------------------------------------

All threads completed!

Overall processing time: 488.042 ms
Average time per config: 30.5026 ms
Solutions saved to "solutions_csv\configs_50_to_65_solutions_4t.csv"
```

### **File Naming Convention**
| Input | Output Filename |
|-------|-----------------|
| `5->10 1` | `configs_5_to_10_solutions.csv` |
| `5->10 4` | `configs_5_to_10_solutions_4t.csv` |
| `all 8` | `all_solutions_8t.csv` |
| `42 1` | `config_42_solution.csv` |
| `42 3` | `config_42_solution_3t.csv` |

## 🔧 **Optimization Guidelines**

### **Choosing Thread Count**
```bash
# For small ranges (1-10 configs): Use 1-2 threads
.\hippodrome_solver_working.exe 5->10 2

# For medium ranges (10-50 configs): Use 2-4 threads  
.\hippodrome_solver_working.exe 20->60 4

# For large ranges (50+ configs): Use 4-8 threads
.\hippodrome_solver_working.exe 100->500 8

# For massive ranges (1000+ configs): Use 8-16 threads
.\hippodrome_solver_working.exe 1000->5000 12
```

### **Hardware Considerations**
- **CPU Cores**: Generally use 1-2 threads per CPU core
- **Memory**: Each thread uses additional memory for solving
- **I/O**: Console output is serialized (doesn't benefit from more threads)

### **Sweet Spot Analysis**
- **2-4 threads**: Good for most scenarios
- **8+ threads**: Beneficial for large ranges (100+ configs)
- **16+ threads**: Only helpful for massive batches (1000+ configs)

## 🎮 **Integration with Visualizer**

Multi-threaded CSV files work seamlessly with the Python visualizer:

```bash
# Solve with multiple threads
.\hippodrome_solver_working.exe 50->60 4

# Visualize the results
python visualize_solution.py solutions_csv/configs_50_to_60_solutions_4t.csv

# Focus on specific config
python visualize_solution.py solutions_csv/configs_50_to_60_solutions_4t.csv 55
```

## 🛠️ **Error Handling**

### **Invalid Thread Count**
```bash
.\hippodrome_solver_working.exe 5->10 0
# Error: Thread count must be positive, got 0

.\hippodrome_solver_working.exe 5->10 abc
# Error: Invalid thread count 'abc'
```

### **Thread Optimization**
```bash
# If you specify more threads than configs, it's automatically optimized:
.\hippodrome_solver_working.exe 5->7 10
# Automatically reduces to 3 threads (one per config)
```

## 📈 **Performance Benefits**

### **When Multi-Threading Helps Most**
- **Large ranges**: 50+ configurations
- **Complex puzzles**: Solutions requiring many moves
- **Batch processing**: Systematic analysis of puzzle sets
- **Multi-core systems**: 4+ CPU cores available

### **When Single-Threading is Better**
- **Small ranges**: 1-10 configurations  
- **Quick tests**: Development and debugging
- **Limited systems**: Single-core or resource-constrained
- **Sequential analysis**: When order matters

## 💡 **Best Practices**

### **Development Workflow**
```bash
# 1. Test with small range, single-threaded
.\hippodrome_solver_working.exe 0->4 1

# 2. Scale up with multi-threading
.\hippodrome_solver_working.exe 0->20 4

# 3. Production batches with optimal threading
.\hippodrome_solver_working.exe 0->1000 8
```

### **Resource Management**
- Monitor CPU usage while running
- For very large ranges, consider splitting into multiple runs
- Save intermediate results to avoid losing progress

### **Quality Assurance**
- Compare single vs. multi-threaded results for consistency
- Verify CSV output integrity with large thread counts
- Test visualization compatibility with multi-threaded outputs

## 🔮 **Future Enhancements**

Potential improvements for even better performance:
- **GPU acceleration** for puzzle solving
- **Distributed computing** across multiple machines
- **Memory pooling** for reduced allocation overhead
- **Priority queuing** for solving hardest puzzles first

---

*The multi-threaded solver transforms your puzzle-solving workflow from sequential to parallel, unlocking the full power of modern multi-core systems!* 🚀⚡ 