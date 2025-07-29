/* Function declarations */

#ifndef SAMPLE_BINARY_CORE_H
#define SAMPLE_BINARY_CORE_H

// Sample the matrix
std::pair<py::array_t<double>, double>
sample_symmetric_binary_matrix_core(const std::vector<int> &ks, int seed);

// Function to generate a sample table along with the (absolute) minus log
// probability that we sampled that table
std::pair<std::vector<std::vector<int>>, double>
sample_table(std::vector<int> ks);

// Sample the off-diagonal entries of the table given the remaining margin
// (passing the table by reference to be written)
double sample_off_diagonal_table(std::vector<std::vector<int>> &table,
                                 std::vector<int> &ks);
// Sample the rows one at a time (passing the table by reference to be written
// as well as the margin ks to be updated)
double sample_table_row(std::vector<std::vector<int>> &table,
                        std::vector<int> &ks, std::vector<int> &is);

#endif // SAMPLE_BINARY_CORE_H
