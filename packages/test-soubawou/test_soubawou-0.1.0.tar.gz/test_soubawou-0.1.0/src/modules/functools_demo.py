"""Demonstration of key functools utilities in Python.

This module demonstrates the use of several functools decorators and utilities:
- cache: Simple unbounded function cache (Python 3.9+)
- lru_cache: Least Recently Used bounded function cache
- cached_property: Property with caching for class instances
- partial: Function with partially applied arguments

Run this file directly to see the demonstrations in action.
"""

import functools
import time
from typing import TypeVar

# Type variables for better type hints
T = TypeVar("T")
R = TypeVar("R")

# ========== @cache demonstration ==========


@functools.cache
def fibonacci_cached(n: int) -> int:
    """Calculate Fibonacci number with memoization using @cache."""
    if n <= 1:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


def fibonacci_uncached(n: int) -> int:
    """Calculate Fibonacci number without caching."""
    if n <= 1:
        return n
    return fibonacci_uncached(n - 1) + fibonacci_uncached(n - 2)


def demonstrate_cache() -> None:
    """Compare performance of cached vs uncached Fibonacci calculation."""
    print("\n===== @cache Demonstration =====")

    test_value = 35

    # Test uncached version first
    start_time = time.time()
    result = fibonacci_uncached(test_value)
    uncached_time = time.time() - start_time
    print(f"Uncached fibonacci({test_value}) = {result}")
    print(f"Time without caching: {uncached_time:.6f} seconds")

    # Test cached version
    start_time = time.time()
    result = fibonacci_cached(test_value)
    cached_time = time.time() - start_time
    print(f"Cached fibonacci({test_value}) = {result}")
    print(f"Time with @cache: {cached_time:.6f} seconds")

    # Demonstrate repeated calls benefit even more
    start_time = time.time()
    for _ in range(10):
        fibonacci_cached(test_value)
    repeat_time = time.time() - start_time
    print(f"Time for 10 repeated cached calls: {repeat_time:.6f} seconds")

    # Show cache info
    cache_info = fibonacci_cached.cache_info()
    print(f"Cache info: {cache_info}")

    # Clear cache and demonstrate
    fibonacci_cached.cache_clear()
    print("Cache cleared")
    cache_info = fibonacci_cached.cache_info()
    print(f"Cache info after clearing: {cache_info}")


# ========== @lru_cache demonstration ==========


@functools.lru_cache(maxsize=128)
def expensive_computation(n: int, factor: float = 1.0) -> float:
    """Simulate an expensive computation with configurable LRU cache."""
    time.sleep(0.01)  # Simulate computation time
    return n * factor


def demonstrate_lru_cache() -> None:
    """Demonstrate LRU cache behavior and cache statistics."""
    print("\n===== @lru_cache Demonstration =====")

    # First call - should be slow
    start_time = time.time()
    result = expensive_computation(42)
    first_call_time = time.time() - start_time
    print(f"First call result: {result}")
    print(f"First call time: {first_call_time:.6f} seconds")

    # Second call with same args - should be fast due to cache
    start_time = time.time()
    result = expensive_computation(42)
    second_call_time = time.time() - start_time
    print(f"Second call result: {result}")
    print(f"Second call time: {second_call_time:.6f} seconds (cached)")
    print(f"Speed improvement: {first_call_time / second_call_time:.2f}x faster")

    # Different args - should be slow again
    start_time = time.time()
    result = expensive_computation(43)
    print(f"Different args result: {result}")
    print(f"Different args time: {time.time() - start_time:.6f} seconds")

    # Show cache statistics
    cache_info = expensive_computation.cache_info()
    print(f"Cache info: {cache_info}")

    # Demonstrate cache eviction (for small maxsize)
    small_cache = functools.lru_cache(maxsize=5)(expensive_computation.__wrapped__)

    print("\nDemonstrating cache eviction with small cache (maxsize=5):")
    for i in range(10):
        small_cache(i)

    cache_info = small_cache.cache_info()
    print(f"Small cache info after 10 unique calls: {cache_info}")
    print(
        f"Hits: {cache_info.hits}, "
        f"Misses: {cache_info.misses}, "
        f"Maxsize: {cache_info.maxsize}, "
        f"Size: {cache_info.currsize}"
    )
    print(
        f"Hits: {cache_info.hits}, "
        f"Misses: {cache_info.misses}, "
        f"Maxsize: {cache_info.maxsize}, "
        f"Size: {cache_info.currsize}"
    )


# ========== @cached_property demonstration ==========


class DataAnalyzer:
    """Class demonstrating @cached_property for expensive computations."""

    def __init__(self, data: list[float]):
        self.data = data
        self._computation_count = 0
        print(f"DataAnalyzer initialized with {len(data)} data points")

    @property
    def regular_property_stats(self) -> dict[str, float]:
        """Calculate statistics as a regular property (recomputed each time)."""
        self._computation_count += 1
        return {
            "mean": sum(self.data) / len(self.data),
            "min": min(self.data),
            "max": max(self.data),
            "computation_count": self._computation_count,
        }

    @functools.cached_property
    def cached_stats(self) -> dict[str, float]:
        """Calculate statistics with caching (computed once per instance)."""
        self._computation_count += 1
        time.sleep(0.1)  # Simulate expensive computation
        return {
            "mean": sum(self.data) / len(self.data),
            "min": min(self.data),
            "max": max(self.data),
            "computation_count": self._computation_count,
        }


def demonstrate_cached_property() -> None:
    """Demonstrate the behavior of @cached_property vs regular @property."""
    print("\n===== @cached_property Demonstration =====")

    # Create test data
    import random

    random.seed(42)  # For reproducibility
    data = [random.random() for _ in range(1000)]

    # Create analyzer instance
    analyzer = DataAnalyzer(data)

    # Test regular property (recomputed each time)
    print("\nRegular property behavior:")
    for i in range(3):
        start_time = time.time()
        stats = analyzer.regular_property_stats
        print(
            f"Call {i + 1}: Computation #{stats['computation_count']} took {time.time() - start_time:.6f} seconds"  # noqa
        )

    # Test cached property (computed once)
    print("\nCached property behavior:")
    for i in range(3):
        start_time = time.time()
        stats = analyzer.cached_stats
        print(
            f"Call {i + 1}: Computation #{stats['computation_count']} took {time.time() - start_time:.6f} seconds"  # noqa
        )

    # Demonstrate that the cache is per-instance
    print("\nDemonstrating per-instance caching:")
    analyzer2 = DataAnalyzer(data[:500])  # Different instance with different data
    start_time = time.time()
    stats = analyzer2.cached_stats
    print(
        f"New instance: Computation #{stats['computation_count']} took {time.time() - start_time:.6f} seconds"  # noqa
    )


# ========== partial demonstration ==========


def power(base: float, exponent: float) -> float:
    """Calculate base raised to exponent power."""
    return base**exponent


def format_number(
    number: float, precision: int = 2, prefix: str = "", suffix: str = ""
) -> str:
    """Format a number with specified precision and optional prefix/suffix."""
    return f"{prefix}{number:.{precision}f}{suffix}"


def demonstrate_partial() -> None:
    """Demonstrate the use of functools.partial for function specialization."""
    print("\n===== functools.partial Demonstration =====")

    # Create specialized versions of the power function
    square = functools.partial(power, exponent=2)
    cube = functools.partial(power, exponent=3)
    square_root = functools.partial(power, exponent=0.5)

    # Use the specialized functions
    value = 4
    print(f"Original: power({value}, 2) = {power(value, 2)}")
    print(f"Partial:  square({value}) = {square(value)}")
    print(f"Partial:  cube({value}) = {cube(value)}")
    print(f"Partial:  square_root({value}) = {square_root(value)}")

    # Partial with multiple pre-filled parameters
    dollar_formatter = functools.partial(format_number, precision=2, prefix="$")
    percent_formatter = functools.partial(format_number, precision=1, suffix="%")

    amount = 1234.5678
    print(f"\nFormatting {amount}:")
    print(f"Default format: {format_number(amount)}")
    print(f"As dollars: {dollar_formatter(amount)}")
    print(f"As percentage: {percent_formatter(amount)}")

    # Demonstrate that you can override the pre-filled parameters
    print(f"Dollar with 0 decimals: {dollar_formatter(amount, precision=0)}")

    # Show introspection of partial objects
    print("\nIntrospecting partial objects:")
    print(f"square.func = {square.func.__name__}")
    print(f"square.args = {square.args}")
    print(f"square.keywords = {square.keywords}")


# ========== Advanced bonus: Combining techniques ==========


def advanced_demo() -> None:
    """Demonstrate combining multiple functools features."""
    print("\n===== Advanced Combinations =====")

    # Combine partial with lru_cache
    @functools.lru_cache(maxsize=32)
    def _calculate_powers(base: float, exponent: float) -> float:
        print(
            f"Computing {base}^{exponent}..."
        )  # Shows when actual computation happens
        return base**exponent

    # Create specialized cached functions using partial
    cached_square = functools.partial(_calculate_powers, exponent=2)
    cached_cube = functools.partial(_calculate_powers, exponent=3)

    print("Using cached partial functions:")
    print(f"First call to cached_square(4): {cached_square(4)}")
    print(f"Second call to cached_square(4): {cached_square(4)}")  # Should use cache
    print(f"First call to cached_square(5): {cached_square(5)}")  # New computation
    print(f"First call to cached_cube(4): {cached_cube(4)}")  # New computation

    # Show cache statistics
    print(f"Cache info: {_calculate_powers.cache_info()}")


# Run all demonstrations when executed directly
if __name__ == "__main__":
    demonstrate_cache()
    demonstrate_lru_cache()
    demonstrate_cached_property()
    demonstrate_partial()
    advanced_demo()

    print("\nAll demonstrations completed!")
