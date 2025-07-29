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
#include <vector>

#include "estimates.h"
#include "globals.h"
#include "helpers.h"
#include "preprocessing.h"
#include "sample_binary_core.h"

PYBIND11_MODULE(sample_binary_core, m) {
  m.doc() = R"pbdoc(
        Sample module
        -------------
        The module provides matrix sampling functionality.
    )pbdoc";

  m.def("sample_symmetric_binary_matrix_core",
        &sample_symmetric_binary_matrix_core, R"pbdoc(
        Sample a symmetric binary matrix with given margins.
        Returns a tuple containing a 2D NumPy array and the log probability of the sample.
    )pbdoc");
}

// Sample matrix function returning a 2D NumPy array and a float
std::pair<py::array_t<double>, double>
sample_symmetric_binary_matrix_core(const std::vector<int> &ks, int seed) {
  rng.seed(seed); // Set the random seed

  // Extract relevant metadata
  n = ks.size(); // Number of rows/columns, globally defined
  m = std::accumulate(ks.begin(), ks.end(), 0) /
      2; // Number of edges, globally defined
  max_row_sum = *std::max_element(
      ks.begin(), ks.end()); // Maximum of margin, globally defined

  // Generate a sample table along with the (absolute) minus log probability
  // that we sampled that table
  auto [table, entropy] = sample_table(ks);

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
sample_table(std::vector<int> ks) {
  // Initialize the table and the minus log probability
  std::vector<std::vector<int>> table; // Table to be returned
  for (int i = 0; i < n; i++) {
    std::vector<int> row(n, 0);
    table.push_back(row);
  }

  // Sample the off-diagonal entries of the table given the margin
  // (passing the table by reference to be written)
  double entropy = sample_off_diagonal_table(table, ks);

  // Return the table and the minus log probability
  return std::make_pair(table, entropy);
}

// Sample the off-diagonal entries of the table given the remaining margin
// (passing the table by reference to be written)
double sample_off_diagonal_table(std::vector<std::vector<int>> &table,
                                 std::vector<int> &ks) {
  // Sample the rows one at a time (passing the table by reference to be written
  // as well as the margin ks to be updated)
  double entropy = 0;
  std::vector<int> is = argsort(ks);
  // Which indices in the table are represented by the remaining degrees
  // (allows us to remove them as 0s appear and rows are sampled, also to keep
  // ks_left sorted) Make a copy of the degrees to be decremented as we sample
  std::vector<int> ks_left;
  for (int i = 0; i < n; i++) {
    ks_left.push_back(ks[is[i]]);
  }
  while (ks_left.size() > 0) {
    entropy += sample_table_row(
        table, ks_left, is); // Note that the new rows are written to the table
                             // as sampled within this function
    // Remove the rows that have degree 0
    std::vector<int> k_zero_inds;
    for (int i = 0; i < ks_left.size(); i++) {
      if (ks_left[i] == 0) {
        k_zero_inds.push_back(i);
      }
    }
    for (int i = k_zero_inds.size() - 1; i >= 0; i--) {
      int ind = k_zero_inds[i];
      is.erase(is.begin() + ind);
      ks_left.erase(ks_left.begin() + ind);
    }
    // Sort the remaining degrees and adjust the represented indices is
    // accordingly
    std::vector<int> remaining_sort = argsort(ks_left);
    std::vector<int> ks_left_new;
    std::vector<int> is_new;
    for (int j : remaining_sort) {
      is_new.push_back(is[j]);
      ks_left_new.push_back(ks_left[j]);
    }
    ks_left = ks_left_new;
    is = is_new;
  }
  return entropy;
}

// Sample the rows one at a time (passing the table by reference to be written
// as well as the margin ks to be updated)
double sample_table_row(std::vector<std::vector<int>> &table,
                        std::vector<int> &ks, std::vector<int> &is) {

  // Precompute the (log) power sums for each of the k[j:n],
  // log_power_sums[r][j] = \log(\sum_{i = j}^n i^r), precompute up to the total
  // we are considering
  std::vector<std::vector<double>> log_power_sums;
  for (int r = 0; r < ks[0] + 1; r++) {
    std::vector<double> log_power_sums_r;
    log_power_sums.push_back(log_power_sums_r);
  }
  for (int j = ks.size() - 1; j >= 0; j--) {
    for (int r = 0; r < ks[0] + 1; r++) {
      if (j == ks.size() - 1) {
        log_power_sums[r].push_back(r * std::log(ks[j]));
      } else {
        log_power_sums[r].insert(
            log_power_sums[r].begin(),
            r * std::log(ks[j]) + std::log(1 + std::exp(log_power_sums[r][0] -
                                                        r * std::log(ks[j]))));
      }
    }
  }

  // Pre-compute the log of the elementary symmetric polynomials, the sum of all
  // possible products of r distinct elements of ks[j:n]
  std::vector<std::vector<double>> log_elem_sym_polys;
  for (int r = 0; r < ks[0] + 1; r++) {
    std::vector<double> log_elem_sym_polys_r;
    for (int j = 0; j < ks.size(); j++) {
      log_elem_sym_polys_r.push_back(0);
    }
    log_elem_sym_polys.push_back(log_elem_sym_polys_r);
  }

  for (int j = 0; j < ks.size(); j++) {
    for (int r = 1; r < ks[0] + 1;
         r++) { // Can skip r = 1, since e_0 = 1 (log = 0)
      // e_r = \sum_{rr = 1}^r (-1)^{rr - 1} e_{r - rr} p_{rr}
      if (r > ks.size() - j) { // nan, there are no subsets of size r in the
                               // remaining degrees
        log_elem_sym_polys[r][j] = std::numeric_limits<double>::quiet_NaN();
      } else {
        // Challenge here is that some of the terms can be negative, although we
        // know the final result must be positive, so we will first collect the
        // positive and negative terms
        std::vector<double> log_positive_terms;
        std::vector<double> log_negative_terms;
        for (int rr = 1; rr <= r; rr++) {
          double log_term =
              log_elem_sym_polys[r - rr][j] + log_power_sums[rr][j];
          if ((rr - 1) % 2 == 0) { // (-1)^(rr - 1)
            log_positive_terms.push_back(log_term);
          } else {
            log_negative_terms.push_back(log_term);
          }
        }
        // Now we can sum the positive and negative terms separately
        double log_positive_terms_sum = log_sum_exp(log_positive_terms);
        double log_negative_terms_sum = log_sum_exp(log_negative_terms);
        // Combining them
        double log_result = log_positive_terms_sum +
                            std::log(1 - std::exp(log_negative_terms_sum -
                                                  log_positive_terms_sum));
        log_result -= std::log(r); // Divide by r
        log_elem_sym_polys[r][j] = log_result;
      }
    }
  }

  // Row to be written in
  std::vector<int> as;
  as.push_back(0); // The first entry is always 0
  double entropy = 0;
  // Loop through the entries of the row
  int n_left = ks.size(); // Number of remaining rows
  int as_total = 0;       // Total number of 1s already sampled in the row
  for (int i = 0; i < n_left - 1; i++) {
    int remaining_total = ks[0] - as_total;
    int remaining_to_sample = n_left - i - 1;
    int next_sample;
    double next_entropy;
    if (remaining_total == remaining_to_sample) {
      next_sample = 1;
      next_entropy = 0;
    } else if (remaining_total == 0) {
      next_sample = 0;
      next_entropy = 0;
    } else {
      // Check whether the the next entry can be 0 given the Erdos-Gallai
      // condition
      std::vector<int> ks_zero;
      for (int j = 1; j < n_left; j++) {
        if (j < as.size()) { // Write the margin which is the current sample
                             // followed by a 0 and then all the 1s leftmost.
          ks_zero.push_back(ks[j] - as[j]);
        } else if (j < as.size() + 1) {
          ks_zero.push_back(ks[j] - 0);
        } else if (j < as.size() + 1 + remaining_total) {
          ks_zero.push_back(ks[j] - 1);
        } else {
          ks_zero.push_back(ks[j] - 0);
        }
      }
      // Sort ks_zero to run from larest to smallest (before making the
      // erdos-gallai check)
      std::sort(ks_zero.begin(), ks_zero.end(), std::greater<int>());

      if (erdos_gallai_condition(ks_zero)) {
        // If a zero is possible, we use our estimate to compute the probability
        // of a 1
        double log_prob_one =
            std::log(ks[i + 1]) +
            log_elem_sym_polys[remaining_total - 1][i + 2] -
            log_sum_exp(log_elem_sym_polys[remaining_total][i + 2],
                        std::log(ks[i + 1]) +
                            log_elem_sym_polys[remaining_total - 1][i + 2]);
        auto [next_sample_unpack, next_entropy_unpack] =
            sample_bernoulli(std::exp(log_prob_one));
        next_sample = next_sample_unpack;
        next_entropy = next_entropy_unpack;
      } else {
        next_sample = 1; // If a zero is not possible, the 1 is forced
        next_entropy = 0;
      }
    }
    as.push_back(next_sample);
    as_total += next_sample;
    entropy += next_entropy;
  }

  // Write the sampled row to the table and subtract off from the margin
  for (int k_i = 0; k_i < n_left; k_i++) {
    table[is[0]][is[k_i]] = as[k_i];
    table[is[k_i]][is[0]] = table[is[0]][is[k_i]]; // Symmetric table
    ks[0] -= table[is[0]][is[k_i]];   // Update the (shifted) margin
    ks[k_i] -= table[is[k_i]][is[0]]; // Update the (shifted) margin
  }

  // Remove the first element of ks
  ks.erase(ks.begin());
  is.erase(is.begin());

  return entropy;
}
