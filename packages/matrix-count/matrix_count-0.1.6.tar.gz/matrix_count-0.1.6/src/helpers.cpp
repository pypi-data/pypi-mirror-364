/* Implementations of helper functions */

#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <vector>

#include "globals.h"
#include "helpers.h"

// Logarithm of the binomial coefficient
double log_binom(double a, double b) {
  if (b == 0) {
    return 0;
  }
  return std::lgamma(a + 1) - std::lgamma(b + 1) - std::lgamma(a - b + 1);
}

// Logarithm of the factorial
double log_factorial(int n) { return std::lgamma(n + 1); }

// Logarithm of the double factorial
double log_factorial2(int n) {
  // Check that n is an even integer
  if (n % 2 != 0) {
    std::cout << "Error: log_factorial2 called with odd integer.\n";
    exit(0);
  }
  return n / 2 * std::log(2) + std::lgamma(n / 2 + 1);
}

// Overflow protected version of log(e^a + e^b)
double log_sum_exp(double a, double b) {
  double a_b_max = std::max(a, b);
  return a_b_max + std::log(std::exp(a - a_b_max) + std::exp(b - a_b_max));
}

// Overflow protected version of log(\sum exp(x_i))
double log_sum_exp(std::vector<double> xs) {
  if (xs.size() == 0) {
    return -std::numeric_limits<double>::infinity();
  }
  double xs_max = *std::max_element(xs.begin(), xs.end());
  double result = 0;
  for (double x : xs) {
    result += std::exp(x - xs_max);
  }
  return xs_max + std::log(result);
}

// Sample from a set of outcomes given log weights (not necessarily normalized),
// also return the entropy of that choice
std::pair<int, double> sample_log_weights(std::vector<double> log_weights) {
  // Normalize the weights
  double log_sum = log_sum_exp(log_weights);
  std::vector<double> weights;
  weights.reserve(log_weights.size()); // Reserve memory for weights
  for (double log_weight : log_weights) {
    weights.push_back(std::exp(log_weight - log_sum));
  }

  // Sample according to these weights (this is where all the randomness comes
  // from), use the global rng mersenne twister
  double p = dis(rng);
  double culm_weight = 0.0;
  for (int i = 0; i < weights.size(); ++i) {
    culm_weight += weights[i];
    if (p <= culm_weight) {
      return std::make_pair(i, -std::log(weights[i]));
    }
  }
  // If no match found, return the last element as a fallback (due to rounding
  // issues)
  return std::make_pair(weights.size() - 1, -std::log(weights.back()));
}

// Sample from a bernoulli distribution with given probability
std::pair<int, double> sample_bernoulli(double p) {
  double r = dis(rng);
  if (r < p) {
    return std::make_pair(1, -std::log(p));
  } else {
    return std::make_pair(0, -std::log(1 - p));
  }
}

// Return the indices perm which label the row sums from largest to smallest
template <typename T> std::vector<int> argsort(const std::vector<T> &array) {
  std::vector<int> indices(array.size());
  std::iota(indices.begin(), indices.end(), 0);
  std::sort(indices.begin(), indices.end(),
            [&array](int left, int right) -> bool {
              // sort indices according to corresponding array element
              return array[left] > array[right];
            });

  return indices;
}

// Explicit instantiation of template function for int type
template std::vector<int> argsort<int>(const std::vector<int> &array);

// Erdos-Gallai condition for a degree sequence (whether a simple graph with
// this degree sequence exists)
bool erdos_gallai_condition(const std::vector<int> &ks) {
  int n = ks.size();
  int sum_k = 0;
  for (int i = 0; i < n; i++) {
    sum_k += ks[i];
  }
  if (sum_k % 2 != 0) {
    return false;
  }
  for (int l = 1; l <= n; l++) {
    int sum_l = 0;
    for (int i = 0; i < l; i++) {
      sum_l += ks[i];
    }
    int sum_min = 0;
    for (int i = l; i < n; i++) {
      sum_min += std::min(ks[i], l);
    }
    if (sum_l > l * (l - 1) + sum_min) {
      return false;
    }
  }
  return true;
}

// Tools for reading and writing from the unordered_map of log_g_i_sP_sT (note
// that this hash can run into issues once we overflow)
void write_log_g_i_sP_sT(int i, int s_prev, int s_this, double val) {
  log_g_i_sP_sT_map[i * (m + 1) * (m + 1) + s_prev * (m + 1) + s_this] = val;
}

double get_log_g_i_sP_sT(int i, int s_prev, int s_this) {
  if (log_g_i_sP_sT_map.find(i * (m + 1) * (m + 1) + s_prev * (m + 1) +
                             s_this) == log_g_i_sP_sT_map.end()) {
    return -std::numeric_limits<double>::infinity(); // Everything not written
                                                     // defaults to 0
  } else {
    return log_g_i_sP_sT_map[i * (m + 1) * (m + 1) + s_prev * (m + 1) + s_this];
  }
}

// Printing functions (useful for debugging)
// Print function which calls print on all arguments
// template <typename T, typename... Args>
// void print(T t, Args... args){
//     std::cout << t << " ";
//     print(args...);
// }

void print(std::vector<std::vector<int>> table) {
  for (int i = 0; i < table.size(); i++) {
    for (int j = 0; j < table[0].size(); j++) {
      std::cout << table[i][j] << ' ';
    }
    std::cout << "\n";
  }
}
void print(std::vector<std::vector<double>> table) {
  for (int i = 0; i < table.size(); i++) {
    for (int j = 0; j < table[0].size(); j++) {
      std::cout << table[i][j] << ' ';
    }
    std::cout << "\n";
  }
}
void print(std::vector<int> vec) {
  for (int n = 0; n < vec.size(); ++n)
    std::cout << vec[n] << ' ';
  std::cout << '\n';
}
void print(std::vector<double> vec) {
  for (int n = 0; n < vec.size(); ++n)
    std::cout << vec[n] << ' ';
  std::cout << '\n';
}
void print(int val) { std::cout << val << std::endl; }
void print(double val) { std::cout << val << std::endl; }
void print(std::string val) { std::cout << val << std::endl; }
