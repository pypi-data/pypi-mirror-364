
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

#include "globals.h"
#include "helpers.h"
#include "preprocessing.h"

std::tuple<std::vector<int>, int> read_data(std::string input_filename) {
  // Read data from input_filename
  std::ifstream inputFile(input_filename);
  print(input_filename);

  if (!inputFile.is_open()) {
    std::cerr << "Error: could not open file " << input_filename << std::endl;
    exit(EXIT_FAILURE);
  }

  // Read the first line of the file
  std::string line;
  std::getline(inputFile, line);

  // Parse the line
  std::vector<int> ks;
  std::istringstream iss(line);
  int k;
  while (iss >> k) {
    ks.push_back(k);
  }

  // If there is no second line we will assume that the diagonal sum is
  // unconstrained
  if (inputFile.eof()) {
    return std::make_tuple(
        ks, -1); // m_in = -1 represents that the diagonal sum is unconstrained
  }

  // Read the second line of the file
  std::getline(inputFile, line);

  // Parse the line
  int m_in;
  std::istringstream iss2(line);
  iss2 >> m_in;
  if (m_in < 0) { // Margin sum must be positive
    std::cerr << "Error: margin sum must be positive.\n";
    exit(EXIT_FAILURE);
  }

  // Remove any 0s from the margin
  ks.erase(std::remove(ks.begin(), ks.end(), 0), ks.end());

  return std::make_tuple(ks, m_in);
}

// Check whether there are any solutions to the input margins with the given
// diagonal sum
void validate_input(std::vector<int> ks, int m_in) {
  // Check that the margin sum is appropriate
  int ks_sum = std::accumulate(ks.begin(), ks.end(), 0);
  // If the margin sum is odd, no solutions can exist
  if (ks_sum % 2 != 0) {
    std::cerr << "Error: no solutions can exist for the odd margin sum of "
              << ks_sum << std::endl;
    exit(EXIT_FAILURE);
  }
  if (ks_sum <= 0) {
    std::cerr
        << "Error: no solutions can exist for the non-positive margin sum of "
        << ks_sum << std::endl;
    exit(EXIT_FAILURE);
  }
  int m = ks_sum / 2; // Number of edges is half of the margin sum

  // Minimum allowable diagonal sum
  int ks_max = *std::max_element(ks.begin(), ks.end());
  int m_in_min = ks_max - m;
  if (m_in_min < 0) { // Also must be at least 0
    m_in_min = 0;
  }

  // Maximum allowable diagonal sum
  int m_in_max = 0;
  for (int k : ks) {
    m_in_max += std::floor(k / 2);
  }

  // Check that diagonal sum is appropriate
  if (m_in == -1) { // Unconstrained diagonal sum, make sure that there exists a
                    // valid value
    if (m_in_min > m_in_max) {
      std::cerr << "Error: no solutions can exist for the given margins."
                << std::endl;
      exit(EXIT_FAILURE);
    }
  } else {
    if (m_in < m_in_min || m_in > m_in_max) {
      std::cerr << "Error: no solutions can exist for the given margins and "
                   "diagonal sum."
                << std::endl;
      exit(EXIT_FAILURE);
    }
  }
}
