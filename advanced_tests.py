
import random
import time
import csv
import statistics
from pathlib import Path
import matplotlib.pyplot as plt


# EXPERIMENT SETTINGS
CAPACITY = 100
DATASET_SIZES = [100, 500, 1000, 2000, 5000]
REPEATS = 3


# 1. NEXT FIT
def next_fit(items, capacity):
    bins = []
    loads = []

    for item in items:
        if not bins or loads[-1] + item > capacity:
            bins.append([item])
            loads.append(item)
        else:
            bins[-1].append(item)
            loads[-1] += item

    return bins


# 2. FIRST FIT
def first_fit(items, capacity):
    bins = []
    loads = []

    for item in items:
        placed = False

        for i in range(len(bins)):
            if loads[i] + item <= capacity:
                bins[i].append(item)
                loads[i] += item
                placed = True
                break

        if not placed:
            bins.append([item])
            loads.append(item)

    return bins


# 3. BEST FIT
def best_fit(items, capacity):
    bins = []
    loads = []

    for item in items:
        best_index = -1
        min_space = capacity + 1

        for i, load in enumerate(loads):
            remaining = capacity - load

            if item <= remaining and remaining < min_space:
                min_space = remaining
                best_index = i

        if best_index == -1:
            bins.append([item])
            loads.append(item)
        else:
            bins[best_index].append(item)
            loads[best_index] += item

    return bins


# 4. FIRST FIT DECREASING
def first_fit_decreasing(items, capacity):
    return first_fit(sorted(items, reverse=True), capacity)


# 5. SEGMENT TREE
class SegmentTree:

    def __init__(self, size):
        self.n = size
        self.tree = [0] * (4 * size + 4)

    def update(self, index, value):
        self._update(1, 0, self.n - 1, index, value)

    def _update(self, node, left, right, index, value):

        if left == right:
            self.tree[node] = value
            return

        mid = (left + right) // 2

        if index <= mid:
            self._update(
                node * 2, left, mid, index, value
            )
        else:
            self._update(
                node * 2 + 1, mid + 1, right,
                index, value
            )

        self.tree[node] = max(
            self.tree[node * 2],
            self.tree[node * 2 + 1]
        )

    def find_first(self, required):

        if self.tree[1] < required:
            return -1

        return self._find(
            1, 0, self.n - 1, required
        )

    def _find(self, node, left, right, required):

        if left == right:
            return left

        mid = (left + right) // 2

        if self.tree[node * 2] >= required:
            return self._find(
                node * 2, left, mid, required
            )

        return self._find(
            node * 2 + 1, mid + 1, right, required
        )


# 6. SEGMENT TREE FIRST FIT
def segment_tree_first_fit(items, capacity):

    if not items:
        return []

    tree = SegmentTree(len(items))
    bins = []
    remaining = [0] * len(items)

    for item in items:

        index = tree.find_first(item)

        if index == -1:
            index = len(bins)
            bins.append([item])
            remaining[index] = capacity - item
        else:
            bins[index].append(item)
            remaining[index] -= item

        tree.update(index, remaining[index])

    return bins


# 7. SEGMENT TREE FFD
def segment_tree_ffd(items, capacity):

    sorted_items = sorted(items, reverse=True)

    return segment_tree_first_fit(sorted_items, capacity)


# GENERATE INPUT PATTERNS
def generate_patterns(size):

    rng = random.Random(2026 + size)

    items = [
        rng.randint(5, CAPACITY)
        for _ in range(size)
    ]

    return {
        "Ascending": sorted(items),
        "Descending": sorted(items, reverse=True),
        "Random": items
    }


# VALIDATE RESULTS
def validate_result(items, bins, capacity):

    packed = [
        item for b in bins for item in b
    ]

    assert sorted(items) == sorted(packed), (
        "Missing or duplicated items"
    )

    assert all(
        0 < sum(b) <= capacity for b in bins
    ), "Invalid bin capacity"


# RUN EXPERIMENTS
def run_experiments():

    algorithms = {
        "Next Fit": next_fit,
        "First Fit": first_fit,
        "Best Fit": best_fit,
        "First Fit Decreasing": first_fit_decreasing,
        "Segment Tree First Fit": segment_tree_first_fit,
        "Segment Tree FFD": segment_tree_ffd
    }

    results = []

    print("=" * 95)
    print("ADVANCED SIX-ALGORITHM EXPERIMENT")
    print("=" * 95)

    for size in DATASET_SIZES:

        patterns = generate_patterns(size)

        for pattern_name, items in patterns.items():

            lower_bound = (
                sum(items) + CAPACITY - 1
            ) // CAPACITY

            print(
                f"\nDataset: {size} | Pattern: {pattern_name}"
            )

            for name, algorithm in algorithms.items():

                times = []
                bins = None

                for _ in range(REPEATS):

                    start = time.perf_counter()

                    current_bins = algorithm(
                        items, CAPACITY
                    )

                    elapsed = time.perf_counter() - start

                    times.append(elapsed)
                    bins = current_bins

                validate_result(items, bins, CAPACITY)

                bin_count = len(bins)

                utilization = (
                    sum(items) /
                    (bin_count * CAPACITY)
                ) * 100

                median_time = (
                    statistics.median(times) * 1000
                )

                result = {
                    "Items": size,
                    "Pattern": pattern_name,
                    "Algorithm": name,
                    "Total Item Size": sum(items),
                    "Bins": bin_count,
                    "Lower Bound": lower_bound,
                    "Gap": bin_count - lower_bound,
                    "Utilization (%)": round(utilization, 2),
                    "Execution Time (ms)": round(
                        median_time, 6
                    )
                }

                results.append(result)

                print(
                    f"{name:<27} "
                    f"Bins: {bin_count:<6} "
                    f"Utilization: {utilization:.2f}% "
                    f"Time: {median_time:.6f} ms"
                )

    return results


# SAVE CSV RESULTS
def save_results(results, folder):

    filename = folder / "advanced_results.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nCSV saved:", filename)


# GENERATE GRAPHS
def generate_graphs(results, folder):

    patterns = [
        "Ascending",
        "Descending",
        "Random"
    ]

    algorithms = [
        "Next Fit",
        "First Fit",
        "Best Fit",
        "First Fit Decreasing",
        "Segment Tree First Fit",
        "Segment Tree FFD"
    ]

    # BIN COUNT COMPARISON
    fig, axes = plt.subplots(1, 3, figsize=(19, 5))

    for ax, pattern in zip(axes, patterns):

        for algorithm in algorithms:

            selected = [
                r for r in results
                if r["Pattern"] == pattern
                and r["Algorithm"] == algorithm
            ]

            selected.sort(key=lambda x: x["Items"])

            ax.plot(
                [r["Items"] for r in selected],
                [r["Bins"] for r in selected],
                marker="o",
                label=algorithm
            )

        ax.set_title(pattern + " Input")
        ax.set_xlabel("Number of Items")
        ax.set_ylabel("Number of Bins")
        ax.grid(True)
        ax.legend(fontsize=7)

    fig.suptitle("Six Algorithms - Bin Count Comparison")
    fig.tight_layout()

    fig.savefig(
        folder / "advanced_bin_comparison.png",
        dpi=200
    )

    plt.close(fig)

    # EXECUTION TIME COMPARISON
    fig, axes = plt.subplots(1, 3, figsize=(19, 5))

    for ax, pattern in zip(axes, patterns):

        for algorithm in algorithms:

            selected = [
                r for r in results
                if r["Pattern"] == pattern
                and r["Algorithm"] == algorithm
            ]

            selected.sort(key=lambda x: x["Items"])

            ax.plot(
                [r["Items"] for r in selected],
                [r["Execution Time (ms)"] for r in selected],
                marker="o",
                label=algorithm
            )

        ax.set_title(pattern + " Input")
        ax.set_xlabel("Number of Items")
        ax.set_ylabel("Median Execution Time (ms)")
        ax.set_yscale("log")
        ax.grid(True)
        ax.legend(fontsize=7)

    fig.suptitle("Six Algorithms - Execution Time Comparison")
    fig.tight_layout()

    fig.savefig(
        folder / "advanced_time_comparison.png",
        dpi=200
    )

    plt.close(fig)

    print("\nBoth comparison graphs saved successfully!")


# MAIN PROGRAM
def main():

    folder = (
        Path(__file__).resolve().parent / "results"
    )

    folder.mkdir(exist_ok=True)

    results = run_experiments()

    save_results(results, folder)

    generate_graphs(results, folder)

    print("\n" + "=" * 70)
    print("ALL ADVANCED EXPERIMENTS COMPLETED!")
    print("Total experiment combinations:", len(results))
    print("=" * 70)


if __name__ == "__main__":
    main()
