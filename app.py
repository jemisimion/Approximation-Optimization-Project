from exact_solver import exact_bin_packing
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import time
import math
from pathlib import Path


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Bin Packing Optimization",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Approximation Strategies for Computationally Hard Optimization Problems")
st.subheader("Bin Packing Problem - Algorithm Comparison")

st.write(
    "An interactive system for comparing approximation "
    "algorithms and Segment Tree-based optimization."
)


# ==========================================
# 1. NEXT FIT
# ==========================================

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


# ==========================================
# 2. FIRST FIT
# ==========================================

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


# ==========================================
# 3. BEST FIT
# ==========================================

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


# ==========================================
# 4. FIRST FIT DECREASING
# ==========================================

def first_fit_decreasing(items, capacity):

    sorted_items = sorted(items, reverse=True)

    return first_fit(sorted_items, capacity)


# ==========================================
# 5. SEGMENT TREE DATA STRUCTURE
# ==========================================

class SegmentTree:

    def __init__(self, size):

        self.n = size
        self.tree = [0] * (4 * size + 4)

    # Update remaining bin capacity
    def update(self, index, value):

        self._update(
            1, 0, self.n - 1, index, value
        )

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


# ==========================================
# 6. SEGMENT TREE FIRST FIT
# ==========================================

def segment_tree_first_fit(items, capacity):

    if not items:
        return []

    size = len(items)

    tree = SegmentTree(size)

    bins = []
    remaining = [0] * size

    for item in items:

        index = tree.find_first(item)

        if index == -1:

            index = len(bins)

            bins.append([item])

            remaining[index] = capacity - item

            tree.update(
                index, remaining[index]
            )

        else:

            bins[index].append(item)

            remaining[index] -= item

            tree.update(
                index, remaining[index]
            )

    return bins


# ==========================================
# 7. SEGMENT TREE FIRST FIT DECREASING
# ==========================================

def segment_tree_ffd(items, capacity):

    sorted_items = sorted(items, reverse=True)

    return segment_tree_first_fit(
        sorted_items, capacity
    )


# ==========================================
# BIN VISUALIZATION
# ==========================================

def plot_bins(bins, capacity, title):

    fig, ax = plt.subplots(
        figsize=(10, max(2.5, len(bins) * 0.7))
    )

    for index, bin_items in enumerate(bins):

        y = len(bins) - index - 1

        left = 0

        for j, item in enumerate(bin_items):

            color = plt.cm.Set3(j % 12 / 12)

            ax.barh(
                y,
                item,
                left=left,
                color=color,
                edgecolor="black",
                height=0.65
            )

            ax.text(
                left + item / 2,
                y,
                str(item),
                ha="center",
                va="center"
            )

            left += item

    ax.set_xlim(0, capacity)

    ax.set_yticks(range(len(bins)))

    ax.set_yticklabels(
        [f"Bin {i}" for i in range(len(bins), 0, -1)]
    )

    ax.set_xlabel("Bin Capacity")
    ax.set_title(title)

    ax.grid(axis="x", alpha=0.3)

    fig.tight_layout()

    return fig


# ==========================================
# ALGORITHM LIST
# ==========================================

algorithms = {

    "Next Fit": next_fit,

    "First Fit": first_fit,

    "Best Fit": best_fit,

    "First Fit Decreasing": first_fit_decreasing,

    "Segment Tree First Fit": segment_tree_first_fit,

    "Segment Tree FFD": segment_tree_ffd

}


# ==========================================
# SIDEBAR INPUT
# ==========================================

st.sidebar.header("⚙️ Input Settings")

with st.sidebar.form("input_form"):

    capacity = st.number_input(
        "Enter Bin Capacity",
        min_value=1,
        value=10,
        step=1
    )

    items_text = st.text_input(
        "Enter Item Sizes",
        value="5,7,5,2,4,2,5,1,6"
    )

    submitted = st.form_submit_button(
        "🚀 Run All Algorithms",
        use_container_width=True
    )


# ==========================================
# MAIN APPLICATION
# ==========================================

if submitted:

    try:

        items = [
            int(x.strip())
            for x in items_text.split(",")
        ]

        if not items:

            st.error("Enter at least one item.")

        elif any(item <= 0 for item in items):

            st.error("All item sizes must be positive.")

        elif any(item > capacity for item in items):

            st.error("An item cannot exceed bin capacity.")

        else:

            st.success("All six algorithms executed successfully!")

            results = []

            # EXECUTE SIX ALGORITHMS
            for name, algorithm in algorithms.items():

                start = time.perf_counter()

                bins = algorithm(items, capacity)

                elapsed = time.perf_counter() - start

                # VALIDATION
                assert sorted(items) == sorted(
                    item for b in bins for item in b
                )

                assert all(
                    sum(b) <= capacity for b in bins
                )

                utilization = (
                    sum(items) /
                    (len(bins) * capacity)
                ) * 100

                results.append({

                    "Algorithm": name,

                    "Bins": bins,

                    "Bin Count": len(bins),

                    "Utilization": utilization,

                    "Execution Time (ms)": elapsed * 1000

                })

            # ==================================
            # PERFORMANCE SUMMARY
            # ==================================

            st.header("📊 Performance Summary")

            lower_bound = math.ceil(
                sum(items) / capacity
            )

            best_count = min(
                r["Bin Count"] for r in results
            )

            best_names = [
                r["Algorithm"]
                for r in results
                if r["Bin Count"] == best_count
            ]

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Total Items",
                len(items)
            )

            c2.metric(
                "Total Item Size",
                sum(items)
            )

            c3.metric(
                "Lower Bound",
                lower_bound
            )

            c4.metric(
                "Best Bin Count",
                best_count
            )

            st.info(
                "Best result for this input: "
                + ", ".join(best_names)
            )

            # ==================================
            # COMPARISON TABLE
            # ==================================

            st.header("📋 Algorithm Comparison")

            comparison = pd.DataFrame([

                {

                    "Algorithm": r["Algorithm"],

                    "Number of Bins": r["Bin Count"],

                    "Utilization (%)": round(
                        r["Utilization"], 2
                    ),

                    "Execution Time (ms)": round(
                        r["Execution Time (ms)"], 6
                    )

                }

                for r in results

            ])

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )

            # ==================================
            # BIN COUNT CHART
            # ==================================

            st.header("📈 Number of Bins Comparison")

            fig, ax = plt.subplots(figsize=(12, 5))

            names = [
                r["Algorithm"] for r in results
            ]

            counts = [
                r["Bin Count"] for r in results
            ]

            bars = ax.bar(names, counts)

            for bar, count in zip(bars, counts):

                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    count + 0.05,
                    str(count),
                    ha="center"
                )

            ax.set_ylabel("Number of Bins")
            ax.set_title("Comparison of Six Algorithms")

            ax.set_ylim(0, max(counts) + 1)

            ax.grid(axis="y", alpha=0.3)

            plt.xticks(rotation=20, ha="right")

            fig.tight_layout()

            st.pyplot(fig)

            plt.close(fig)

            # ==================================
            # EXECUTION TIME CHART
            # ==================================

            st.header("⏱️ Execution Time Comparison")

            time_df = pd.DataFrame({

                "Algorithm": names,

                "Execution Time (ms)": [
                    r["Execution Time (ms)"]
                    for r in results
                ]

            })

            st.bar_chart(
                time_df.set_index("Algorithm")
            )

            # ==================================
            # BIN VISUALIZATION
            # ==================================

            st.header("📦 Individual Bin Visualization")

            for r in results:

                with st.expander(
                    f"{r['Algorithm']} - "
                    f"{r['Bin Count']} Bins",
                    expanded=(r["Bin Count"] == best_count)
                ):

                    st.write(
                        "Bin utilization:",
                        round(r["Utilization"], 2),
                        "%"
                    )

                    for i, b in enumerate(r["Bins"], 1):

                        st.write(
                            f"Bin {i}: {b} | "
                            f"Used: {sum(b)} | "
                            f"Remaining: {capacity - sum(b)}"
                        )

                    fig = plot_bins(
                        r["Bins"],
                        capacity,
                        r["Algorithm"]
                    )

                    st.pyplot(fig)

                    plt.close(fig)

            # ==================================
            # FINAL RESULT
            # ==================================

            st.header("🏆 Final Result")

            st.success(
                f"Minimum bins used: {best_count}"
            )

            st.write(
                f"Theoretical lower bound: {lower_bound}"
            )

            st.write(
                "Gap from lower bound:",
                best_count - lower_bound
            )

            st.caption(
                "The lower bound is not necessarily the exact "
                "optimum. The winning algorithm is the one using "
                "the fewest bins among the six tested algorithms."
            )


    except ValueError as e:
        st.error(f"Invalid input: {e}")


# ==========================================
# EXPERIMENTAL PERFORMANCE ANALYSIS
# ==========================================

# ==========================================
# EXPERIMENTAL PERFORMANCE ANALYSIS
# ==========================================

st.divider()

st.header("🧪 Experimental Performance Analysis")

folder = Path(__file__).resolve().parent / "results"

benchmark_file = folder / "performance.csv"

if benchmark_file.exists():

    benchmark_df = pd.read_csv(benchmark_file)

    st.success("Benchmark results loaded successfully!")

    st.subheader("Benchmark Results")

    st.dataframe(
        benchmark_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "📥 Download Benchmark Results",
        data=benchmark_df.to_csv(index=False),
        file_name="performance_results.csv",
        mime="text/csv",
        key="benchmark_download"
    )

    if {"Items", "Algorithm", "Bins"}.issubset(benchmark_df.columns):

        bin_chart = benchmark_df.pivot(
            index="Items",
            columns="Algorithm",
            values="Bins"
        ).sort_index()

        st.subheader("Number of Bins vs Dataset Size")

        st.line_chart(bin_chart)

    if {
        "Items", "Algorithm", "Execution Time (ms)"
    }.issubset(benchmark_df.columns):

        time_chart = benchmark_df.pivot(
            index="Items",
            columns="Algorithm",
            values="Execution Time (ms)"
        ).sort_index()

        st.subheader("Execution Time vs Dataset Size")

        st.line_chart(time_chart)

else:

    st.warning(
        "Benchmark file not found. Run py benchmark.py first."
    )


# ==========================================
# ADVANCED EXPERIMENTAL ANALYSIS
# ==========================================

st.divider()

st.header("🔬 Advanced Experimental Analysis")

advanced_file = folder / "advanced_results.csv"

if advanced_file.exists():

    advanced_df = pd.read_csv(advanced_file)

    st.success("Advanced experimental results loaded!")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Dataset Sizes",
        advanced_df["Items"].nunique()
    )

    c2.metric(
        "Input Patterns",
        advanced_df["Pattern"].nunique()
    )

    c3.metric(
        "Algorithms Tested",
        advanced_df["Algorithm"].nunique()
    )

    st.subheader("Advanced Experimental Results")

    st.dataframe(
        advanced_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "📥 Download Advanced Results",
        data=advanced_df.to_csv(index=False),
        file_name="advanced_results.csv",
        mime="text/csv",
        key="advanced_download"
    )

    patterns = advanced_df["Pattern"].unique().tolist()

    tabs = st.tabs(patterns)

    for tab, pattern in zip(tabs, patterns):

        with tab:

            selected = advanced_df[
                advanced_df["Pattern"] == pattern
            ].copy()

            st.subheader(f"{pattern} Input")

            for metric, heading in [

                ("Bins", "Number of Bins"),

                ("Execution Time (ms)", "Execution Time"),

                ("Utilization (%)", "Bin Utilization")

            ]:

                if metric in selected.columns:

                    pivot = selected.pivot(
                        index="Items",
                        columns="Algorithm",
                        values=metric
                    ).sort_index()

                    st.write(heading)

                    st.line_chart(pivot)

else:

    st.warning(
        "Advanced results not found. "
        "Run py advanced_tests.py first."
    )


# ==========================================
# ALGORITHM COMPLEXITY ANALYSIS
# ==========================================

st.divider()

st.header("🧠 Algorithm Complexity Analysis")

complexity_data = {

    "Algorithm": [

        "Next Fit",

        "First Fit",

        "Best Fit",

        "First Fit Decreasing",

        "Segment Tree First Fit",

        "Segment Tree FFD"

    ],

    "Time Complexity": [

        "O(n)",

        "O(n²)",

        "O(n²)",

        "O(n²)",

        "O(n log n)",

        "O(n log n)"

    ],

    "Space Complexity": [

        "O(n)",

        "O(n)",

        "O(n)",

        "O(n)",

        "O(n)",

        "O(n)"

    ],

    "Working Principle": [

        "Uses the current bin.",

        "Finds the first available bin.",

        "Finds the bin with minimum remaining space.",

        "Sorts items and applies First Fit.",

        "Uses Segment Tree to find the first suitable bin.",

        "Sorts items and applies Segment Tree First Fit."

    ]

}

complexity_df = pd.DataFrame(complexity_data)

st.dataframe(
    complexity_df,
    use_container_width=True,
    hide_index=True
)

st.subheader("Complexity Explanation")

st.markdown("""
### Next Fit
Checks only the current bin for each item.

Time Complexity: O(n)

### First Fit
Searches existing bins sequentially for each item.

Time Complexity: O(n²)

### Best Fit
Searches all existing bins to find the best placement.

Time Complexity: O(n²)

### First Fit Decreasing
Sorts the items and applies First Fit.

Time Complexity: O(n²)

### Segment Tree First Fit
Uses a Segment Tree to locate the first suitable bin.

Time Complexity: O(n log n)

### Segment Tree FFD
Sorts the items and applies Segment Tree First Fit.

Time Complexity: O(n log n)

All implementations require O(n) space to store bins,
items and supporting data structures.
""")


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "M.Tech CSE | Advanced Data Structures and Algorithms "
    "| Bin Packing Approximation Project"
)

# ==========================================
# EXACT OPTIMIZATION AND VALIDATION
# ==========================================

st.divider()

st.header("🎯 Exact Bin Packing Optimization")

st.write(
    "Compare approximation algorithms with the "
    "exact optimal solution using Backtracking "
    "and Branch and Bound."
)

with st.form("exact_solver_form"):

    exact_capacity = st.number_input(
        "Exact Solver - Bin Capacity",
        min_value=1,
        value=10,
        step=1
    )

    exact_items_text = st.text_input(
        "Enter items for exact optimization",
        value="5,7,5,2,4,2,5,1,6"
    )

    exact_time_limit = st.number_input(
        "Maximum search time (seconds)",
        min_value=1,
        max_value=30,
        value=5
    )

    run_exact = st.form_submit_button(
        "🔍 Find Optimal Solution"
    )


if run_exact:

    try:

        exact_items = [
            int(x.strip())
            for x in exact_items_text.split(",")
        ]

        if not exact_items:

            st.error("Enter at least one item.")

        elif any(x <= 0 for x in exact_items):

            st.error("All items must be positive.")

        elif any(x > exact_capacity for x in exact_items):

            st.error("An item exceeds bin capacity.")

        else:

            with st.spinner("Searching for optimal solution..."):

                exact_result = exact_bin_packing(
                    exact_items,
                    exact_capacity,
                    time_limit=exact_time_limit
                )

            st.subheader("Exact Solver Results")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Lower Bound",
                exact_result["lower_bound"]
            )

            c2.metric(
                "Greedy Upper Bound",
                exact_result["upper_bound"]
            )

            c3.metric(
                "Search Nodes",
                exact_result["nodes"]
            )

            st.write(
                "Execution Time:",
                round(exact_result["time"] * 1000, 4),
                "ms"
            )

            st.write(
                "Solver Status:",
                exact_result["status"]
            )

            if exact_result["status"] == "OPTIMAL":

                optimum = exact_result["optimal_bins"]

                st.success(
                    f"Optimal solution proven: {optimum} bins."
                )

                comparison_rows = []

                for name, algorithm in algorithms.items():

                    bins = algorithm(
                        exact_items,
                        exact_capacity
                    )

                    comparison_rows.append({

                        "Algorithm": name,

                        "Bins Used": len(bins),

                        "Difference from Optimum": (
                            len(bins) - optimum
                        )

                    })

                comparison_rows.append({

                    "Algorithm": "Exact Solver",

                    "Bins Used": optimum,

                    "Difference from Optimum": 0

                })

                exact_df = pd.DataFrame(comparison_rows)

                st.subheader(
                    "Approximation vs Optimal Comparison"
                )

                st.dataframe(
                    exact_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.subheader("Optimal Bin Arrangement")

                for i, b in enumerate(
                    exact_result["bins"], 1
                ):

                    st.write(
                        f"Bin {i}: {b} | "
                        f"Used: {sum(b)} | "
                        f"Remaining: {exact_capacity - sum(b)}"
                    )

                fig = plot_bins(
                    exact_result["bins"],
                    exact_capacity,
                    "Exact Optimal Bin Arrangement"
                )

                st.pyplot(fig)
                plt.close(fig)

            else:

                st.warning(
                    "The time limit was reached. "
                    "Optimality has not been proven."
                )

                st.write(
                    "Best known feasible bin count:",
                    exact_result["upper_bound"]
                )

                st.write(
                    "Lower bound:",
                    exact_result["lower_bound"]
                )

    except ValueError as e:

        st.error(f"Invalid input: {e}")
