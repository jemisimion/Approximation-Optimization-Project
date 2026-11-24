
import time
import math


# GREEDY SOLUTION FOR INITIAL UPPER BOUND
def first_fit_decreasing(items, capacity):

    bins = []
    loads = []

    for item in sorted(items, reverse=True):

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


# EXACT BIN PACKING USING BACKTRACKING
def exact_bin_packing(items, capacity, time_limit=5):

    if capacity <= 0:
        raise ValueError("Capacity must be positive.")

    if any(item <= 0 or item > capacity for item in items):
        raise ValueError("Invalid item size.")

    start = time.perf_counter()
    deadline = start + time_limit

    if not items:

        return {
            "status": "OPTIMAL",
            "optimal_bins": 0,
            "bins": [],
            "lower_bound": 0,
            "upper_bound": 0,
            "nodes": 0,
            "time": 0
        }

    items = sorted(items, reverse=True)

    # LOWER BOUND
    volume_bound = math.ceil(sum(items) / capacity)

    large_item_bound = sum(
        1 for item in items if item > capacity / 2
    )

    lower_bound = max(volume_bound, large_item_bound)

    # UPPER BOUND USING FFD
    best_bins = first_fit_decreasing(items, capacity)
    upper_bound = len(best_bins)

    nodes = 0

    # CHECK WHETHER ITEMS FIT IN K BINS
    def can_pack(k):

        nonlocal nodes

        loads = [0] * k
        packed_bins = [[] for _ in range(k)]

        def search(position):

            nonlocal nodes

            nodes += 1

            if time.perf_counter() >= deadline:
                raise TimeoutError

            if position == len(items):
                return True

            item = items[position]

            # Skip bins having identical remaining loads
            seen_loads = set()

            for i in range(k):

                current_load = loads[i]

                if current_load in seen_loads:
                    continue

                seen_loads.add(current_load)

                if current_load + item <= capacity:

                    loads[i] += item
                    packed_bins[i].append(item)

                    if search(position + 1):
                        return True

                    packed_bins[i].pop()
                    loads[i] -= item

                    # Empty bins are interchangeable
                    if current_load == 0:
                        break

            return False

        if search(0):

            return [
                b[:] for b in packed_bins if b
            ]

        return None

    # SEARCH FROM LOWER BOUND TO UPPER BOUND
    try:

        for k in range(lower_bound, upper_bound):

            solution = can_pack(k)

            if solution is not None:

                elapsed = time.perf_counter() - start

                return {
                    "status": "OPTIMAL",
                    "optimal_bins": len(solution),
                    "bins": solution,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "nodes": nodes,
                    "time": elapsed
                }

        # No smaller solution exists
        elapsed = time.perf_counter() - start

        return {
            "status": "OPTIMAL",
            "optimal_bins": upper_bound,
            "bins": best_bins,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "nodes": nodes,
            "time": elapsed
        }

    except TimeoutError:

        elapsed = time.perf_counter() - start

        return {
            "status": "TIME LIMIT - NOT PROVEN",
            "optimal_bins": None,
            "bins": best_bins,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "nodes": nodes,
            "time": elapsed
        }


# MAIN PROGRAM
def main():

    print("=" * 55)
    print("EXACT BIN PACKING OPTIMIZATION")
    print("=" * 55)

    capacity = 10

    items = [5, 7, 5, 2, 4, 2, 5, 1, 6]

    print("Bin Capacity:", capacity)
    print("Items:", items)

    result = exact_bin_packing(
        items,
        capacity,
        time_limit=5
    )

    print("\nEXACT SOLVER RESULTS")
    print("-" * 55)

    print("Status:", result["status"])
    print("Lower Bound:", result["lower_bound"])
    print("Greedy Upper Bound:", result["upper_bound"])
    print("Search Nodes:", result["nodes"])
    print("Execution Time:", round(result["time"] * 1000, 4), "ms")

    if result["optimal_bins"] is not None:

        print("Optimal Number of Bins:", result["optimal_bins"])

    else:

        print("Optimal Number of Bins: Not proven")

    print("\nBin Arrangement:")

    for i, b in enumerate(result["bins"], 1):

        print(
            f"Bin {i}: {b} | Used: {sum(b)} | "
            f"Remaining: {capacity - sum(b)}"
        )

    print("=" * 55)


if __name__ == "__main__":
    main()
