import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from utils.misc import merge_close_values

# --- Matplotlib setup ---
matplotlib.use("TkAgg")
SMALL_SIZE = 12
MEDIUM_SIZE = 20
BIGGER_SIZE = 28

plt.rc('font', size=SMALL_SIZE)
plt.rc('axes', titlesize=MEDIUM_SIZE)
plt.rc('axes', labelsize=MEDIUM_SIZE)
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=BIGGER_SIZE)
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

# --- Load data ---
df = pd.read_csv("collimation_results.csv")

w0_values = sorted(df["w0 (microns)"].unique())
rocs = sorted(df["ROC (mm)"].unique())
focals = sorted(df["Focal Length (mm)"].unique())

# --- Create subplots: 2 rows (waist + d_lens), N columns (RoCs) ---
fig, axes = plt.subplots(2, len(rocs), figsize=(14, 10), sharex=True)

# Make sure axes is always 2D array
if len(rocs) == 1:
    axes = axes.reshape(2, 1)

# Loop over RoCs
for col, roc in enumerate(rocs):
    all_waists = []
    all_lengths = []

    # --- First row: Waist ---
    ax_w = axes[0, col]
    for w0 in w0_values:
        subset = df[(df["ROC (mm)"] == roc) & (df["w0 (microns)"] == w0)]
        subset = subset.sort_values("Focal Length (mm)")

        ax_w.plot(
            subset["Focal Length (mm)"],
            subset["Waist (mm)"],
            marker="o",
            linestyle="--",
            label=fr"$w_0$={w0} $\mu$m"
        )
        all_waists.extend(subset["Waist (mm)"].values)

    # Highlight zone where waist > 1.5 mm
    ax_w.axhspan(1.5, max(all_waists) + 0.2, color="green", alpha=0.15, label="Collimated zone")

    # Merge close waists for ticks
    merged_waists = merge_close_values(sorted(set(all_waists)), tol=0.1)
    ax_w.set_yticks(merged_waists)
    ax_w.set_yticklabels([f"{w:.3f}" for w in merged_waists])
    ax_w.set_title(f"RoC = {roc} mm")
    ax_w.grid(True, linestyle="--", alpha=0.6)
    if col == 0:
        ax_w.set_ylabel("Waist (mm)")

    # --- Second row: d_lens ---
    ax_dl = axes[1, col]
    for w0 in w0_values:
        subset = df[(df["ROC (mm)"] == roc) & (df["w0 (microns)"] == w0)]
        subset = subset.sort_values("Focal Length (mm)")

        ax_dl.plot(
            subset["Focal Length (mm)"],
            subset["d_lens (mm)"],
            marker="x",
            linestyle=":",
            label=fr"$w_0$={w0} $\mu$m"
        )
        all_lengths.extend(subset["d_lens (mm)"].values)

    # Merge close d_lens for ticks
    merged_lengths = merge_close_values(sorted(set(all_lengths)), tol=5.0)
    ax_dl.set_yticks(merged_lengths)
    ax_dl.set_yticklabels([f"{dl:.1f}" for dl in merged_lengths])
    ax_dl.grid(True, linestyle="--", alpha=0.6)
    ax_dl.set_xlabel("Focal Length (mm)")
    # ax_dl.set_yscale("log")  # <<<<<< LOG SCALE for d_lens
    if col == 0:
        ax_dl.set_ylabel("$d_{lens}$ (mm)")

# Legend on top-left subplot
axes[0, 0].legend(title="Initial Waist")

plt.tight_layout()
plt.show()
