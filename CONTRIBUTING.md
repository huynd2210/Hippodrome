# Contributing to Hippodrome Solver 🤝

Thank you for your interest in contributing to the Hippodrome Solver project! This guide will help you get started.

## 🚀 Quick Start

### Prerequisites
- **C++ Compiler**: GCC 7+ or Clang 5+ with C++17 support
- **Python 3.8+**: For utilities and web frontend
- **Git**: For version control

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hippodrome-solver.git
   cd hippodrome-solver
   ```

2. **Build the solver**
   ```bash
   make all
   # or manually:
   g++ -std=c++17 -O3 -pthread hippodrome_solver_working.cpp -o solver
   ```

3. **Install Python dependencies**
   ```bash
   make install-deps
   # or manually:
   cd frontend_explorer && pip install -r requirements.txt
   ```

4. **Run tests**
   ```bash
   make test
   make test-solver
   ```

## 📁 Project Architecture

### Core Components

- **`hippodrome_solver_working.cpp`**: Main solver with A* algorithm
- **`frontend_explorer/`**: Flask web application
- **`tests/`**: Unit tests for core functionality
- **Utility scripts**: Visualization, validation, and demo tools

### Key Algorithms

- **A* Search**: Core pathfinding algorithm
- **Heuristics**: Manhattan distance + piece-specific costs
- **Multi-threading**: Parallel processing of configurations
- **State Management**: Efficient board representation

## 🛠️ Development Guidelines

### Code Style

#### C++
- **Standard**: C++17
- **Naming**: `snake_case` for variables, `PascalCase` for classes
- **Comments**: Document complex algorithms and heuristics
- **Thread Safety**: Use proper locking for shared resources

```cpp
// Good
class HippodromeState {
    int calculate_heuristic() const;
    std::vector<Move> get_valid_moves() const;
};

// Bad
class hippodromestate {
    int calcHeuristic();
};
```

#### Python
- **Style**: Follow PEP 8
- **Type Hints**: Use for function signatures
- **Docstrings**: Document all public functions

```python
def visualize_solution(board_state: str, moves: str) -> None:
    """Display step-by-step solution visualization.
    
    Args:
        board_state: 16-character board representation
        moves: Comma-separated move sequence
    """
```

#### Web Frontend
- **JavaScript**: ES6+ features, clear variable names
- **CSS**: Organized by component, responsive design
- **HTML**: Semantic markup, accessibility considerations

### Testing

#### Unit Tests
- **Location**: `tests/` directory
- **Framework**: pytest for Python tests
- **Coverage**: Aim for >80% code coverage

```bash
# Run all tests
make test

# Run specific test file
cd tests && python -m pytest test_solver.py -v
```

#### Integration Tests
- **Solver**: Test with sample configurations
- **Frontend**: API endpoint testing
- **End-to-end**: Full pipeline validation

#### Performance Tests
- **Benchmarks**: Track solving speed improvements
- **Memory**: Monitor memory usage patterns
- **Scalability**: Test with large configuration sets

## 🔧 Common Development Tasks

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Implement with tests**
   - Write tests first (TDD approach)
   - Implement feature
   - Ensure all tests pass

3. **Update documentation**
   - Add/update relevant README sections
   - Document new API endpoints
   - Add usage examples

### Optimizing the Solver

1. **Profile performance**
   ```bash
   # Compile with debug info
   g++ -std=c++17 -O3 -g -pthread hippodrome_solver_working.cpp -o solver_debug
   
   # Profile with perf or similar tools
   perf record ./solver_debug input.csv output.csv 0-99 1
   ```

2. **Common optimization areas**
   - Heuristic function improvements
   - Memory allocation patterns
   - Thread synchronization overhead
   - Database query optimization

### Frontend Development

1. **Start development server**
   ```bash
   cd frontend_explorer
   python app.py
   ```

2. **Test API endpoints**
   ```bash
   python test_api.py
   ```

3. **Frontend testing**
   - Test across different browsers
   - Verify responsive design
   - Check accessibility features

## 🐛 Bug Reports

### Before Reporting
- Search existing issues
- Test with latest version
- Reproduce with minimal example

### Bug Report Template
```markdown
**Bug Description**
Clear description of the issue

**Steps to Reproduce**
1. Compile with: `g++ ...`
2. Run with: `./solver ...`
3. Observe error: ...

**Expected Behavior**
What should have happened

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Compiler: [e.g., GCC 9.3.0]
- Python: [e.g., 3.8.5]

**Additional Context**
Screenshots, logs, or config files
```

## 💡 Feature Requests

### Good Feature Requests Include:
- **Clear use case**: Why is this needed?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches?
- **Implementation hints**: Technical details if known

### Priority Areas:
- **Performance improvements**: Faster solving algorithms
- **UI enhancements**: Better user experience
- **Visualization**: New ways to display solutions
- **Analysis tools**: Solution statistics and patterns

## 📝 Pull Request Process

### Before Submitting
- [ ] Tests pass locally (`make check`)
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No merge conflicts with main

### PR Description Template
```markdown
## Changes Made
- Brief description of changes
- Link to related issue: #123

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if UI changes)
[Include relevant screenshots]

## Additional Notes
Any special considerations for reviewers
```

### Review Process
1. **Automated checks**: CI runs tests automatically
2. **Code review**: Maintainers review for quality
3. **Testing**: Additional testing on different platforms
4. **Merge**: Approved PRs merged to main branch

## 🏆 Recognition

Contributors are recognized in:
- **README.md**: Major contributors listed
- **Releases**: Contributors credited in release notes
- **GitHub**: Contributor graphs and statistics

## 📞 Getting Help

### Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Code Comments**: In-line documentation

### Response Times
- **Bug reports**: Usually within 2-3 days
- **Feature requests**: Weekly review cycle
- **Pull requests**: Within 1 week for initial feedback

## 📚 Additional Resources

### Learning Resources
- [A* Algorithm Guide](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Chess Programming Wiki](https://www.chessprogramming.org/)
- [Multi-threading in C++](https://en.cppreference.com/w/cpp/thread)

### Development Tools
- **Debuggers**: GDB, LLDB for C++ debugging
- **Profilers**: Valgrind, perf for performance analysis
- **Static Analysis**: Clang-tidy, cppcheck for code quality

---

**Happy coding! 🎯** Thank you for contributing to Hippodrome Solver! 