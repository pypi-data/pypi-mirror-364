# Script to generate the test margins used to assess the performance of the symmetric multigraph estimates 
# as the size n and number of edges m vary. 

import matrix_count
import pandas as pd
import numpy as np
import sys
import os

filename = "test_margins_binary.csv"

# Seed the rng for repeatability
np.random.seed(0)

# Sample from a Dirichlet-Multinomial distribution
def sample_dirichlet_multinomial(total, size, alpha):
    p = np.random.dirichlet([alpha] * size)
    return np.random.multinomial(total, p)

# Sample margin (only return non-negative margins)
def sample_margin(n, m):
    margin = sample_dirichlet_multinomial(2*m - n, n, 1)
    return margin + 1

# Values of m and n to test
n_values = [8, 16, 32, 64, 128, 256, 512, 1024, 2048] # Size of the matrix
m_values = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800] # Number of edges

# Number of samples to generate for each value of m and n
num_samples = 10

df_dict = {"n": [], "m": [], "margin": [], "true_log_count": [], "true_log_count_err": [], "estimate_mult": [], "estimate_DM": []}

# Generate the margins
for n in n_values:
    for m in m_values:
        if n < 2*m:
            print(f"Generating margins for n: {n}, m: {m}")
            num_valid_samples = 0
            for sample_num in range(1000):
                if num_valid_samples < num_samples:
                    margin = sample_margin(n, m)
                    if matrix_count.erdos_gallai_check(margin): # Sample uniformly over margins that have a valid binary matrix
                        num_valid_samples += 1
                        df_dict["n"].append(n)
                        df_dict["m"].append(m)
                        df_dict["margin"].append(str(margin.tolist()))
                        df_dict["true_log_count"].append(np.nan)
                        df_dict["true_log_count_err"].append(np.nan)
                        df_dict["estimate_mult"].append(matrix_count.estimate_log_symmetric_matrices(margin, binary_matrix=True, binary_multinomial_estimate=True))
                        df_dict["estimate_DM"].append(matrix_count.estimate_log_symmetric_matrices(margin, binary_matrix=True))

df = pd.DataFrame(df_dict)
print(df)

# Check if the filename already exists, if so prompt to ask if it should be overwritten
if filename in os.listdir():
    overwrite = input(f"{filename} already exists. Overwrite? (y/n): ")
    if overwrite.lower() != "y":
        print("Exiting without overwriting.")
        sys.exit()
    else:
        print("Overwriting.")
        df.to_csv(filename, index=False)
else:
    df.to_csv(filename, index=False)