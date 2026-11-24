
from exact_solver import exact_bin_packing

from benchmark import (
    next_fit,
    first_fit,
    best_fit,
    first_fit_decreasing,
    segment_tree_first_fit,
    segment_tree_ffd
)


# SIX APPROXIMATION ALGORITHMS
algorithms = {
    "Next Fit": next_fit,
    "First Fit": first_fit,
    "Best Fit": best_fit,
    "First Fit Decreasing": first_fit_decreasing,
    "Segment Tree First Fit": segment_tree_first_fit,
    "Segment Tree FFD": segment_tree_ffd
}


# TEST DATASETS
test_cases = [
    ("Normal Dataset", 10, [5, 7, 5, 2, 4, 2, 5, 1, 6], 4),

    ("FFD Gap Test", 10, [3, 3, 4, 3, 4, 3], 2),

    ("Exact Pair Test", 10, [6, 4, 6, 4], 2),

    ("Large Item Test", 10, [6, 6, 6], 3),

    ("Full Capacity Test", 10, [10], 1),

    ("Empty Dataset", 10, [], 0)
]


def validate(items, bins, capacity):

    packed = [
        item for b in bins for item in b
    ]

    assert sorted(items) == sorted(packed), (
        "Items missing or duplicated"
    )

    assert all(
        0 <= sum(b) <= capacity for b in bins
    ), "Bin capacity exceeded"


# MAIN VALIDATION
def main():

    print("=" * 85)
    print("EXACT OPTIMIZATION - VALIDATION AND COMPARISON")
    print("=" * 85)

    all_passed = True

    for name, capacity, items, expected in test_cases:

        print("\nTEST:", name)
        print("Items:", items)
        print("Capacity:", capacity)

        exact = exact_bin_packing(
            items,
            capacity,
            time_limit=5
        )

        if exact["status"] != "OPTIMAL":

            print("Exact result not proven.")
            all_passed = False
            continue

        optimum = exact["optimal_bins"]

        print("\nExact Optimal Bins:", optimum)
        print("Expected Optimal Bins:", expected)
        print("Search Nodes:", exact["nodes"])

        if optimum != expected:

            print("VALIDATION FAILED: Wrong optimum.")
            all_passed = False
            continue

        print("\nAPPROXIMATION COMPARISON")
        print("-" * 75)

        for algorithm_name, algorithm in algorithms.items():

            bins = algorithm(items, capacity)

            validate(items, bins, capacity)

            count = len(bins)
            gap = count - optimum

            assert gap >= 0, (
                "Approximation used fewer bins than proven optimum"
            )

            print(
                f"{algorithm_name:<28}"
                f"Bins: {count:<6}"
                f"Gap: {gap}"
            )

        validate(
            items,
            exact["bins"],
            capacity
        )

        print("\nTEST RESULT: PASSED")

    print("\n" + "=" * 85)

    if all_passed:
        print("ALL VALIDATION TESTS PASSED!")
    else:
        print("SOME VALIDATION TESTS NEED REVIEW.")

    print("=" * 85)


if __name__ == "__main__":
    main()
