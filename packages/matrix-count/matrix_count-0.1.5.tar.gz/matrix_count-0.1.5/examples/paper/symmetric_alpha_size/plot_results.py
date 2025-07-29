# Plot the results

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm, TwoSlopeNorm
import matplotlib.colors as mcolors

# Read the data
df_binary = pd.read_csv("test_margins_binary.csv")
df_multigraph = pd.read_csv("test_margins_multigraph.csv")

# For each row, compute the error and fractional error in the estimates
df_multigraph["estimate_2_err"] = (df_multigraph["estimate_2"] - df_multigraph["true_log_count"])
df_multigraph["estimate_3_err"] = (df_multigraph["estimate_3"] - df_multigraph["true_log_count"])
df_multigraph["estimate_2_err_frac"] = (df_multigraph["estimate_2"] - df_multigraph["true_log_count"]) / df_multigraph["true_log_count"]
df_multigraph["estimate_3_err_frac"] = (df_multigraph["estimate_3"] - df_multigraph["true_log_count"]) / df_multigraph["true_log_count"]

# For each of the n and alpha values, compute the mean and RMSE of the fractional error among the non-NaN values
df_multigraph["estimate_2_err_frac_mean"] = df_multigraph.groupby(["n", "alpha"])["estimate_2_err_frac"].transform(lambda x: np.abs(np.nanmean(x)))
df_multigraph["estimate_3_err_frac_mean"] = df_multigraph.groupby(["n", "alpha"])["estimate_3_err_frac"].transform(lambda x: np.abs(np.nanmean(x)))
df_multigraph["estimate_2_err_mean"] = df_multigraph.groupby(["n", "alpha"])["estimate_2_err"].transform(lambda x: np.abs(np.nanmean(x)))
df_multigraph["estimate_3_err_mean"] = df_multigraph.groupby(["n", "alpha"])["estimate_3_err"].transform(lambda x: np.abs(np.nanmean(x)))

# Plot the fractional error for the multigraph estimates estimate_2 and estimate_3 side by side as an imshow plot with axis alpha and n
ns = df_multigraph["n"].unique()
alphas = df_multigraph["alpha"].unique()

# Keep the alpha_tick_values to two decimal places
alpha_tick_values = np.round(alphas, 2)

plt.clf()
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Estimate 2
pivot_table_2 = df_multigraph.pivot_table(index="n", columns="alpha", values="estimate_2_err_frac_mean", aggfunc="mean")
pivot_table_2 = pivot_table_2.reindex(index=ns, columns=alphas)
im = axes[0].imshow(pivot_table_2, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.0001, vmax=1))
axes[0].set_xticks(np.arange(len(alphas)))
axes[0].set_xticklabels(alpha_tick_values, rotation=45)
axes[0].set_yticks(np.arange(len(ns)))
axes[0].set_yticklabels(ns)
axes[0].set_xlabel(r'$\alpha$')
axes[0].set_ylabel("n")
axes[0].set_title("Average Fractional Error of Multigraph Estimate 2")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('fractional error')

# Estimate 3
pivot_table_3 = df_multigraph.pivot_table(index="n", columns="alpha", values="estimate_3_err_frac_mean", aggfunc="mean")
pivot_table_3 = pivot_table_3.reindex(index=ns, columns=alphas)
im = axes[1].imshow(pivot_table_3, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.0001, vmax=1))
axes[1].set_xticks(np.arange(len(alphas)))
axes[1].set_xticklabels(alpha_tick_values, rotation=45)
axes[1].set_yticks(np.arange(len(ns)))
axes[1].set_yticklabels(ns)
axes[1].set_xlabel(r'$\alpha$')
axes[1].set_ylabel("n")
axes[1].set_title("Average Fractional Error of Multigraph Estimate 3")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('fractional error')

plt.tight_layout()
plt.savefig("multigraph_fractional_error.png")

# Plot the error for the multigraph estimates estimate_2 and estimate_3 side by side as an imshow plot with axis alpha and n
ns = df_multigraph["n"].unique()
alphas = df_multigraph["alpha"].unique()

plt.clf()
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Estimate 2
pivot_table_2 = df_multigraph.pivot_table(index="n", columns="alpha", values="estimate_2_err_mean", aggfunc="mean")
pivot_table_2 = pivot_table_2.reindex(index=ns, columns=alphas)
im = axes[0].imshow(pivot_table_2, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.01, vmax=100))
axes[0].set_xticks(np.arange(len(alphas)))
axes[0].set_xticklabels(alpha_tick_values, rotation=45)
axes[0].set_yticks(np.arange(len(ns)))
axes[0].set_yticklabels(ns)
axes[0].set_xlabel(r'$\alpha$')
axes[0].set_ylabel("n")
axes[0].set_title("Average Error of Multigraph Estimate 2")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('absolute error')

# Estimate 3
pivot_table_3 = df_multigraph.pivot_table(index="n", columns="alpha", values="estimate_3_err_mean", aggfunc="mean")
pivot_table_3 = pivot_table_3.reindex(index=ns, columns=alphas)
im = axes[1].imshow(pivot_table_3, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.01, vmax=100))
axes[1].set_xticks(np.arange(len(alphas)))
axes[1].set_xticklabels(alpha_tick_values, rotation=45)
axes[1].set_yticks(np.arange(len(ns)))
axes[1].set_yticklabels(ns)
axes[1].set_xlabel(r'$\alpha$')
axes[1].set_ylabel("n")
axes[1].set_title("Average Error of Multigraph Estimate 3")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('absolute error')

plt.tight_layout()
plt.savefig("multigraph_error.png")
