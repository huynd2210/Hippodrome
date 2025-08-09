// This program solves a puzzle on a 4x4 board, where the goal is to move four knights ('N')
// to a target configuration. The other pieces on the board can be King ('K'), Queen ('Q'),
// Rook ('R'), or Bishop ('B'). The empty space is represented by 'x'.
// The program uses the A* search algorithm to find the shortest path to the solution.
// It can solve multiple board configurations in parallel using multiple threads.
// The board configurations are loaded from a CSV file, and the solutions are saved to another CSV file.

#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <unordered_set>
#include <functional>
#include <fstream>
#include <stdexcept>
#include <cmath>
#include <chrono>
#include <tuple>
#include <sstream>
#include <thread>
#include <mutex>
#include <atomic>

/**
 * @brief Represents a target configuration for the puzzle.
 * A target is defined by a set of 4 board positions that the knights must occupy.
 */
struct Target {
    std::vector<int> positions; // The target positions, represented as indices from 0 to 15.
    std::string name;           // A descriptive name for the target (e.g., "top-row").
    
    /**
     * @brief Constructor for a Target.
     * @param pos A vector of 4 integers representing the target positions.
     * @param n A string representing the name of the target.
     */
    Target(const std::vector<int>& pos, const std::string& n) 
        : positions(pos), name(n) {}
};

/**
 * @brief A namespace for predefined, commonly used target configurations.
 */
namespace Targets {
    const Target TOP_ROW({0, 1, 2, 3}, "top-row");
    const Target BOTTOM_ROW({12, 13, 14, 15}, "bottom-row");
    const Target FIRST_COLUMN({0, 4, 8, 12}, "first-column");
    const Target LAST_COLUMN({3, 7, 11, 15}, "last-column");
}

/**
 * @brief Parses a target configuration from a string.
 * @param target_str The string to parse. It can be a predefined target name (e.g., "top-row") 
 * or a custom, comma-separated list of 4 board positions (e.g., "0,1,4,5").
 * @return A Target object.
 */
Target parse_target(const std::string& target_str) {
    if (target_str == "top-row") return Targets::TOP_ROW;
    if (target_str == "bottom-row") return Targets::BOTTOM_ROW;
    if (target_str == "first-column") return Targets::FIRST_COLUMN;
    if (target_str == "last-column") return Targets::LAST_COLUMN;
    
    // Try to parse as custom positions (e.g., "0,1,4,5")
    std::vector<int> positions;
    std::stringstream ss(target_str);
    std::string pos_str;
    
    while (std::getline(ss, pos_str, ',')) {
        try {
            int pos = std::stoi(pos_str);
            if (pos >= 0 && pos < 16) {
                positions.push_back(pos);
            }
        } catch (...) {
            // Invalid position, skip
        }
    }
    
    if (positions.size() == 4) {
        return Target(positions, "custom-" + target_str);
    }
    
    // Default to top-row if parsing fails
    return Targets::TOP_ROW;
}

/**
 * @brief Calculates the minimum number of knight moves required to get from a given
 * starting position to any of the target positions.
 * @param from_pos The starting position of the knight.
 * @param target The target configuration.
 * @return The minimum number of knight moves.
 */
int knight_distance_to_targets(int from_pos, const Target& target) {
    int from_row = from_pos / 4;
    int from_col = from_pos % 4;
    
    int min_distance = INT_MAX;
    for (int target_pos : target.positions) {
        int target_row = target_pos / 4;
        int target_col = target_pos % 4;
        
        // Use Breadth-First Search (BFS) to find the exact knight distance.
        std::queue<std::pair<int, int>> q; // (position, distance)
        std::unordered_set<int> visited;
        
        q.push({from_pos, 0});
        visited.insert(from_pos);
        
        while (!q.empty()) {
            auto [pos, dist] = q.front();
            q.pop();
            
            if (pos == target_pos) {
                min_distance = std::min(min_distance, dist);
                break;
            }
            
            if (dist >= min_distance) continue; // Pruning
            
            int row = pos / 4;
            int col = pos % 4;
            
            // Knight moves
            std::vector<std::pair<int, int>> knight_moves = {
                {-2, -1}, {-2, 1}, {-1, -2}, {-1, 2},
                {1, -2}, {1, 2}, {2, -1}, {2, 1}
            };
            
            for (auto [dr, dc] : knight_moves) {
                int new_row = row + dr;
                int new_col = col + dc;
                if (new_row >= 0 && new_row < 4 && new_col >= 0 && new_col < 4) {
                    int new_pos = new_row * 4 + new_col;
                    if (visited.find(new_pos) == visited.end()) {
                        visited.insert(new_pos);
                        q.push({new_pos, dist + 1});
                    }
                }
            }
        }
    }
    
    return min_distance == INT_MAX ? 0 : min_distance;
}

/**
 * @brief Represents a state in the A* search algorithm.
 */
struct State {
    int f_score; // f_score = g_score + h_score
    int g_score; // The cost of the path from the start node to this node.
    std::vector<std::string> path; // The sequence of board states to reach this state.
    std::string board; // The current board configuration as a 16-character string.

    /**
     * @brief Overloads the greater-than operator for the priority queue.
     * The priority queue will store states with the lowest f_score at the top.
     */
    bool operator>(const State& other) const {
        return f_score > other.f_score;
    }
};

// --- Function Prototypes ---
int calculate_heuristic(const std::string& board, const Target& target);
bool is_valid_move(char piece, int r1, int c1, int r2, int c2);
std::vector<std::string> get_next_states(const std::string& board);
std::vector<std::string> solve_hippodrome(const std::string& initial_board_str, const Target& target);
void print_board(const std::string& board_str);
std::vector<std::pair<int, std::string>> load_configs_from_csv(const std::string& csv_path);
void save_batch_to_csv(const std::vector<std::tuple<int, std::string, std::vector<std::string>, int, double>>& solutions, const std::string& filename);

// --- Threading Support ---
std::mutex output_mutex; // Mutex to protect console output from concurrent access.
std::mutex results_mutex; // Mutex to protect the shared results vector.
std::atomic<int> completed_count{0}; // Atomic counter for tracking overall progress.

/**
 * @brief This function is executed by each thread to process a range of board configurations.
 * @param configs The vector of all board configurations.
 * @param start_idx The starting index of the range to process.
 * @param end_idx The ending index of the range to process.
 * @param thread_id The ID of the current thread.
 * @param shared_results A reference to the shared vector of solutions.
 * @param total_configs The total number of configurations being processed.
 * @param target The target configuration.
 */
void process_configs_range(
    const std::vector<std::pair<int, std::string>>& configs,
    int start_idx, 
    int end_idx,
    int thread_id,
    std::vector<std::tuple<int, std::string, std::vector<std::string>, int, double>>& shared_results,
    int total_configs,
    const Target& target
) {
    std::vector<std::tuple<int, std::string, std::vector<std::string>, int, double>> local_results;
    
    for (int i = start_idx; i <= end_idx; ++i) {
        const auto& config = configs[i];
        int id = config.first;
        std::string initial_board = config.second;

        // Thread-safe progress output
        {
            std::lock_guard<std::mutex> lock(output_mutex);
            int current_completed = ++completed_count;
            std::cout << "Thread " << thread_id << " processing config " 
                      << (i - start_idx + 1) << " (Index: " << i << ", ID: " << id 
                      << ") [" << current_completed << "/" << total_configs << " total]" << std::endl;
            std::cout << "Initial board: " << initial_board << std::endl;
            print_board(initial_board);
        }

        auto start = std::chrono::high_resolution_clock::now();
        std::vector<std::string> solution_path = solve_hippodrome(initial_board, target);
        auto end = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double, std::milli> duration = end - start;
        int moves = solution_path.empty() ? -1 : static_cast<int>(solution_path.size()) - 1;

        // Thread-safe progress output
        {
            std::lock_guard<std::mutex> lock(output_mutex);
            std::cout << "Thread " << thread_id << " - ID: " << id
                      << ", Moves: " << moves
                      << ", Time: " << duration.count() << " ms" << std::endl;

            if (!solution_path.empty()) {
                std::cout << "Solution found with " << moves << " moves!" << std::endl;
            } else {
                std::cout << "No solution found." << std::endl;
            }
            std::cout << "----------------------------------------" << std::endl;
        }

        local_results.emplace_back(id, initial_board, solution_path, moves, duration.count());
    }
    
    // Add local results to shared results (thread-safe)
    {
        std::lock_guard<std::mutex> lock(results_mutex);
        shared_results.insert(shared_results.end(), local_results.begin(), local_results.end());
    }
}

// --- Range Parsing Functions ---
/**
 * @brief A simple struct to hold a start and end index for a range.
 */
struct Range {
    int start;
    int end;
    bool valid;
};

/**
 * @brief Parses a range string (e.g., "5-10", "5->10", "5..10", "10") into a Range struct.
 * @param range_str The string to parse.
 * @return A Range object.
 */
Range parse_range(const std::string& range_str) {
    Range range = {0, 0, false};
    
    // Check for range formats: "5->10", "5-10", "5..10"
    size_t arrow_pos = range_str.find("->");
    size_t dash_pos = range_str.find('-');
    size_t dots_pos = range_str.find("..");
    
    if (arrow_pos != std::string::npos) {
        // Format: "5->10"
        std::string start_str = range_str.substr(0, arrow_pos);
        std::string end_str = range_str.substr(arrow_pos + 2);
        try {
            range.start = std::stoi(start_str);
            range.end = std::stoi(end_str);
            range.valid = true;
        } catch (...) {
            range.valid = false;
        }
    } else if (dots_pos != std::string::npos) {
        // Format: "5..10"
        std::string start_str = range_str.substr(0, dots_pos);
        std::string end_str = range_str.substr(dots_pos + 2);
        try {
            range.start = std::stoi(start_str);
            range.end = std::stoi(end_str);
            range.valid = true;
        } catch (...) {
            range.valid = false;
        }
    } else if (dash_pos != std::string::npos && dash_pos > 0) {
        // Format: "5-10" (but not negative numbers)
        std::string start_str = range_str.substr(0, dash_pos);
        std::string end_str = range_str.substr(dash_pos + 1);
        try {
            range.start = std::stoi(start_str);
            range.end = std::stoi(end_str);
            range.valid = true;
        } catch (...) {
            range.valid = false;
        }
    } else {
        // Single number: "5" means process only config 5
        try {
            range.start = std::stoi(range_str);
            range.end = range.start;
            range.valid = true;
        } catch (...) {
            range.valid = false;
        }
    }
    
    return range;
}

/**
 * @brief Prints the command-line usage instructions for the program.
 * @param program_name The name of the program executable.
 */
void print_usage(const char* program_name) {
    std::cout << "Usage: " << program_name << " [range] [threads] [target]\n"
              << "Examples:\n"
              << "  " << program_name << "                    # Process first 5 configs, single-threaded, top-row target\n"
              << "  " << program_name << " 10                 # Process only config 10, single-threaded, top-row target\n"
              << "  " << program_name << " 5->10              # Process configs 5 to 10 (inclusive), single-threaded, top-row target\n"
              << "  " << program_name << " 5-10               # Process configs 5 to 10 (inclusive), single-threaded, top-row target\n"
              << "  " << program_name << " 5..10              # Process configs 5 to 10 (inclusive), single-threaded, top-row target\n"
              << "  " << program_name << " 5->10 4            # Process configs 5 to 10 using 4 threads, top-row target\n"
              << "  " << program_name << " all 8              # Process all configs using 8 threads, top-row target\n"
              << "  " << program_name << " all 1 first-column # Process all configs, single-threaded, first-column target\n"
              << "  " << program_name << " 0-99 4 bottom-row  # Process configs 0-99, 4 threads, bottom-row target\n"
              << "  " << program_name << " 0-99 4 \"0,4,8,12\" # Process configs 0-99, 4 threads, custom target positions\n"
              << "\nTarget options:\n"
              << "  top-row        # Knights must reach positions 0,1,2,3 (default)\n"
              << "  bottom-row     # Knights must reach positions 12,13,14,15\n"
              << "  first-column   # Knights must reach positions 0,4,8,12\n"
              << "  last-column    # Knights must reach positions 3,7,11,15\n"
              << "  \"0,1,4,5\"      # Custom positions (must be exactly 4 positions)\n"
              << std::endl;
}

// --- Heuristics and Moves ---
const int TARGET_PENALTY = 100; // A penalty applied when a non-knight piece occupies a target square.

/**
 * @brief Calculates the heuristic value (h_score) for the A* algorithm.
 * @param board The current board state.
 * @param target The target configuration.
 * @return The heuristic value.
 */
int calculate_heuristic(const std::string& board, const Target& target) {
    int total_heuristic = 0;

    // Create a set of target positions for quick lookup
    std::unordered_set<int> target_positions(target.positions.begin(), target.positions.end());

    for (int i = 0; i < 16; ++i) {
        if (board[i] == 'N') {
            // Add the minimum distance from this knight to any target position.
            total_heuristic += knight_distance_to_targets(i, target);
        } else if (target_positions.count(i) && board[i] != 'x') {
            // Add a penalty for non-knight pieces in target positions.
            total_heuristic += TARGET_PENALTY;
        }
    }

    return total_heuristic;
}

/**
 * @brief Checks if a move from (r1, c1) to (r2, c2) is valid for a given piece type.
 * @param piece The piece to move.
 * @param r1 The starting row.
 * @param c1 The starting column.
 * @param r2 The ending row.
 * @param c2 The ending column.
 * @return True if the move is valid, false otherwise.
 */
bool is_valid_move(char piece, int r1, int c1, int r2, int c2) {
    int dr = std::abs(r1 - r2);
    int dc = std::abs(c1 - c2);

    if (piece == 'N') { // Knight moves in an L-shape.
        return (dr == 1 && dc == 2) || (dr == 2 && dc == 1);
    }

    // For other pieces, the move must be to an adjacent square.
    bool is_adjacent = (std::max(dr, dc) == 1);
    if (!is_adjacent) return false;

    if (piece == 'K' || piece == 'Q') return true; // King and Queen can move to any adjacent square.
    if (piece == 'R') return r1 == r2 || c1 == c2; // Rook can move horizontally or vertically.
    if (piece == 'B') return dr == dc; // Bishop can move diagonally.

    return false;
}

// --- Board Operations ---
/**
 * @brief Generates all possible next board states from the current board state.
 * @param board The current board state.
 * @return A vector of strings, where each string is a possible next board state.
 */
std::vector<std::string> get_next_states(const std::string& board) {
    std::vector<std::string> next_states;
    
    size_t empty_index = board.find('x'); // Find the empty space marked with 'x'
    if (empty_index == std::string::npos) {
        return next_states; // No empty space found
    }

    int empty_row = empty_index / 4;
    int empty_col = empty_index % 4;

    for (int i = 0; i < 16; ++i) {
        if (board[i] != 'x') { // For each piece on the board...
            int piece_row = i / 4;
            int piece_col = i % 4;

            // ...if it's a valid move to the empty square...
            if (is_valid_move(board[i], piece_row, piece_col, empty_row, empty_col)) {
                std::string new_board = board;
                // ...swap the piece with the empty square.
                new_board[empty_index] = board[i];
                new_board[i] = 'x';
                next_states.push_back(new_board);
            }
        }
    }

    return next_states;
}

/**
 * @brief Prints a 4x4 representation of the board to the console.
 * @param board_str The board state as a 16-character string.
 */
void print_board(const std::string& board_str) {
    std::cout << "+---+---+---+---+" << std::endl;
    for (int i = 0; i < 4; ++i) {
        std::cout << "| ";
        for (int j = 0; j < 4; ++j) {
            std::cout << board_str[i * 4 + j] << " | ";
        }
        std::cout << std::endl << "+---+---+---+---+" << std::endl;
    }
}

// --- A* Solver ---
/**
 * @brief The main A* search algorithm to solve the Hippodrome puzzle.
 * @param initial_board_str The initial board state as a 16-character string.
 * @param target The target configuration.
 * @return A vector of strings representing the solution path. If no solution is found, the vector is empty.
 */
std::vector<std::string> solve_hippodrome(const std::string& initial_board_str, const Target& target) {
    if (initial_board_str.length() != 16) {
        std::cerr << "Error: Input string must be 16 characters long." << std::endl;
        return {};
    }

    // Lambda function to check if the current board state is the goal state.
    auto is_goal_state = [&target](const std::string& board) {
        // Check if all target positions are occupied by knights.
        for (int pos : target.positions) {
            if (board[pos] != 'N') {
                return false;
            }
        }
        return true;
    };

    // A priority queue to store states to visit, ordered by f_score.
    std::priority_queue<State, std::vector<State>, std::greater<State>> pq;
    // A set to keep track of visited board states to avoid cycles.
    std::unordered_set<std::string> visited;

    int initial_heuristic = calculate_heuristic(initial_board_str, target);
    pq.push({initial_heuristic, 0, {initial_board_str}, initial_board_str});

    while (!pq.empty()) {
        State current = pq.top();
        pq.pop();

        if (visited.count(current.board)) {
            continue;
        }
        visited.insert(current.board);

        if (is_goal_state(current.board)) {
            return current.path; // Solution found
        }

        int new_g_score = current.g_score + 1;
        for (const auto& next_board : get_next_states(current.board)) {
            if (!visited.count(next_board)) {
                int heuristic = calculate_heuristic(next_board, target);
                int new_f_score = new_g_score + heuristic;
                std::vector<std::string> new_path = current.path;
                new_path.push_back(next_board);
                pq.push({new_f_score, new_g_score, new_path, next_board});
            }
        }
    }

    return {}; // No solution found
}

// --- CSV Functions ---
/**
 * @brief Loads board configurations from a CSV file.
 * @param csv_path The path to the CSV file.
 * @return A vector of pairs, where each pair contains the ID and the board string.
 */
std::vector<std::pair<int, std::string>> load_configs_from_csv(const std::string& csv_path) {
    std::vector<std::pair<int, std::string>> configs;
    std::ifstream file(csv_path);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open CSV file: " + csv_path);
    }

    std::string line;
    std::getline(file, line); // Skip header row

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string id_str, board_state;
        if (std::getline(ss, id_str, ',') && std::getline(ss, board_state)) {
            // Remove any trailing carriage return
            if (!board_state.empty() && board_state.back() == '\r') {
                board_state.pop_back();
            }
            
            // Trim any leading/trailing whitespace
            board_state.erase(0, board_state.find_first_not_of(" \t\n\r"));
            board_state.erase(board_state.find_last_not_of(" \t\n\r") + 1);
            
            // Replace spaces with 'x' to represent empty squares
            for (char& c : board_state) {
                if (c == ' ') {
                    c = 'x';
                }
            }
            
            // Ensure exactly 16 characters
            if (board_state.length() > 16) {
                board_state = board_state.substr(0, 16);
            }
            
            // Only add if we have exactly 16 characters
            if (board_state.length() == 16) {
                configs.push_back({std::stoi(id_str), board_state});
            }
        }
    }
    return configs;
}

/**
 * @brief Saves the solutions to a CSV file.
 * @param solutions The vector of solutions to save.
 * @param filename The name of the output CSV file.
 */
void save_batch_to_csv(const std::vector<std::tuple<int, std::string, std::vector<std::string>, int, double>>& solutions, const std::string& filename) {
    if (solutions.empty()) {
        std::cout << "No solutions to save." << std::endl;
        return;
    }

    // Create solutions_csv directory (manually handle cross-platform)
    #ifdef _WIN32
        system("mkdir solutions_csv 2>nul");
    #else
        system("mkdir -p solutions_csv");
    #endif
    
    std::string full_path = "solutions_csv/" + filename;
    std::ofstream file(full_path);

    file << "ID,Initial Board,Solution Path,Moves,Time (ms)\n";
    for (const auto& sol : solutions) {
        file << std::get<0>(sol) << "," << std::get<1>(sol) << ",";
        const auto& path = std::get<2>(sol);
        for (size_t i = 0; i < path.size(); ++i) {
            file << path[i] << (i == path.size() - 1 ? "" : ";");
        }
        file << "," << std::get<3>(sol) << "," << std::get<4>(sol) << "\n";
    }
    std::cout << "Solutions saved to " << full_path << std::endl;
}

// --- Main ---
/**
 * @brief The main entry point of the program.
 * @param argc The number of command-line arguments.
 * @param argv An array of command-line arguments.
 * @return 0 on success, 1 on error.
 */
int main(int argc, char* argv[]) {
    std::string csv_path = "filtered_hippodrome_configs.csv";
    std::vector<std::pair<int, std::string>> configs = load_configs_from_csv(csv_path);
    std::vector<std::tuple<int, std::string, std::vector<std::string>, int, double>> all_solutions;

    // Parse command line arguments
    Range range = {0, 4, true}; // Default: first 5 configs (0-4)
    std::string range_description = "first 5";
    std::string output_filename = "first_5_solutions.csv";
    int num_threads = 1; // Default: single-threaded
    Target target = Targets::TOP_ROW; // Default: top-row target
    
    if (argc > 1) {
        std::string arg = argv[1];
        
        if (arg == "all") {
            range.start = 0;
            range.end = (int)configs.size() - 1;
            range.valid = true;
            range_description = "all";
            output_filename = "all_solutions.csv";
        } else if (arg == "help" || arg == "-h" || arg == "--help") {
            print_usage(argv[0]);
            return 0;
        } else {
            range = parse_range(arg);
            if (range.valid) {
                range_description = "configs " + std::to_string(range.start) + " to " + std::to_string(range.end);
                if (range.start == range.end) {
                    output_filename = "config_" + std::to_string(range.start) + "_solution.csv";
                } else {
                    output_filename = "configs_" + std::to_string(range.start) + "_to_" + std::to_string(range.end) + "_solutions.csv";
                }
            } else {
                std::cerr << "Error: Invalid range format '" << arg << "'" << std::endl;
                print_usage(argv[0]);
                return 1;
            }
        }
    }
    
    // Parse thread count if provided
    if (argc > 2) {
        try {
            num_threads = std::stoi(argv[2]);
            if (num_threads <= 0) {
                std::cerr << "Error: Thread count must be positive, got " << num_threads << std::endl;
                return 1;
            }
            // Add thread count to output filename
            if (num_threads > 1) {
                size_t dot_pos = output_filename.rfind('.');
                if (dot_pos != std::string::npos) {
                    output_filename = output_filename.substr(0, dot_pos) + "_" + std::to_string(num_threads) + "t" + output_filename.substr(dot_pos);
                } else {
                    output_filename += "_" + std::to_string(num_threads) + "t";
                }
            }
        } catch (...) {
            std::cerr << "Error: Invalid thread count '" << argv[2] << "'" << std::endl;
            print_usage(argv[0]);
            return 1;
        }
    }
    
    // Parse target if provided
    if (argc > 3) {
        target = parse_target(argv[3]);
        // Add target to output filename
        size_t dot_pos = output_filename.rfind('.');
        if (dot_pos != std::string::npos) {
            output_filename = output_filename.substr(0, dot_pos) + "_" + target.name + output_filename.substr(dot_pos);
        } else {
            output_filename += "_" + target.name;
        }
    }
    
    // Validate range bounds
    if (range.start < 0 || range.end >= (int)configs.size() || range.start > range.end) {
        std::cerr << "Error: Range " << range.start << " to " << range.end 
                  << " is invalid. Available configs: 0 to " << (configs.size() - 1) << std::endl;
        return 1;
    }
    
    int total_to_process = range.end - range.start + 1;
    
    // Limit threads to available work
    if (num_threads > total_to_process) {
        num_threads = total_to_process;
    }
    
    std::cout << "Processing " << range_description << " (" << total_to_process 
              << " configs) out of " << configs.size() << " total configs" << std::endl;
    std::cout << "Using " << num_threads << " thread(s)" << std::endl;
    std::cout << "Target: " << target.name << " (positions: ";
    for (size_t i = 0; i < target.positions.size(); ++i) {
        std::cout << target.positions[i];
        if (i < target.positions.size() - 1) std::cout << ",";
    }
    std::cout << ")" << std::endl;
    std::cout << "Output file: " << output_filename << "\n" << std::endl;

    // Reset global counters
    completed_count = 0;
    
    auto overall_start = std::chrono::high_resolution_clock::now();
    
    if (num_threads == 1) {
        // Single-threaded mode
        for (int i = range.start; i <= range.end; ++i) {
            const auto& config = configs[i];
            int id = config.first;
            std::string initial_board = config.second;

            int current_index = i - range.start + 1;
            std::cout << "Processing config " << current_index << "/" << total_to_process 
                      << " (Index: " << i << ", ID: " << id << ")" << std::endl;
            std::cout << "Initial board: " << initial_board << std::endl;
            print_board(initial_board);

            auto start = std::chrono::high_resolution_clock::now();
            std::vector<std::string> solution_path = solve_hippodrome(initial_board, target);
            auto end = std::chrono::high_resolution_clock::now();

            std::chrono::duration<double, std::milli> duration = end - start;
            int moves = solution_path.empty() ? -1 : static_cast<int>(solution_path.size()) - 1;

            std::cout << "ID: " << id
                      << ", Moves: " << moves
                      << ", Time: " << duration.count() << " ms" << std::endl;

            if (!solution_path.empty()) {
                std::cout << "Solution found with " << moves << " moves!" << std::endl;
            } else {
                std::cout << "No solution found." << std::endl;
            }
            std::cout << "----------------------------------------" << std::endl;

            all_solutions.emplace_back(id, initial_board, solution_path, moves, duration.count());
        }
    } else {
        // Multi-threaded mode
        std::vector<std::thread> threads;
        
        // Calculate work distribution
        int configs_per_thread = total_to_process / num_threads;
        int remaining_configs = total_to_process % num_threads;
        
        int current_start = range.start;
        for (int thread_id = 0; thread_id < num_threads; ++thread_id) {
            int thread_configs = configs_per_thread + (thread_id < remaining_configs ? 1 : 0);
            int thread_end = current_start + thread_configs - 1;
            
            std::cout << "Thread " << thread_id << " will process configs " 
                      << current_start << " to " << thread_end 
                      << " (" << thread_configs << " configs)" << std::endl;
            
            threads.emplace_back(process_configs_range, 
                               std::cref(configs), 
                               current_start, 
                               thread_end, 
                               thread_id, 
                               std::ref(all_solutions),
                               total_to_process,
                               std::cref(target));
            
            current_start = thread_end + 1;
        }
        
        std::cout << "\nStarting " << num_threads << " threads...\n" << std::endl;
        
        // Wait for all threads to complete
        for (auto& thread : threads) {
            thread.join();
        }
        
        std::cout << "\nAll threads completed!" << std::endl;
    }
    
    auto overall_end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> overall_duration = overall_end - overall_start;
    
    std::cout << "\nOverall processing time: " << overall_duration.count() << " ms" << std::endl;
    std::cout << "Average time per config: " << (overall_duration.count() / total_to_process) << " ms" << std::endl;

    save_batch_to_csv(all_solutions, output_filename);

    return 0;
}
