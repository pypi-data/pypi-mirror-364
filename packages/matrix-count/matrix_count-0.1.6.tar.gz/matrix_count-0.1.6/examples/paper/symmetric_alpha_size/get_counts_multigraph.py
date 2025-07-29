# Script to use matrix_count in order to evaluate the performance of the symmetric multigraph estimates as the size n and number of edges m vary.

import matrix_count
from joblib import Parallel, delayed
from multiprocessing import Process, Manager

import pandas as pd
import numpy as np
import ast

filename = "test_margins_multigraph.csv"

# Read csv
df = pd.read_csv(filename)

def save_to_file(q):
    while True:
        try:
            i, true_log_count, true_log_count_err = q.get()
            if i is None: break
            df.at[i, "true_log_count"] = true_log_count
            df.at[i, "true_log_count_err"] = true_log_count_err
            df.to_csv(filename, index=False)
        except:
            continue

# Function to calculate true log count for a row
def calculate_true_log_count(i, row):
    if np.isnan(row["true_log_count"]):
        # 10 minute timeout
        print(row["n"],row["m"],row["margin"])
        true_log_count, true_log_count_err = matrix_count.count_log_symmetric_matrices(np.array(ast.literal_eval(row["margin"])), binary_matrix=False, timeout=60*10, max_samples=10000)
        q.put((i, true_log_count, true_log_count_err))

m = Manager()
q = m.Queue() # queue to store results to be written to file as they come in
p = Process(target=save_to_file, args=(q,))
p.start()
Parallel(n_jobs=-1)(delayed(calculate_true_log_count)(i, row) for i, row in df.iterrows())
q.put(None)
p.join()
