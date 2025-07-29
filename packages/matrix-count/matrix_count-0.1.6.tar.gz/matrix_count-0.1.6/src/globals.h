/* Global variable declarations */

#ifndef GLOBALS_H
#define GLOBALS_H

#include <random>
#include <unordered_map>

// Global information about the problem
inline int n;
inline int m;
inline double alpha;
inline int max_row_sum;

// Constants
inline double ALPHA_EPSILON =
    1e-7; // Small constant to add to the alpha parameter to avoid poles

// Hash map for storing the values in the dynamic programming algorithm
inline std::unordered_map<int, double> log_g_i_sP_sT_map;

inline std::random_device rd;
inline std::mt19937 rng(rd()); // Initialize Mersenne Twister (global RNG)
inline std::uniform_real_distribution<double>
    dis(0.0, 1.0); // Uniform distribution on [0,1]

#endif // GLOBALS_H
