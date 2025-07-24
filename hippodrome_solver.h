
#ifndef HIPPODROME_SOLVER_H
#define HIPPODROME_SOLVER_H

#include <string>
#include <unordered_map>

extern std::unordered_map<std::string, int> g_knightHeur;

void load_heuristics(const std::string& filename, std::unordered_map<std::string, int>& heuristics);
int get_heuristic(const std::string& board_state, const std::unordered_map<std::string, int>& heuristics);
int calculate_heuristic(const std::string& board_state);

#endif

