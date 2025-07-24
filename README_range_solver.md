# 🏇 Enhanced Hippodrome Solver with Range Support

The hippodrome solver now supports processing specific ranges of configurations, giving you full control over which puzzles to solve.

## 🚀 **Range Functionality**

### **Command Line Usage**
```bash
# Default: Process first 5 configs (0-4)
.\hippodrome_solver_working.exe

# Process a single config
.\hippodrome_solver_working.exe 15

# Process a range using different formats
.\hippodrome_solver_working.exe 5->10     # Configs 5 to 10 (inclusive)
.\hippodrome_solver_working.exe 5-10      # Configs 5 to 10 (inclusive)  
.\hippodrome_solver_working.exe 5..10     # Configs 5 to 10 (inclusive)

# Process ALL configurations (be careful - this is 415k+ configs!)
.\hippodrome_solver_working.exe all

# Show help
.\hippodrome_solver_working.exe help
```

## 📁 **Automatic File Naming**

The solver automatically names output files based on your range:

| Range Input | Output Filename |
|-------------|-----------------|
| *(default)* | `first_5_solutions.csv` |
| `15` | `config_15_solution.csv` |
| `5->10` | `configs_5_to_10_solutions.csv` |
| `20-25` | `configs_20_to_25_solutions.csv` |
| `all` | `all_solutions.csv` |

## 🎯 **Examples & Results**

### **Example 1: Process configs 5-10**
```bash
.\hippodrome_solver_working.exe 5->10
```
**Output:**
```
Processing configs 5 to 10 (6 configs) out of 415801 total configs

Processing config 1/6 (Index: 5, ID: 5)
Initial board: KBKRKxBBRRKBNNNN
[Board visualization...]
ID: 5, Moves: 28, Time: 149.894 ms
Solution found with 28 moves!
----------------------------------------
[... continues for configs 6,7,8,9,10 ...]

Solutions saved to "solutions_csv\configs_5_to_10_solutions.csv"
```

### **Example 2: Process single config**
```bash
.\hippodrome_solver_working.exe 15
```
**Output:**
```
Processing configs 15 to 15 (1 configs) out of 415801 total configs

Processing config 1/1 (Index: 15, ID: 15)
[Board visualization and solution...]

Solutions saved to "solutions_csv\config_15_solution.csv"
```

## ⚙️ **Features**

### ✅ **Multiple Range Formats**
- **Arrow format**: `5->10`
- **Dash format**: `5-10` 
- **Dots format**: `5..10`
- **Single config**: `15`
- **All configs**: `all`

### ✅ **Smart Validation**
- Validates range bounds against available configs
- Prevents invalid ranges (e.g., start > end)
- Clear error messages for invalid input

### ✅ **Progress Tracking**
- Shows current config being processed
- Displays both relative position (1/6) and absolute index
- Shows total configs available vs. being processed

### ✅ **Automatic Output Management**
- Auto-generates descriptive filenames
- Creates `solutions_csv/` directory if needed
- No file conflicts - each range gets its own file

## 🎮 **Integration with Visualizer**

The range solver works seamlessly with the Python visualizer:

```bash
# Solve a range
.\hippodrome_solver_working.exe 10->15

# Visualize the results
python visualize_solution.py solutions_csv/configs_10_to_15_solutions.csv

# Or visualize a specific config from that range
python visualize_solution.py solutions_csv/configs_10_to_15_solutions.csv 12
```

## 📊 **Performance Notes**

- **Small ranges (1-20 configs)**: Very fast, great for testing
- **Medium ranges (20-100 configs)**: Good for systematic analysis
- **Large ranges (100+ configs)**: Consider running in batches
- **All configs (415k+)**: Plan for significant processing time

## 🛠️ **Error Handling**

### **Invalid Range Format**
```bash
.\hippodrome_solver_working.exe xyz
# Error: Invalid range format 'xyz'
# [Shows usage help]
```

### **Out of Bounds Range**
```bash
.\hippodrome_solver_working.exe 500000->500010
# Error: Range 500000 to 500010 is invalid. Available configs: 0 to 415800
```

### **Backwards Range**
```bash
.\hippodrome_solver_working.exe 10->5
# Error: Range 10 to 5 is invalid. Available configs: 0 to 415800
```

## 💡 **Use Cases**

### **Development & Testing**
```bash
# Test solver changes on small set
.\hippodrome_solver_working.exe 0->4
```

### **Systematic Analysis**
```bash
# Analyze difficulty patterns in ranges
.\hippodrome_solver_working.exe 100->200
.\hippodrome_solver_working.exe 1000->1100
```

### **Specific Config Investigation**
```bash
# Focus on a particular interesting configuration
.\hippodrome_solver_working.exe 1337
```

### **Batch Processing**
```bash
# Process in manageable chunks
.\hippodrome_solver_working.exe 0->999     # First 1k
.\hippodrome_solver_working.exe 1000->1999 # Second 1k
# ... continue as needed
```

## 🔧 **Technical Details**

- **Range parsing**: Supports multiple formats with robust error handling
- **Index validation**: Ensures ranges fit within available data
- **Memory efficient**: Only loads configs once, processes specified range
- **Progress reporting**: Clear indication of current position
- **File management**: Automatic directory creation and naming

## 🎯 **Best Practices**

1. **Start small**: Test with small ranges before large batches
2. **Use descriptive ranges**: `10->20` is clearer than just `all`
3. **Monitor output**: Check CSV files are being generated correctly
4. **Batch large jobs**: Break huge ranges into manageable chunks
5. **Backup results**: Save important solution sets before re-running

---

*The enhanced solver gives you complete control over which configurations to process - from single configs to massive batch jobs!* 🚀 