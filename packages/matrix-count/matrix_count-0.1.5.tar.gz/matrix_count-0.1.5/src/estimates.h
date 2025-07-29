#ifndef ESTIMATES_H
#define ESTIMATES_H

double alpha_unconstrained(int n, int m);
double alpha_constrained(int n, int m, int m_in);
double alpha_zero_diagonal(int n, int m);
double log_Omega_fixed_diagonal(std::vector<int> ks, int m_in);
double log_Omega_unconstrained_diagonal(std::vector<int> ks);

#endif // ESTIMATES_H
