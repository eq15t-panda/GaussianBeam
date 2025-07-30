import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("TkAgg")  # Use a compatible backend

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

# Read data from the CSV file
csv_file = "collimation_results.csv"
data = {}

with open(csv_file, mode="r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        roc = float(row["ROC (mm)"])
        focal_length = float(row["Focal Length (mm)"])
        d_lens = row["d_lens (mm)"]
        waist = row["Waist (microns)"]

        # Skip rows with errors
        if d_lens == "Error" or waist == "Error":
            continue

        d_lens = float(d_lens)
        waist = float(waist)

        if roc not in data:
            data[roc] = {"focal_lengths": [], "d_lens": [], "waists": []}

        data[roc]["focal_lengths"].append(focal_length)
        data[roc]["d_lens"].append(d_lens)
        data[roc]["waists"].append(waist)

# Plot the results
for roc, values in data.items():
    focal_lengths = np.array(values["focal_lengths"])
    d_lens = np.array(values["d_lens"])
    waists = np.array(values["waists"])

    # Plot d_lens vs. Focal Length
    plt.figure()
    plt.plot(focal_lengths, d_lens, marker="o", label=f"ROC = {roc:.1f} mm")
    plt.xlabel("Focal Length (mm)")
    plt.ylabel(r"$d_{lens}$ (mm)")
    plt.title("$d_{{lens}}$ vs. Focal Length for\n"+r"ROC = {:.1f} mm and $w_0$ = {:.1f} $\mu$m".format(roc, waists[0]))
    # plt.legend()
    plt.grid()
    plt.savefig(f"d_lens_vs_focal_length_ROC_{int(roc)}.png")

plt.show()
