// Functions relevant for the moment-matching approximations of the number of
// matrices

#include <cstdio>
#include <numeric>
#include <vector>

#include "estimates.h"
#include "globals.h"
#include "helpers.h"

// Logarithm of the estimate for the number of symmetric tables with given
// margin and diagonal sum
double log_Omega_fixed_diagonal(std::vector<int> ks, int m_in) {
  // Extract relevant metadata
  int n = ks.size(); // Number of rows/columns
  int m = std::accumulate(ks.begin(), ks.end(), 0) / 2; // Number of edges
  // Get the alpha value
  double alpha;
  if (m_in == 0) {
    alpha = alpha_zero_diagonal(n, m);
  } else {
    alpha = alpha_constrained(n, m, m_in);
  }

  // Calculate the log of the estimate
  int m_out = m - m_in;
  double log_Omega =
      log_binom(m_out + n * (n - 1) / 2 - 1, n * (n - 1) / 2 - 1) +
      log_binom(m_in + n - 1, n - 1) -
      log_binom(2 * m + n * alpha - 1, n * alpha - 1);
  for (int i = 0; i < n; i++) {
    log_Omega += log_binom(ks[i] + alpha - 1, alpha - 1);
  }

  return log_Omega;
}

// Logarithm of the estimate for the number of symmetric tables with given
// margin and unconstrained diagonal sum
double log_Omega_unconstrained_diagonal(std::vector<int> ks) {
  // Extract relevant metadata
  int n = ks.size(); // Number of rows/columns
  int m = std::accumulate(ks.begin(), ks.end(), 0) / 2; // Number of edges

  // Get the alpha value
  double alpha = alpha_unconstrained(n, m);

  // Calculate the log of the estimate
  double log_Omega = log_binom(m + n * (n + 1) / 2 - 1, n * (n + 1) / 2 - 1) -
                     log_binom(2 * m + n * alpha - 1, n * alpha - 1);
  for (int i = 0; i < n; i++) {
    log_Omega += log_binom(ks[i] + alpha - 1, alpha - 1);
  }
  return log_Omega;
}

// alpha parameter for an unconstrained diagonal sum
double alpha_unconstrained(int n, int m) {
  double numerator = 2 * m * (n * n + 2 * n + 2) - (n + 1) * (n + 2);
  double denominator = 2 * m * (n + 2) + (n + 1) * (n - 2);
  double result = numerator / (denominator + ALPHA_EPSILON);
  return result;
}

// alpha parameter for a fixed diagonal sum
double alpha_constrained(int n, int m, int m_in) {
  double mu = (m - m_in) / double(m);
  double numerator =
      2 * (-1 + m) * (-1 + n) * n * (2 + (-1 + n) * n) +
      mu * (-1 + n) * (4 * m * (2 + (-1 + n) * n) + n * (6 + (-1 + n) * n)) +
      2 * m * mu * mu * (4 + n * (-2 + n - n * n));

  // Calculate the denominator
  double denominator =
      n *
      ((-1 + n) * (-1 + 2 * m + n) * (2 + (-1 + n) * n) +
       2 * m * mu * mu * (-4 + n * (2 + (-1 + n) * n)) -
       mu * (-1 + n) * (4 * m * (2 + (-1 + n) * n) + n * (6 + (-1 + n) * n)));

  // Calculate the result
  double result = numerator / (denominator + ALPHA_EPSILON);

  // Switch a negative result to inf
  if (result < 0) {
    result = 10000.0;
  }

  return result;
}

// alpha parameter for zero digaonal sum (case of fixed, but the expression
// simplifies)
double alpha_zero_diagonal(int n, int m) {
  // Calculate the numerator
  double numerator = -((-2 + n) * (-1 + n)) + 2 * m * (2 + (-2 + n) * n);

  // Calculate the denominator
  double denominator = 2 + 2 * m * (-2 + n) - n - n * n;

  // Calculate the result
  double result = numerator / (denominator + ALPHA_EPSILON);

  // Switch a negative result to inf
  if (result < 0) {
    result = 10000.0;
  }

  return result;
}
