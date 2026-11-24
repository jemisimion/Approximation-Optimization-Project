
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# 1. NEXT FIT
def next_fit(items, capacity):
    bins = []

    for item in items:
        if not bins or sum(bins[-1]) + item > capacity:
            bins.append([item])
        else:
            bins[-1].append(item)

    return bins


# 2. FIRST FIT
def first_fit(items, capacity):
    bins = []

    for item in items:
        placed = False

        for b in bins:
            if sum(b) + item <= capacity:
                b.append(item)
                placed = True
                break

        if not placed:
            bins.append([item])

    return bins


# 3. BEST FIT
def best_fit(items, capacity):
    bins = []

    for item in items:
        best_index = -1
        min_space = capacity + 1

        for i, b in enumerate(bins):
            remaining = capacity - sum(b)

            if item <= remaining and remaining < min_space:
                min_space = remaining
                best_index = i

        if best_index == -1:
            bins.append([item])
        else:
            bins[best_index].append(item)

    return bins


# 4. FIRST FIT DECREASING
def first_fit_decreasing(items, capacity):
    sorted_items = sorted(items, reverse=True)
    return first_fit(sorted_items, capacity)


# DISPLAY RESULTS
def display_results(name, bins, items, capacity, elapsed):
    print("\n" + "=" * 45)
    print(name)
    print("=" * 45)

    for i, b in enumerate(bins, 1):
        print(f"Bin {i}: {b}")
        print(f"Used: {sum(b)}")
        print(f"Remaining: {capacity - sum(b)}")

    utilization = sum(items) / (len(bins) * capacity) * 100

    print("Total Bins:", len(bins))
    print("Utilization:", round(utilization, 2), "%")
    print("Execution Time:", round(elapsed * 1000, 4), "ms")


# GRAPHICAL VISUALIZATION
def visualize_results(results, capacity):
    counts = [len(bins) for name, bins, elapsed in results]
    labels = [name for name, bins, elapsed in results]

    fig = plt.figure(
        figsize=(12, 3 + sum(len(bins) * 0.65 for _, bins, _ in results))
    )

    grid = fig.add_gridspec(
        5, 1,
        height_ratios=[2] + [max(1, len(bins)) for _, bins, _ in results],
        hspace=0.9
    )

    # Comparison chart
    ax1 = fig.add_subplot(grid[0])
    bars = ax1.bar(labels, counts)

    for bar, count in zip(bars, counts):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            str(count),
            ha="center"
        )

    ax1.set_title("Algorithm Comparison - Number of Bins")
    ax1.set_ylabel("Bins Used")
    ax1.set_ylim(0, max(counts) + 1)

    # Individual bin packing diagrams
    for index, (name, bins, elapsed) in enumerate(results):
        ax = fig.add_subplot(grid[index + 1])

        for bin_index, bin_items in enumerate(bins):
            y = len(bins) - bin_index - 1
            x = 0

            ax.add_patch(
                Rectangle(
                    (0, y), capacity, 0.7,
                    fill=False, edgecolor="black", linewidth=1.5
                )
            )

            for item in bin_items:
                color = plt.cm.Set3((item % 12) / 12)

                ax.add_patch(
                    Rectangle(
                        (x, y), item, 0.7,
                        facecolor=color, edgecolor="black"
                    )
                )

                ax.text(
                    x + item / 2, y + 0.35,
                    str(item),
                    ha="center", va="center"
                )

                x += item

        ax.set_xlim(0, capacity)
        ax.set_ylim(-0.2, len(bins) + 0.2)
        ax.set_yticks(range(len(bins)))
        ax.set_yticklabels(
            [f"Bin {i}" for i in range(len(bins), 0, -1)]
        )
        ax.set_title(f"{name} - {len(bins)} Bins")
        ax.set_xlabel("Bin Capacity")
        ax.grid(axis="x", alpha=0.3)

    fig.suptitle(
        "BIN PACKING APPROXIMATION ALGORITHMS",
        fontsize=15
    )

    plt.tight_layout()
    plt.show()


# MAIN PROGRAM
def main():
    print("=" * 50)
    print("BIN PACKING APPROXIMATION ALGORITHMS")
    print("=" * 50)

    try:
        capacity = int(input("\nEnter bin capacity: "))

        user_input = input(
            "Enter item sizes separated by commas: "
        )

        items = [int(x.strip()) for x in user_input.split(",")]

    except ValueError:
        print("Error: Enter valid positive integers.")
        return

    if capacity <= 0:
        print("Capacity must be greater than zero.")
        return

    if not items or any(item <= 0 for item in items):
        print("Items must be positive integers.")
        return

    if any(item > capacity for item in items):
        print("An item cannot exceed bin capacity.")
        return

    print("\nInput Capacity:", capacity)
    print("Input Items:", items)

    algorithms = {
        "NEXT FIT": next_fit,
        "FIRST FIT": first_fit,
        "BEST FIT": best_fit,
        "FIRST FIT DECREASING": first_fit_decreasing
    }

    results = []

    for name, algorithm in algorithms.items():
        start = time.perf_counter()
        bins = algorithm(items, capacity)
        elapsed = time.perf_counter() - start

        display_results(
            name, bins, items, capacity, elapsed
        )

        results.append((name, bins, elapsed))

    # FINAL COMPARISON
    print("\n" + "=" * 55)
    print("FINAL ALGORITHM COMPARISON")
    print("=" * 55)

    print(f"{'Algorithm':<25}{'Bins':<10}{'Time (ms)':<12}")

    for name, bins, elapsed in results:
        print(
            f"{name:<25}{len(bins):<10}"
            f"{elapsed * 1000:<12.4f}"
        )

    best = min(results, key=lambda x: len(x[1]))

    print("-" * 55)
    print("Best result:", best[0])
    print("Minimum bins:", len(best[1]))
    print("=" * 55)

    # SHOW GRAPHS
    visualize_results(results, capacity)


if __name__ == "__main__":
    main()
