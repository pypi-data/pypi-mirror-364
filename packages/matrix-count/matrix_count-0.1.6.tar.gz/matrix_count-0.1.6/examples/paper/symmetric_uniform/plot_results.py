# Plot the results

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm, TwoSlopeNorm
import matplotlib.colors as mcolors

# Read the data
df_binary = pd.read_csv("test_margins_binary.csv")
df_multigraph = pd.read_csv("test_margins_multigraph.csv")


# For each row, compute the fractional error in the estimates
df_binary["estimate_mult_err_frac"] = (df_binary["estimate_mult"] - df_binary["true_log_count"]) / df_binary["true_log_count"]
df_binary["estimate_DM_err_frac"] = (df_binary["estimate_DM"] - df_binary["true_log_count"]) / df_binary["true_log_count"]
df_multigraph["estimate_2_err_frac"] = (df_multigraph["estimate_2"] - df_multigraph["true_log_count"]) / df_multigraph["true_log_count"]
df_multigraph["estimate_3_err_frac"] = (df_multigraph["estimate_3"] - df_multigraph["true_log_count"]) / df_multigraph["true_log_count"]

# For each of the n and m values, compute the mean and RMSE of the fractional error among the non-NaN values
df_binary["estimate_mult_err_frac_mean"] = df_binary.groupby(["n", "m"])["estimate_mult_err_frac"].transform(lambda x: np.nanmean(x))
df_binary["estimate_mult_err_frac_rmse"] = df_binary.groupby(["n", "m"])["estimate_mult_err_frac"].transform(lambda x: np.sqrt(np.nanmean(x**2)))
df_binary["estimate_DM_err_frac_mean"] = df_binary.groupby(["n", "m"])["estimate_DM_err_frac"].transform(lambda x: np.nanmean(x))
df_binary["estimate_DM_err_frac_rmse"] = df_binary.groupby(["n", "m"])["estimate_DM_err_frac"].transform(lambda x: np.sqrt(np.nanmean(x**2)))
df_multigraph["estimate_2_err_frac_mean"] = df_multigraph.groupby(["n", "m"])["estimate_2_err_frac"].transform(lambda x: np.nanmean(x))
df_multigraph["estimate_2_err_frac_rmse"] = df_multigraph.groupby(["n", "m"])["estimate_2_err_frac"].transform(lambda x: np.sqrt(np.nanmean(x**2)))
df_multigraph["estimate_3_err_frac_mean"] = df_multigraph.groupby(["n", "m"])["estimate_3_err_frac"].transform(lambda x: np.nanmean(x))
df_multigraph["estimate_3_err_frac_rmse"] = df_multigraph.groupby(["n", "m"])["estimate_3_err_frac"].transform(lambda x: np.sqrt(np.nanmean(x**2)))

# Get a list of the n and m values and these means and RMSEs
estimate_mult_err_frac_mean = df_binary["estimate_mult_err_frac_mean"].unique()
estimate_mult_err_frac_rmse = df_binary["estimate_mult_err_frac_rmse"].unique()
estimate_DM_err_frac_mean = df_binary["estimate_DM_err_frac_mean"].unique()
estimate_DM_err_frac_rmse = df_binary["estimate_DM_err_frac_rmse"].unique()
estimate_2_err_frac_mean = df_multigraph["estimate_2_err_frac_mean"].unique()
estimate_2_err_frac_rmse = df_multigraph["estimate_2_err_frac_rmse"].unique()
estimate_3_err_frac_mean = df_multigraph["estimate_3_err_frac_mean"].unique()
estimate_3_err_frac_rmse = df_multigraph["estimate_3_err_frac_rmse"].unique()

# Plot the RMSE fractional error for the binary estimates estimate_mult and estimate_DM side by side as an imshow plot with axis m and n
ns = df_binary["n"].unique()
ms = df_binary["m"].unique()

fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Estimate Mult
pivot_table_mult = df_binary.pivot_table(index="n", columns="m", values="estimate_mult_err_frac_rmse", aggfunc="mean")
pivot_table_mult = pivot_table_mult.reindex(index=ns, columns=ms)

im = axes[0].imshow(pivot_table_mult, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.00001, vmax=1))
axes[0].set_xticks(np.arange(len(ms)))
axes[0].set_xticklabels(ms, rotation=45)
axes[0].set_yticks(np.arange(len(ns)))
axes[0].set_yticklabels(ns)
axes[0].set_xlabel("m")
axes[0].set_ylabel("n")
axes[0].set_title("RMSE of Fractional Error of Binary Estimate Mult")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('RMSE')

# Estimate DM
pivot_table_DM = df_binary.pivot_table(index="n", columns="m", values="estimate_DM_err_frac_rmse", aggfunc="mean")
pivot_table_DM = pivot_table_DM.reindex(index=ns, columns=ms)

im = axes[1].imshow(pivot_table_DM, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.00001, vmax=1))

axes[1].set_xticks(np.arange(len(ms)))
axes[1].set_xticklabels(ms, rotation=45)
axes[1].set_yticks(np.arange(len(ns)))
axes[1].set_yticklabels(ns)
axes[1].set_xlabel("m")
axes[1].set_ylabel("n")
axes[1].set_title("RMSE of Fractional Error of Binary Estimate DM")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('RMSE')

plt.tight_layout()
plt.savefig("binary_fractional_error_rmse.png")


# Plot the RMSE fractional error for the multigraph estimates estimate_2 and estimate_3 side by side as an imshow plot with axis m and n
ns = df_multigraph["n"].unique()
ms = df_multigraph["m"].unique()

fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Estimate 2
pivot_table_2 = df_multigraph.pivot_table(index="n", columns="m", values="estimate_2_err_frac_rmse", aggfunc="mean")
pivot_table_2 = pivot_table_2.reindex(index=ns, columns=ms)
im = axes[0].imshow(pivot_table_2, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.0001, vmax=0.1))
axes[0].set_xticks(np.arange(len(ms)))
axes[0].set_xticklabels(ms, rotation=45)
axes[0].set_yticks(np.arange(len(ns)))
axes[0].set_yticklabels(ns)
axes[0].set_xlabel("m")
axes[0].set_ylabel("n")
axes[0].set_title("RMSE of Fractional Error of Multigraph Estimate 2")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('RMSE')

# Estimate 3
pivot_table_3 = df_multigraph.pivot_table(index="n", columns="m", values="estimate_3_err_frac_rmse", aggfunc="mean")
pivot_table_3 = pivot_table_3.reindex(index=ns, columns=ms)
im = axes[1].imshow(pivot_table_3, origin="lower", aspect='equal', norm=SymLogNorm(linthresh=1e-4, vmin=0.0001, vmax=0.1))
axes[1].set_xticks(np.arange(len(ms)))
axes[1].set_xticklabels(ms, rotation=45)
axes[1].set_yticks(np.arange(len(ns)))
axes[1].set_yticklabels(ns)
axes[1].set_xlabel("m")
axes[1].set_ylabel("n")
axes[1].set_title("RMSE of Fractional Error of Multigraph Estimate 3")

# Add colorbar
cbar = fig.colorbar(im, orientation='vertical')
cbar.ax.set_ylabel('RMSE')

plt.tight_layout()
plt.savefig("multigraph_fractional_error_rmse.png")
