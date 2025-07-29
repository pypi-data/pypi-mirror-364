/* Function declarations */

#ifndef SAMPLE_CORE_H
#define SAMPLE_CORE_H

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

// Sample the matrix
std::pair<py::array_t<double>, double>
sample_symmetric_matrix_core(const std::vector<int> &ks, int diagonal_sum,
                             double alpha_input, int seed);

// Function to generate a sample table along with the (absolute) minus log
// probability that we sampled that table
std::pair<std::vector<std::vector<int>>, double>
sample_table(std::vector<int> ks, int m_in);

// Sample the diagonal sum of a symmetric table with given margin
std::pair<int, double> sample_diagonal_sum(std::vector<int> ks);

// Sample the diagonal entries of a symmetric table with given margin and
// diagonal sum
std::pair<std::vector<int>, double> sample_diagonal_entries(std::vector<int> ks,
                                                            int m_in);

// Sample the off-diagonal entries of the table given the remaining margin
// (passing the table by reference to be written)
double sample_off_diagonal_table(std::vector<std::vector<int>> &table,
                                 std::vector<int> &ks, int m_in);

// Sample the rows one at a time (passing the table by reference to be written
// as well as the margin ks to be updated)
double sample_table_row(std::vector<std::vector<int>> &table,
                        std::vector<int> &ks, std::vector<int> &is);

#endif // SAMPLE_CORE_H
