import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from utils.misc import merge_close_values


matplotlib.use("TkAgg")  # or "Qt5Agg" if installed
# -- Matplotlib parameters -- #
SMALL_SIZE = 12
MEDIUM_SIZE = 20
BIGGER_SIZE = 28

plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)  # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['font.family'] = 'STIXGeneral'


# Load CSV
df = pd.read_csv("collimation_results.csv")

# Get unique values
w0_values = sorted(df["w0 (microns)"].unique())
d_lens = sorted(df["d_lens (mm)"].unique())
rocs = sorted(df["ROC (mm)"].unique())
focals = sorted(df["Focal Length (mm)"].unique())

# Create subplots: one for each RoC
fig, axes = plt.subplots(1, len(rocs), figsize=(14, 5), sharey=False)

if len(rocs) == 1:
    axes = [axes]  # Ensure axes is iterable

for ax, roc in zip(axes, rocs):
    all_waists = []
    all_length = []

    ax2 = ax.twinx()  # Create a second y-axis for d_lens

    for w0, dl in zip(w0_values, d_lens):
        # Set subset for waist values
        subset = df[(df["ROC (mm)"] == roc) & (df["w0 (microns)"] == w0)]
        subset = subset.sort_values("Focal Length (mm)")

        # Plot waist on the primary y-axis
        ax.plot(
            subset["Focal Length (mm)"],
            subset["Waist (mm)"],
            marker="o",
            linestyle="--",
            label=fr"$w_0$={w0} $\mu$m"
        )
        # Plot d_lens on the secondary y-axis
        ax2.plot(
            subset["Focal Length (mm)"],
            subset["d_lens (mm)"],
            marker="x",
            linestyle=":",
            label=fr"$d_\mathrm{{lens}}$={dl} mm",
            color="gray"
        )

        # Collect all waist and d_lens values for unique y-ticks
        all_waists.extend(subset["Waist (mm)"].values)
        all_length.extend(subset["d_lens (mm)"].values)

    # Merge close values for unique y-ticks
    unique_waists = sorted(set(all_waists))
    unique_waists_merged = merge_close_values(unique_waists, tol=0.06)

    unique_length = sorted(set(all_length))
    unique_length_merged = merge_close_values(unique_length, tol=5.)

    # Set y-ticks for waist
    ax.set_yticks(unique_waists_merged)
    ax.set_yticklabels([f"{w:.3f}" for w in unique_waists_merged])

    # Set y-ticks for d_lens
    ax2.set_yticks(unique_length_merged)
    ax2.set_yticklabels([f"{dl:.3f}" for dl in unique_length_merged])

    ax.set_xticks(focals)
    ax.set_title(f"RoC = {roc} mm")
    ax.set_xlabel("Focal Length (mm)")
    ax.grid(True, linestyle="--", alpha=0.6)
    if ax == axes[0]:
        ax.set_ylabel("Waist (mm)")

axes[0].legend(title="Initial Waist")
# plt.suptitle(r"Waist evolution for all $w_0$ values")
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
