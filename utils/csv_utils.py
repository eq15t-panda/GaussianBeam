import csv
import os


CSV_FILE = "collimation_results.csv"
HEADER = ["w0 (microns)", "ROC (mm)", "Focal Length (mm)", "d_lens (mm)", "Waist (mm)", "Wavefront (m)"]


def read_existing_results():
    """
    Reads CSV into a set of existing (ROC, Focal, d_lens) to avoid duplicates.
    """
    existing = set()
    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    key = (float(row["w0 (microns)"]),
                           float(row["ROC (mm)"]),
                           float(row["Focal Length (mm)"]),
                           float(row["d_lens (mm)"]))
                    existing.add(key)
                except ValueError:
                    pass  # Skip malformed rows
    return existing


def ensure_header():
    """
    Ensure the CSV has a header if missing.
    """
    if not os.path.isfile(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        with open(CSV_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)


def append_result(w0, roc, f_len, d_lens, waist, wavefront):
    """
    Append result only if it doesn't exist.
    """
    ensure_header()
    existing = read_existing_results()
    key = (w0, roc, f_len, d_lens)
    if key not in existing:
        with open(CSV_FILE, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([w0, roc, f_len, d_lens, waist, wavefront])
