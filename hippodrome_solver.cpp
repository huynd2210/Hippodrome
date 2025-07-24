#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <unordered_set>
#include <functional>
#include <fstream>
#include <filesystem>
#include <sqlite3.h>
#include <stdexcept>
#include <cmath>
#include <unordered_map>
#include <sstream>

// Global map for knight heuristics
std::unordered_map<std::string, int> g_knightHeur;

// Represents a state in the A* search
struct State {
    int f_score;
    int g_score;
    std::vector<std::string> path;
    std::string board;

    // For the priority queue comparison
    bool operator>(const State& other) const {
        return f_score > other.f_score;
    }
};

bool is_valid_move(char piece, int r1, int c1, int r2, int c2);
std::vector<std::string> get_next_states(const std::string& board);
std::vector<std::string> solve_hippodrome(const std::string& initial_board_str);
void print_board(const std::string& board_str);
std::vector<std::pair<int, std::string>> load_configs_from_db(const std::string& db_path, int batch_size, int offset);
void save_batch_to_csv(const std::vector<std::tuple<int, std::string, std::vector<std::string>>>& solutions, const std::string& filename);

// --- Heuristics and Moves ---


int calculate_heuristic(const std::string& boardStr) {
    // The heuristic is the sum of the minimum moves for each knight to reach
    // the target row (row 0), which is an admissible heuristic.
    int knight_moves_to_row_0[] = {0, 2, 1, 2}; // Min moves from row 0, 1, 2, 3
    int total_heuristic = 0;
    for (int i = 0; i < 16; ++i) {
        if (boardStr[i] == 'N') {
            int row = i / 4;
            total_heuristic += knight_moves_to_row_0[row];
        }
    }
    return total_heuristic;
}

int get_heuristic(const std::string& board_state, const std::unordered_map<std::string, int>& heuristics) {
    auto it = heuristics.find(board_state);
    if (it != heuristics.end()) {
        return it->second;
    }
    return calculate_heuristic(board_state);
}

bool is_valid_move(char piece, int r1, int c1, int r2, int c2) {
    int dr = std::abs(r1 - r2);
    int dc = std::abs(c1 - c2);

    if (piece == 'N') {
        return (dr == 1 && dc == 2) || (dr == 2 && dc == 1);
    }

    bool is_adjacent = (std::max(dr, dc) == 1);
    if (!is_adjacent) return false;

    if (piece == 'K' || piece == 'Q') return true;
    if (piece == 'R') return r1 == r2 || c1 == c2;
    if (piece == 'B') return dr == dc;

    return false;
}

// --- Board Operations ---
std::vector<std::string> get_next_states(const std::string& board) {
    std::vector<std::string> next_states;
    size_t empty_index = board.find(' ');
    if (empty_index == std::string::npos) return next_states;

    int er = empty_index / 4;
    int ec = empty_index % 4;

    for (int i = 0; i < 16; ++i) {
        if (i == empty_index) continue;

        int r = i / 4;
        int c = i % 4;
        if (is_valid_move(board[i], r, c, er, ec)) {
            std::string new_board = board;
            std::swap(new_board[empty_index], new_board[i]);
            next_states.push_back(new_board);
        }
    }
    return next_states;
}

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
std::vector<std::string> solve_hippodrome(const std::string& initial_board_str) {
    if (initial_board_str.length() != 16) {
        std::cerr << "Error: Input string must be 16 characters long." << std::endl;
        return {};
    }

    auto is_goal_state = [](const std::string& board) {
        return board.substr(0, 4) == "NNNN";
    };

    std::priority_queue<State, std::vector<State>, std::greater<State>> pq;
    std::unordered_set<std::string> visited;

    int initial_heuristic = get_heuristic(initial_board_str, g_knightHeur);
    pq.push({initial_heuristic, 0, {initial_board_str}, initial_board_str});

    while (!pq.empty()) {
        State current = pq.top();
        pq.pop();

        if (visited.count(current.board)) {
            continue;
        }
        visited.insert(current.board);

        if (is_goal_state(current.board)) {
            std::cout << "Solution found in " << current.path.size() - 1 << " moves!" << std::endl;
            return current.path;
        }

        int new_g_score = current.g_score + 1;
        for (const auto& next_board : get_next_states(current.board)) {
            if (!visited.count(next_board)) {
                int heuristic = get_heuristic(next_board, g_knightHeur);
                int new_f_score = new_g_score + heuristic;
                std::vector<std::string> new_path = current.path;
                new_path.push_back(next_board);
                pq.push({new_f_score, new_g_score, new_path, next_board});
            }
        }
    }

    std::cout << "No solution found for the given board configuration." << std::endl;
    return {};
}

// --- Database and CSV ---
std::vector<std::pair<int, std::string>> load_configs_from_db(const std::string& db_path, int batch_size, int offset) {
    sqlite3* db;
    if (sqlite3_open(db_path.c_str(), &db)) {
        throw std::runtime_error("Can't open database: " + std::string(sqlite3_errmsg(db)));
    }

    sqlite3_stmt* stmt;
    std::string sql = "SELECT id, board_state FROM configurations LIMIT ? OFFSET ?;";
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, 0) != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare statement: " + std::string(sqlite3_errmsg(db)));
    }

    sqlite3_bind_int(stmt, 1, batch_size);
    sqlite3_bind_int(stmt, 2, offset);

    std::vector<std::pair<int, std::string>> configs;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char* board_state_text = sqlite3_column_text(stmt, 1);
        configs.push_back({id, std::string(reinterpret_cast<const char*>(board_state_text))});
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return configs;
}

void save_batch_to_csv(const std::vector<std::tuple<int, std::string, std::vector<std::string>>>& solutions, const std::string& filename) {
    if (solutions.empty()) {
        std::cout << "No solutions to save." << std::endl;
        return;
    }

    std::filesystem::create_directory("solutions_csv");
    std::ofstream file(std::filesystem::path("solutions_csv") / filename);

    file << "ID,Initial Board,Solution Path\n";
    for (const auto& sol : solutions) {
        file << std::get<0>(sol) << "," << std::get<1>(sol) << ",";
        const auto& path = std::get<2>(sol);
        for (size_t i = 0; i < path.size(); ++i) {
            file << path[i] << (i == path.size() - 1 ? "" : ";");
        }
        file << "\n";
    }
    std::cout << "Solutions for the batch saved to " << (std::filesystem::path("solutions_csv") / filename) << std::endl;
}

void load_heuristics(const std::string& path, std::unordered_map<std::string, int>& heuristics) {
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open heuristics file: " << path << std::endl;
        exit(1);
    }

    std::string line;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string board_config;
        std::string heur_val_str;

        if (std::getline(ss, board_config, ',') && std::getline(ss, heur_val_str)) {
            try {
heuristics[board_config] = std::stoi(heur_val_str);
            } catch (const std::invalid_argument& ia) {
                std::cerr << "Invalid argument: " << ia.what() << " for line: " << line << std::endl;
            } catch (const std::out_of_range& oor) {
                std::cerr << "Out of Range error: " << oor.what() << " for line: " << line << std::endl;
            }
        }
    }
}


