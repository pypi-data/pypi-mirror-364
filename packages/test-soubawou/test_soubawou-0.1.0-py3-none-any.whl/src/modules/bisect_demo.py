"""Demonstration of Python's bisect module usage.

Using bisect is not about replacing sort but avoiding expensive resorting
when data is already sorted. Key advantages:

1. Efficient insertions into a sorted list:
   - bisect.insort() locates insertion point via binary search (O(log n))
   - More efficient than append + sort for incremental updates
   - Avoids O(n log n) resort operations when adding new items
"""

import bisect
import random
import time
from typing import List, Tuple


def binary_search_demo(sorted_list: List[int], target: int) -> Tuple[bool, int]:
    """Demonstrate binary search using bisect_left.

    Args:
        sorted_list: A sorted list of integers
        target: The value to search for

    Returns:
        Tuple containing (found_status, position)
    """
    pos = bisect.bisect_left(sorted_list, target)

    # Check if the target is in the list
    if pos < len(sorted_list) and sorted_list[pos] == target:
        return True, pos
    else:
        return False, pos  # Position where it would be inserted


def insertion_demo(sorted_list: List[int], new_value: int) -> List[int]:
    """Demonstrate insertion while maintaining sort order.

    Args:
        sorted_list: A sorted list of integers
        new_value: The value to insert

    Returns:
        The updated sorted list
    """
    # Create a copy to avoid modifying the original
    result = sorted_list.copy()
    bisect.insort(result, new_value)
    return result


def performance_comparison(size: int = 10000) -> None:
    """Compare performance of sorted insertion vs regular sort.

    Args:
        size: Size of the list to test with
    """
    print(f"Performance comparison with list size {size}:")

    # Method 1: Insert into sorted list using bisect
    sorted_list: List[int] = []
    start = time.time()
    for _ in range(size):
        bisect.insort(sorted_list, random.randint(0, size * 10))
    bisect_time = time.time() - start
    print(f"  Insertion with bisect.insort: {bisect_time:.5f} seconds")

    # Method 2: Append and sort
    unsorted_list: List[int] = []
    start = time.time()
    for _ in range(size):
        unsorted_list.append(random.randint(0, size * 10))
    unsorted_list.sort()
    sort_time = time.time() - start
    print(f"  Append and sort: {sort_time:.5f} seconds")

    print(f"  Ratio (sort/bisect): {sort_time / bisect_time:.2f}\n")


def grade_mapping_demo() -> None:
    """Demonstrate using bisect for mapping scores to letter grades."""
    # Define the grade thresholds
    breakpoints = [60, 70, 80, 90]
    grades = ["F", "D", "C", "B", "A"]

    scores = [33, 59, 60, 61, 75, 89, 90, 91, 100]

    print("Grade mapping example:")
    for score in scores:
        # Find the index where this score would go
        index = bisect.bisect(breakpoints, score)
        # Map to corresponding grade
        grade = grades[index]
        print(f"  Score {score} maps to grade {grade}")
    print()


def interval_search_demo() -> None:
    """Demonstrate finding which interval a value belongs to."""
    intervals = [0, 10, 20, 30, 40, 50]
    interval_names = ["0-9", "10-19", "20-29", "30-39", "40-49", "50+"]

    test_values = [5, 10, 15, 25, 50, 75]

    print("Interval search example:")
    for value in test_values:
        index = bisect.bisect_right(intervals, value) - 1
        print(f"  Value {value} is in interval {interval_names[index]}")
    print()


def main() -> None:
    """Main entry point showcasing bisect module capabilities."""
    print("BISECT MODULE DEMONSTRATION")
    print("===========================\n")

    # Basic binary search demo
    sorted_data = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    print(f"Sorted list: {sorted_data}")

    targets = [20, 42, 90]
    print("Binary search examples:")
    for target in targets:
        found, position = binary_search_demo(sorted_data, target)
        if found:
            print(f"  Found {target} at position {position}")
        else:
            print(f"  {target} not found, would be inserted at position {position}")
    print()

    # Insertion demo
    print("Insertion examples:")
    original = [10, 20, 30, 40, 50]
    print(f"  Original list: {original}")

    # Insert in the middle
    updated = insertion_demo(original, 35)
    print(f"  After inserting 35: {updated}")

    # Insert at the beginning
    updated = insertion_demo(original, 5)
    print(f"  After inserting 5: {updated}")

    # Insert at the end
    updated = insertion_demo(original, 60)
    print(f"  After inserting 60: {updated}")
    print()

    # More advanced use cases
    grade_mapping_demo()
    interval_search_demo()

    # Performance comparison
    performance_comparison(5000)

    print("Bisect module demonstration completed")


if __name__ == "__main__":
    main()
