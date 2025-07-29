# Plot the results

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the data
df_binary = pd.read_csv("test_margins_binary.csv")
df_multigraph = pd.read_csv("test_margins_multigraph.csv")


# For each row, compute the fractional error in the estimates
df_binary["estimate_mult_err_frac"] = (df_binary["estimate_mult"] - df_binary["true_log_count"]) / df_binary["true_log_count"]
df_binary["estimate_DM_err_frac"] = (df_binary["estimate_DM"] - df_binary["true_log_count"]) / df_binary["true_log_count"]
df_multigraph["estimate_2_err_frac"] = (df_multigraph["estimate_2"] - df_multigraph["true_log_count"]) / df_multigraph["true_log_count"]
df_multigraph["estimate_3_err_frac"] = (df_multigraph["estimate_3"] - df_multigraph["true_log_count"]) / df_multigraph["true_log_count"]

# For each of the alpha values, compute the average and upper and lower quartiles of the fractional error among the non-NaN values
df_binary["estimate_mult_err_frac_median"] = df_binary.groupby("alpha")["estimate_mult_err_frac"].transform(lambda x: np.nanpercentile(x, 50) if not x.isna().all() else np.nan)
df_binary["estimate_mult_err_frac_upper"] = df_binary.groupby("alpha")["estimate_mult_err_frac"].transform(lambda x: np.nanpercentile(x, 75) if not x.isna().all() else np.nan)
df_binary["estimate_mult_err_frac_lower"] = df_binary.groupby("alpha")["estimate_mult_err_frac"].transform(lambda x: np.nanpercentile(x, 25) if not x.isna().all() else np.nan)
df_binary["estimate_DM_err_frac_median"] = df_binary.groupby("alpha")["estimate_DM_err_frac"].transform(lambda x: np.nanpercentile(x, 50) if not x.isna().all() else np.nan)
df_binary["estimate_DM_err_frac_upper"] = df_binary.groupby("alpha")["estimate_DM_err_frac"].transform(lambda x: np.nanpercentile(x, 75) if not x.isna().all() else np.nan)
df_binary["estimate_DM_err_frac_lower"] = df_binary.groupby("alpha")["estimate_DM_err_frac"].transform(lambda x: np.nanpercentile(x, 25) if not x.isna().all() else np.nan)
df_multigraph["estimate_2_err_frac_median"] = df_multigraph.groupby("alpha")["estimate_2_err_frac"].transform(lambda x: np.nanpercentile(x, 50) if not x.isna().all() else np.nan)
df_multigraph["estimate_2_err_frac_upper"] = df_multigraph.groupby("alpha")["estimate_2_err_frac"].transform(lambda x: np.nanpercentile(x, 75) if not x.isna().all() else np.nan)
df_multigraph["estimate_2_err_frac_lower"] = df_multigraph.groupby("alpha")["estimate_2_err_frac"].transform(lambda x: np.nanpercentile(x, 25) if not x.isna().all() else np.nan)
df_multigraph["estimate_3_err_frac_median"] = df_multigraph.groupby("alpha")["estimate_3_err_frac"].transform(lambda x: np.nanpercentile(x, 50) if not x.isna().all() else np.nan)
df_multigraph["estimate_3_err_frac_upper"] = df_multigraph.groupby("alpha")["estimate_3_err_frac"].transform(lambda x: np.nanpercentile(x, 75) if not x.isna().all() else np.nan)
df_multigraph["estimate_3_err_frac_lower"] = df_multigraph.groupby("alpha")["estimate_3_err_frac"].transform(lambda x: np.nanpercentile(x, 25) if not x.isna().all() else np.nan)


# Get a list of the alpha values and these averages and quartiles
alphas = df_binary["alpha"].unique()
estimate_mult_err_frac_median = df_binary["estimate_mult_err_frac_median"].unique()
estimate_mult_err_frac_upper = df_binary["estimate_mult_err_frac_upper"].unique()
estimate_mult_err_frac_lower = df_binary["estimate_mult_err_frac_lower"].unique()
estimate_DM_err_frac_median = df_binary["estimate_DM_err_frac_median"].unique()
estimate_DM_err_frac_upper = df_binary["estimate_DM_err_frac_upper"].unique()
estimate_DM_err_frac_lower = df_binary["estimate_DM_err_frac_lower"].unique()
estimate_2_err_frac_median = df_multigraph["estimate_2_err_frac_median"].unique()
estimate_2_err_frac_upper = df_multigraph["estimate_2_err_frac_upper"].unique()
estimate_2_err_frac_lower = df_multigraph["estimate_2_err_frac_lower"].unique()
estimate_3_err_frac_median = df_multigraph["estimate_3_err_frac_median"].unique()
estimate_3_err_frac_upper = df_multigraph["estimate_3_err_frac_upper"].unique()
estimate_3_err_frac_lower = df_multigraph["estimate_3_err_frac_lower"].unique()

# Plot the fractional error for the binary matrix estimates
plt.clf()
plt.figure()
plt.plot(alphas, estimate_mult_err_frac_median, label="Binary Multinomial Estimate")
plt.fill_between(alphas, estimate_mult_err_frac_lower, estimate_mult_err_frac_upper, alpha=0.3)
plt.plot(alphas, estimate_DM_err_frac_median, label="Binary DM Estimate")
plt.fill_between(alphas, estimate_DM_err_frac_lower, estimate_DM_err_frac_upper, alpha=0.3)
plt.axvline(x=1, color='r', linestyle='--')
plt.xscale("log")
plt.xlabel(r'$\alpha$')
plt.yscale("symlog", linthresh=1e-4)
plt.ylabel("Fractional Error")
plt.title("Fractional Error of Binary Matrix Estimates")
plt.legend()
plt.savefig("binary_matrix_fractional_error.png")

# Plot the fractional error for the multigraph estimates
alphas = df_multigraph["alpha"].unique() # Do this again since the set of valid alphas may be different

plt.clf()
plt.figure()
plt.plot(alphas, estimate_2_err_frac_median, label="Multigraph Estimate 2nd Order")
plt.fill_between(alphas, estimate_2_err_frac_lower, estimate_2_err_frac_upper, alpha=0.3)
plt.plot(alphas, estimate_3_err_frac_median, label="Multigraph Estimate 3rd Order")
plt.fill_between(alphas, estimate_3_err_frac_lower, estimate_3_err_frac_upper, alpha=0.3)
plt.axvline(x=1, color='r', linestyle='--')
plt.xscale("log")
plt.xlabel(r'$\alpha$')
plt.yscale("symlog", linthresh=1e-4)
plt.ylabel("Fractional Error")
plt.title("Fractional Error of Multigraph Estimates")
plt.legend()
plt.savefig("multigraph_fractional_error.png")
