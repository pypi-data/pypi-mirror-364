#include <pybind11/numpy.h> // To support NumPy array conversions
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // To support std::vector conversions
#include <random>

namespace py = pybind11;

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

#include "estimates.h"
#include "globals.h"
#include "helpers.h"
#include "preprocessing.h"
#include "sample_core.h"

PYBIND11_MODULE(sample_core, m) {
  m.doc() = R"pbdoc(
        Sample module
        -------------
        The module provides matrix sampling functionality.
    )pbdoc";

  m.def("sample_symmetric_matrix_core", &sample_symmetric_matrix_core, R"pbdoc(
        Sample a symmetric matrix with given margins and Dirichlet-Multinomial weighting.
        Returns a tuple containing a 2D NumPy array and the log probability of the sample.
    )pbdoc");
}

// Sample matrix function returning a 2D NumPy array and a float
std::pair<py::array_t<double>, double>
sample_symmetric_matrix_core(const std::vector<int> &ks, int diagonal_sum,
                             double alpha_input, int seed) {
  rng.seed(seed); // Set the random seed

  // Extract relevant metadata
  n = ks.size(); // Number of rows/columns, globally defined
  m = std::accumulate(ks.begin(), ks.end(), 0) /
      2;               // Number of edges, globally defined
  alpha = alpha_input; // Alpha parameter, globally defined

  int m_in;
  if (diagonal_sum == -1) { // Unconstrained diagonal sum
    m_in = -1;
  } else {
    m_in = diagonal_sum / 2;
  }

  // Generate a sample table along with the (absolute) minus log probability
  // that we sampled that table
  auto [table, entropy] = sample_table(ks, m_in);

  // Convert to numpy array
  py::array_t<double> matrix({n, n});
  auto r = matrix.mutable_unchecked<2>(); // raw access to array data

  for (size_t i = 0; i < n; ++i) {
    for (size_t j = 0; j < n; ++j) {
      r(i, j) = table[i][j];
    }
  }

  return std::make_pair(matrix, entropy);
}

// Function to generate a sample table along with the (absolute) minus log
// probability that we sampled that table
std::pair<std::vector<std::vector<int>>, double>
sample_table(std::vector<int> ks, int m_in) {
  // Initialize the table and the minus log probability
  std::vector<std::vector<int>> table; // Table to be returned
  for (int i = 0; i < n; i++) {
    std::vector<int> row(n, 0);
    table.push_back(row);
  }

  double entropy = 0;

  if (m_in == -1) { // Unconstrained diagonal sum
    // Replace with an appropriately sampled value
    auto [m_in_sampled, diagonal_sum_entropy] = sample_diagonal_sum(ks);
    m_in = m_in_sampled;
    entropy += diagonal_sum_entropy;
  }

  // Sample the diagonal entries of the table among the possibilities with the
  // appropriate total
  auto [diagonal_entries, diagonal_entries_entropy] =
      sample_diagonal_entries(ks, m_in);
  entropy += diagonal_entries_entropy;

  // Write the diagonal entries to the table and adjust the remaining margin
  for (int i = 0; i < n; i++) {
    table[i][i] = 2 * diagonal_entries[i];
  }

  // Sample the off-diagonal entries of the table given the remaining margin
  // (passing the table by reference to be written)
  double off_diag_entropy = sample_off_diagonal_table(table, ks, m_in);
  entropy += off_diag_entropy;

  // Return the table and the minus log probability
  return std::make_pair(table, entropy);
}

// Sample the diagonal sum of a symmetric table with given margin (and return
// the entropy that sample)
std::pair<int, double> sample_diagonal_sum(std::vector<int> ks) {
  // Calculate the bounds of possible diagonal sums

  // Note that this could all be computed once globally, although the cost isn't
  // too high anyway.
  std::vector<int> valid_m_ins; // valid values of m_in (Note that this does not
                                // need to be a continuous range, for example ks
                                // = {2,2,2,2} gives m_in = {0,1,2,4}.)
  for (int m_in = 0; m_in <= m; m_in++) {
    int m_out = m - m_in;
    int m_in_min = 0;
    int m_in_max = 0;
    for (int i = 0; i < n; i++) {
      m_in_min +=
          std::max(0.0, std::ceil(static_cast<double>(ks[i] - m_out) / 2));
      m_in_max += std::floor(static_cast<double>(ks[i]) / 2);
    }
    if (m_in_min <= m_in && m_in <= m_in_max) {
      valid_m_ins.push_back(m_in);
    }
  }

  // Get the (log) counts for the number of possible matrices for the valid
  // diagonal sums
  std::vector<double> log_counts;
  for (int m_in : valid_m_ins) {
    log_counts.push_back(log_Omega_fixed_diagonal(ks, m_in));
  }

  // If we globally compute the above this can just be done once.
  auto [m_in_index, entropy] =
      sample_log_weights(log_counts); // Sample the index of the log_counts
  return std::make_pair(valid_m_ins[m_in_index],
                        entropy); // Return the corresponding diagonal sum
}

// Sample the diagonal entries of a symmetric table with given margin and
// diagonal sum (and give entropy of that choice)
std::pair<std::vector<int>, double> sample_diagonal_entries(std::vector<int> ks,
                                                            int m_in) {
  int m_out = m - m_in; // Number of off-diagonal edges
  if (m_in < 0) {
    print("Error: m_in negative");
    exit(1);
  }
  if (m_out < 0) {
    print("Error: m_out negative");
    exit(1);
  }

  // Use dynamic programming to compute the log_g values. Implementing the
  // recursion g_n(s_{n-1},s_n) = h_n(s_{n-1},s_n) g_i(s_{i-1},s_i) =
  // h_i(s_{i-1},s_i)*\sum_{s_i} g_{i+1}(s_i,s_{i+1}) where h_i(s_{i-1},s_i) =
  // binom(k_i-2 d_i + alpha_DM - 1, alpha_DM -
  // 1)*1{0,(k_i-m_out)/2<=d_i<=k_i/2} and the s_i variables are the cumulative
  // sum of (half) the diagonal entries up to row i so that d_i = s_i - s_{i-1}
  // is the entry A_{i,i}/2 of the final table. We use variable names s_prev =
  // s_{i-1}, s_this = s_i, s_next = s_{i+1}, d_this = d_i, d_next = d_{i+1}
  // Note that the i range from 1 to n in these expressions, although the code
  // will be 0-indexed. So for example k_i = ks[i-1], s_i = s[i-1], etc.

  // These are going to be weighted by the number of symmetric matrices that can
  // fill the off-diagonal entries (i.e. zero diagonal sum)
  double alpha_DM = alpha_zero_diagonal(n, m_out) +
                    ALPHA_EPSILON; // The relevant alpha for the approximation

  // For efficiency we only loop over s_{i} with possibly nonzero \sum_{s_{i+1}}
  // g_i(s_i, s_{i+1})
  std::vector<int> min_s_this(n + 1,
                              10000);     // Track the smallest s_i with nonzero
                                          // \sum_{s_{i+1}} g_i(s_i, s_{i+1})
  std::vector<int> max_s_this(n + 1, -1); // Track the largest s_i with nonzero
                                          // \sum_{s_{i+1}} g_i(s_i, s_{i+1})

  min_s_this[n] = m_in; // For the last entry, the total sum of the diagonal
                        // entries is m_in by definition.
  max_s_this[n] = m_in;

  for (int i = n - 1; i >= 0; i--) {
    // 1{0,(k_i-m_out)/2<=d_i<=k_i/2}, bounds for the current degree
    int d_min = std::max(0.0, std::ceil(static_cast<double>(ks[i] - m_out) /
                                        2)); // 0,(k_i-m_out)/2<=d_i
    int d_max = std::floor(static_cast<double>(ks[i]) / 2); // d_i<=k_i/2

    if (i == n - 1) { // g_n(s_{n-1},s_n) = h_n(s_{n-1},s_n)
      for (int d_this = d_min; d_this <= std::min(d_max, m_in);
           d_this++) {              // 0,(k_i-m_out)/2<=d_i<=k_i/2
        int s_prev = m_in - d_this; // s_{i-1}
        int s_this = m_in;          // s_i
        // g_i(s_{i-1},s_i) = h_i(s_{i-1},s_i) = binom(k_i-2 d_i + alpha_DM - 1,
        // alpha_DM - 1)
        write_log_g_i_sP_sT(
            i, s_prev, s_this,
            log_binom(ks[i] - 2 * d_this + alpha_DM - 1, alpha_DM - 1));
      }
      min_s_this[i] =
          std::max(0, m_in - d_max); // The smallest s_i with nonzero
                                     // \sum_{s_{i+1}} g_i(s_i, s_{i+1})
      max_s_this[i] = m_in - d_min;  // The largest s_i with nonzero
                                     // \sum_{s_{i+1}} g_i(s_i, s_{i+1})
    } else {
      // Range of valid d[i+1], for finding the contributing
      // g_{i+1}(s_i,s_{i+1}) 0,(k_{i+1}-m_out)/2<=d_{i+1}<=k_{i+1}/2
      int d_next_min =
          std::max(0.0, std::ceil(static_cast<double>(ks[i + 1] - m_out) / 2));
      int d_next_max = std::floor(static_cast<double>(ks[i + 1]) / 2);
      // g_i(s_{i-1},s_i) = h_i(s_{i-1},s_i)*\sum_{s_i} g_{i+1}(s_i,s_{i+1})
      for (int s_this = min_s_this[i + 1]; s_this <= max_s_this[i + 1];
           s_this++) { // Writing in the nonzero log g_n(s_{i-1},s_i)
        for (int d_this = d_min; d_this <= std::min(d_max, s_this);
             d_this++) {                // Also ensure that s_{i-1} >= 0
          int s_prev = s_this - d_this; // s_{i-1}
          if (i != 0 || s_prev == 0) {  // The first s_{i-1} is always 0
            double log_h =
                log_binom(ks[i] - 2 * d_this + alpha_DM - 1, alpha_DM - 1);
            std::vector<double> log_gs; // The log(g) values that the next g is
                                        // defined as a sum over.
            for (int d_next = d_next_min;
                 d_next <= std::min(d_next_max, m_in - s_this);
                 d_next++) {                // Make sure that s_{i+1} <= m_in
              int s_next = s_this + d_next; // s_{i+1}
              if (i != n - 2 ||
                  s_next == m_in) { // The last s_{i+1} is always m_in
                log_gs.push_back(get_log_g_i_sP_sT(i + 1, s_this, s_next));
              }
            }
            write_log_g_i_sP_sT(i, s_prev, s_this, log_h + log_sum_exp(log_gs));
            // Update the min_s_this and max_s_this
            if (s_prev < min_s_this[i]) {
              min_s_this[i] = s_prev;
            }
            if (s_prev > max_s_this[i]) {
              max_s_this[i] = s_prev;
            }
          }
        }
      }
    }
  }

  // Sample from the distribution given by the g
  std::vector<int> ds;
  double entropy = 0;
  int s_prev = 0;
  for (int i = 0; i < n; i++) {
    int d_min =
        std::max(0.0, std::ceil(static_cast<double>(ks[i] - m_out) / 2));
    int d_max = std::floor(static_cast<double>(ks[i]) / 2);
    std::vector<double> weights; // Weights given by the valid weights
    std::vector<int> d_choices;  // Choices of degree
    for (int d_this = d_min; d_this <= std::min(d_max, m_in - s_prev);
         d_this++) { // Make sure that s_{i} <= m_in
      int s_this = s_prev + d_this;
      if (s_this >= min_s_this[i + 1] &&
          s_this <= max_s_this[i + 1]) { // Make sure that the resulting s_this
                                         // is valid
        if (i != n - 1 || s_this == m_in) {
          weights.push_back(get_log_g_i_sP_sT(i, s_prev, s_this));
          d_choices.push_back(d_this);
        }
      }
    }
    auto [d_this_index, d_entropy] = sample_log_weights(weights);
    entropy += d_entropy;
    int d_this = d_choices[d_this_index];
    ds.push_back(d_this);
    s_prev += d_this;
  }

  return std::make_pair(ds, entropy);
}

// Sample the off-diagonal entries of the table given the remaining margin
// (passing the table by reference to be written)
double sample_off_diagonal_table(std::vector<std::vector<int>> &table,
                                 std::vector<int> &ks, int m_in) {
  // Sample the rows one at a time (passing the table by reference to be written
  // as well as the margin ks to be updated)
  double entropy = 0;
  // Make a copy of the degrees to be decremented as we sample
  std::vector<int> ks_left;
  for (int i = 0; i < n; i++) {
    ks_left.push_back(ks[i] - table[i][i]);
  }
  std::vector<int>
      is; // Which indices in the table are represented by the remaining degrees
          // (allows us to remove them as 0s appear and rows are sampled)
  for (int i = 0; i < n; i++) {
    is.push_back(i);
  }
  for (int i = 0; i < n; i++) {
    // Clear the unordered map
    log_g_i_sP_sT_map.clear();

    entropy += sample_table_row(table, ks_left, is);
  }
  return entropy;
}

// Sample the rows one at a time (passing the table by reference to be written
// as well as the margin ks to be updated)
double sample_table_row(std::vector<std::vector<int>> &table,
                        std::vector<int> &ks, std::vector<int> &is) {
  // Remove the rows that have degree 0
  std::vector<int> k_zero_inds;
  for (int i = 0; i < is.size(); i++) {
    if (ks[i] == 0) {
      k_zero_inds.push_back(i);
    }
  }
  for (int i = k_zero_inds.size() - 1; i >= 0; i--) {
    int ind = k_zero_inds[i];
    is.erase(is.begin() + ind);
    ks.erase(ks.begin() + ind);
  }
  int n_left = ks.size(); // Number of remaining rows
  int m_out = std::accumulate(ks.begin(), ks.end(), 0) /
              2; // Number of remaining off-diagonal edges
  if (n_left == 0) {
    return 0;
  }

  // Sample the top row, assuming that all of the diagonal values are 0 (a
  // length n_left - 1 vector that sums to ks[0]) Use dynamic programming to
  // compute the log_g values If the number left is 4 or less, we can set alpha
  // = 1 since all remaining configurations are equally likely (single solution)
  double alpha_DM;
  if (n_left <= 4) {
    alpha_DM = 1;
  } else {
    alpha_DM = alpha_zero_diagonal(n_left - 1, 2 * m_out - 2 * ks[0]) +
               ALPHA_EPSILON; // The relevant alpha for the approximation
  }

  // For efficiency we only loop over s_{i} with possibly nonzero \sum_{s_{i+1}}
  // g_i(s_i, s_{i+1})
  std::vector<int> min_s_this(n_left,
                              10000); // Track the smallest s_i with nonzero
                                      // \sum_{s_{i+1}} g_i(s_i, s_{i+1})
  std::vector<int> max_s_this(n_left, -1); // Track the largest s_i with nonzero
                                           // \sum_{s_{i+1}} g_i(s_i, s_{i+1})

  min_s_this[n_left - 1] = ks[0];
  max_s_this[n_left - 1] = ks[0];

  for (int i = n_left - 1 - 1; i >= 0; i--) {
    int a_min = std::max(0, ks[i + 1] + ks[0] - m_out);
    int a_max = ks[i + 1];
    if (i == n_left - 1 - 1) { // Should just be equal to the log_h
      for (int a_this = a_min; a_this <= std::min(a_max, ks[0]);
           a_this++) { // The range of valid a[i], writing in the nonzero log
                       // g_n(s_{i-1},s_i), make sure s_prev >= 0
        int s_prev = ks[0] - a_this; // s_{i-1}
        int s_this = ks[0];          // s_i
        write_log_g_i_sP_sT(i, s_prev, s_this,
                            log_binom(ks[i + 1] - a_this + alpha_DM - 1,
                                      alpha_DM - 1)); // log h_i(s_{i-1},s_i)
      }
      min_s_this[i] =
          std::max(0, ks[0] - a_max); // The smallest s_i with nonzero
                                      // \sum_{s_{i+1}} g_i(s_i, s_{i+1})
      max_s_this[i] = ks[0] - a_min;  // The largest s_i with nonzero
                                      // \sum_{s_{i+1}} g_i(s_i, s_{i+1})
    } else {
      // Range of valid d[i+1], for finding the contributing
      // g_{i+1}(s_i,s_{i+1})
      int a_next_min = std::max(0, ks[i + 2] + ks[0] - m_out);
      int a_next_max = ks[i + 2];
      // g_i(s_{i-1},s_i) = h_i(s_{i-1},s_i)*\sum_{s_i} g_{i+1}(s_i,s_{i+1})
      for (int s_this = min_s_this[i + 1]; s_this <= max_s_this[i + 1];
           s_this++) { // Writing in the nonzero log g_n(s_{i-1},s_i)
        for (int a_this = a_min; a_this <= std::min(a_max, s_this);
             a_this++) {                // Also ensure that s_{i-1} >= 0
          int s_prev = s_this - a_this; // s_{i-1}
          if (i != 0 || s_prev == 0) {  // The first s_{i-1} is always 0
            double log_h = log_binom(ks[i + 1] - a_this + alpha_DM - 1,
                                     alpha_DM - 1); // log h_i(s_{i-1},s_i)
            std::vector<double> log_gs; // The log(g) values that the next g is
                                        // defined as a sum over.
            for (int a_next = a_next_min;
                 a_next <= std::min(a_next_max, ks[0] - s_this);
                 a_next++) {                // Make sure that s_{i+1} <= m_in
              int s_next = s_this + a_next; // s_{i+1}
              if (i != n_left - 1 - 1 - 1 ||
                  s_next == ks[0]) { // The last s_{i+1} is always ks[0]
                log_gs.push_back(get_log_g_i_sP_sT(i + 1, s_this, s_next));
              }
            }
            write_log_g_i_sP_sT(i, s_prev, s_this, log_h + log_sum_exp(log_gs));
            // Update the min_s_this and max_s_this
            if (s_prev < min_s_this[i]) {
              min_s_this[i] = s_prev;
            }
            if (s_prev > max_s_this[i]) {
              max_s_this[i] = s_prev;
            }
          }
        }
      }
    }
  }

  // Sample from the distribution given by the g
  std::vector<int> as;
  double entropy = 0;
  int s_prev = 0;
  for (int i = 0; i < n_left - 1; i++) {
    int a_min = std::max(0, ks[i + 1] + ks[0] - m_out);
    int a_max = ks[i + 1];
    std::vector<double> weights; // Weights given by the valid weights
    std::vector<int> a_choices;  // Choices of degree
    for (int a_this = a_min; a_this <= std::min(a_max, ks[0] - s_prev);
         a_this++) { // Make sure that s_{i} <= ks[0]
      int s_this = s_prev + a_this;
      if (s_this >= min_s_this[i + 1] &&
          s_this <= max_s_this[i + 1]) { // Make sure that the resulting s_this
                                         // is valid
        if (i != n_left - 1 - 1 || s_this == ks[0]) {
          weights.push_back(get_log_g_i_sP_sT(i, s_prev, s_this));
          a_choices.push_back(a_this);
        }
      }
    }
    auto [a_this_index, d_entropy] = sample_log_weights(weights);
    entropy += d_entropy;
    int a_this = a_choices[a_this_index];
    as.push_back(a_this);
    s_prev += a_this;
  }

  // Write the sampled row to the table and update the degrees
  int i = n - n_left; // Number of rows already sampled
  for (int k_i = 0; k_i < n_left - 1; k_i++) {
    table[is[0]][is[k_i + 1]] = as[k_i];
    table[is[k_i + 1]][is[0]] = table[is[0]][is[k_i + 1]]; // Symmetric table
    ks[0] -= table[is[0]][is[k_i + 1]];       // Update the (shifted) margin
    ks[k_i + 1] -= table[is[k_i + 1]][is[0]]; // Update the (shifted) margin
  }
  // Remove the first element of ks and is
  ks.erase(ks.begin());
  is.erase(is.begin());
  return entropy;
}
