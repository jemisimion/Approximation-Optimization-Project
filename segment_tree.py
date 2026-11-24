
import time


# SEGMENT TREE DATA STRUCTURE
class SegmentTree:

    def __init__(self, size):
        self.n = size
        self.tree = [0] * (4 * size)

    # Update remaining capacity
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

    # Find first bin with sufficient capacity
    def find_first(self, required):

        if self.tree[1] < required:
            return -1

        return self._find(1, 0, self.n - 1, required)

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


# NORMAL FIRST FIT FOR COMPARISON
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


# SEGMENT TREE-BASED FIRST FIT
def segment_tree_first_fit(items, capacity):

    if capacity <= 0:
        raise ValueError("Capacity must be positive.")

    if any(item <= 0 or item > capacity for item in items):
        raise ValueError("Invalid item size.")

    if not items:
        return []

    tree = SegmentTree(len(items))

    bins = []
    remaining = [0] * len(items)

    for item in items:

        # Search for the first suitable bin
        index = tree.find_first(item)

        if index == -1:

            # Open a new bin
            index = len(bins)

            bins.append([item])

            remaining[index] = capacity - item

            tree.update(index, remaining[index])

        else:

            # Place item in existing bin
            bins[index].append(item)

            remaining[index] -= item

            tree.update(index, remaining[index])

    return bins


# FIRST FIT DECREASING WITH SEGMENT TREE
def segment_tree_ffd(items, capacity):

    sorted_items = sorted(items, reverse=True)

    return segment_tree_first_fit(sorted_items, capacity)


# MAIN PROGRAM
def main():

    capacity = 10

    items = [5, 7, 5, 2, 4, 2, 5, 1, 6]

    print("=" * 55)
    print("SEGMENT TREE OPTIMIZED BIN PACKING")
    print("=" * 55)

    print("Capacity:", capacity)
    print("Items:", items)

    # Normal First Fit
    start = time.perf_counter()
    normal_bins = first_fit(items, capacity)
    normal_time = time.perf_counter() - start

    # Segment Tree First Fit
    start = time.perf_counter()
    optimized_bins = segment_tree_first_fit(
        items, capacity
    )
    optimized_time = time.perf_counter() - start

    # Segment Tree FFD
    start = time.perf_counter()
    ffd_bins = segment_tree_ffd(items, capacity)
    ffd_time = time.perf_counter() - start

    # Verify identical First Fit arrangement
    assert normal_bins == optimized_bins

    print("\nNORMAL FIRST FIT")
    print(normal_bins)
    print("Total bins:", len(normal_bins))

    print("\nSEGMENT TREE FIRST FIT")
    print(optimized_bins)
    print("Total bins:", len(optimized_bins))

    print("\nSEGMENT TREE FIRST FIT DECREASING")
    print(ffd_bins)
    print("Total bins:", len(ffd_bins))

    print("\nEXECUTION TIME COMPARISON")
    print("-" * 55)

    print("Normal First Fit:",
          round(normal_time * 1000, 4), "ms")

    print("Segment Tree First Fit:",
          round(optimized_time * 1000, 4), "ms")

    print("Segment Tree FFD:",
          round(ffd_time * 1000, 4), "ms")

    print("\nVERIFICATION")
    print("Normal and optimized First Fit match:",
          normal_bins == optimized_bins)

    print("=" * 55)


if __name__ == "__main__":
    main()
