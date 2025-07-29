# Script to generate the test margins used to assess the performance of the symmetric multigraph estimates 
# as the size n and number of edges m vary. 

import matrix_count
import pandas as pd
import numpy as np
import sys
import os

filename = "test_margins_multigraph.csv"

# Seed the rng for repeatability
np.random.seed(0)

# Sample from a Dirichlet-Multinomial distribution
def sample_dirichlet_multinomial(total, size, alpha):
    p = np.random.dirichlet([alpha] * size)
    return np.random.multinomial(total, p)

# Sample margin (only return non-negative margins)
def sample_margin(n, m, alpha):
    margin = sample_dirichlet_multinomial(2*m - n, n, alpha)
    return margin + 1

# Values of m and n to test
n_values = [2,3,4,5,7,10,15,20] # Matrix sizes to consider
m = 200 # Number of edges

# Number of samples to generate for each value of m and n
num_samples = 10

df_dict = {"n": [], "m": [], "alpha": [], "margin": [], "true_log_count": [], "true_log_count_err": [], "estimate_2": [], "estimate_3": []}

# Generate the margins for values of alpha from 0.01 to 100 on a log scale
for alpha in np.logspace(-1, 1, 8):
    for n in n_values:
        print(f"Generating margins for alpha: {alpha}, n: {n}")
        for sample_num in range(num_samples):
            margin = sample_margin(n, m, alpha)
            df_dict["n"].append(n)
            df_dict["m"].append(m)
            df_dict["alpha"].append(alpha)
            df_dict["margin"].append(str(margin.tolist()))
            df_dict["true_log_count"].append(np.nan)
            df_dict["true_log_count_err"].append(np.nan)
            df_dict["estimate_2"].append(matrix_count.estimate_log_symmetric_matrices(margin, binary_matrix=False, force_second_order=True))
            df_dict["estimate_3"].append(matrix_count.estimate_log_symmetric_matrices(margin, binary_matrix=False))

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