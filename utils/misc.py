import numpy as np


def merge_close_values(values, tol=0.01):
    """
    Merge values within tolerance by grouping them and keeping one representative per group.
    """
    sorted_vals = sorted(values)
    merged = []
    current_group = [sorted_vals[0]]

    for val in sorted_vals[1:]:
        if val - current_group[-1] <= tol:
            current_group.append(val)
        else:
            merged.append(np.mean(current_group))  # or current_group[0]
            current_group = [val]

    merged.append(np.mean(current_group))  # Add last group
    return merged
