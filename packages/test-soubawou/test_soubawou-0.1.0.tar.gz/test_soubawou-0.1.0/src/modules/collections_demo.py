#!/usr/bin/env python3
"""Demo script showcasing Python's collections module with examples of:

- deque: double-ended queue for efficient append/pop from both ends
- namedtuple: factory function for creating tuple subclasses with named fields
- Counter: dict subclass for counting hashable objects
"""

import time
from collections import Counter, deque, namedtuple

# When to Reach for a Deque
# 	•	Queue / Stack patterns where you need both FIFO and LIFO operations.
# 	•	Sliding-window algorithms (e.g. moving sums, maxima).
# 	•	BFS graph traversals (fast popleft()).
# 	•	Any scenario where youd otherwise use list.pop(0) or list.insert(0, x).


def deque_demo() -> None:
    """Demonstrates the usage and advantages of collections.deque."""
    print("\n===== DEQUE DEMO =====")

    # Create a deque
    d = deque([1, 2, 3, 4, 5])
    print(f"Original deque: {d}")

    # Append and appendleft operations
    d.append(6)
    d.appendleft(0)
    print(f"After append(6) and appendleft(0): {d}")

    # Pop and popleft operations
    right_item = d.pop()
    left_item = d.popleft()
    print(f"Popped from right: {right_item}, Popped from left: {left_item}")
    print(f"After pop operations: {d}")

    # Rotate the deque
    d.rotate(2)  # Rotate two steps to the right
    print(f"After rotate(2): {d}")

    d.rotate(-2)  # Rotate two steps to the left
    print(f"After rotate(-2): {d}")

    # Performance comparison with list for left operations
    print("\nPerformance comparison - inserting at the beginning:")

    # List performance
    start_time = time.time()
    lst = []
    for i in range(100000):
        lst.insert(0, i)  # Insert at the beginning (expensive for lists)
    list_time = time.time() - start_time
    print(f"List insert(0, i) time: {list_time:.5f} seconds")

    # Deque performance
    start_time = time.time()
    d = deque()
    for i in range(100000):
        d.appendleft(i)  # Insert at the beginning (efficient for deque)
    deque_time = time.time() - start_time
    print(f"Deque appendleft(i) time: {deque_time:.5f} seconds")
    print(f"Deque is {list_time / deque_time:.1f}x faster for left operations")


# Prefer typing NamedTuple
def namedtuple_demo() -> None:
    """Demonstrates the usage of collections.namedtuple."""
    print("\n===== NAMEDTUPLE DEMO =====")

    # Define a namedtuple type
    Person = namedtuple("Person", ["name", "age", "city"])

    # Create instances
    alice = Person(name="Alice", age=30, city="New York")
    bob = Person("Bob", 25, "San Francisco")  # Positional arguments also work

    # Access by name
    print(f"Person: {alice.name}, {alice.age}, {alice.city}")

    # Access by index (like a regular tuple)
    print(f"First person's info by index: {alice[0]}, {alice[1]}, {alice[2]}")

    # Unpacking
    name, age, city = bob
    print(f"Unpacked: {name}, {age}, {city}")

    # Convert to dictionary
    alice_dict = alice._asdict()
    print(f"As dictionary: {alice_dict}")

    # Create a new instance with one field replaced
    charlie = alice._replace(name="Charlie", age=35)
    print(f"New person from replacement: {charlie}")

    # Use in a function that takes multiple arguments
    def greeting(name: str, age: int, city: str) -> str:
        return f"Hello {name}, age {age} from {city}!"

    print(greeting(*alice))  # Unpacking a namedtuple as function arguments

    # Comparison with regular dictionaries
    print("\nComparing with dictionaries:")
    print(f"Memory size of namedtuple: {Person.__sizeof__(alice)} bytes")
    regular_dict = {"name": "Alice", "age": 30, "city": "New York"}
    print(f"Memory size of dict: {regular_dict.__sizeof__()} bytes")


def counter_demo() -> None:
    """Demonstrates the usage of collections.Counter."""
    print("\n===== COUNTER DEMO =====")

    # Create a Counter from a sequence
    text = "The quick brown fox jumps over the lazy dog"
    char_counts = Counter(text.lower())
    print(f"Character counts: {char_counts}")

    # Get the most common elements
    print(f"Most common characters: {char_counts.most_common(3)}")

    # Create a Counter from a dictionary
    word_counts = Counter({
        "the": 2,
        "quick": 1,
        "brown": 1,
        "fox": 1,
        "jumps": 1,
        "over": 1,
        "lazy": 1,
        "dog": 1,
    })
    print(f"Word counts: {word_counts}")

    # Create a Counter from keyword arguments
    fruit_counts = Counter(apples=3, oranges=5, bananas=2)
    print(f"Fruit counts: {fruit_counts}")

    # Update with another counter
    more_fruits = Counter(apples=2, pears=4, bananas=1)
    fruit_counts.update(more_fruits)
    print(f"Updated fruit counts: {fruit_counts}")

    # Arithmetic operations with counters
    basket1 = Counter(apples=3, oranges=1, bananas=2)
    basket2 = Counter(apples=1, oranges=2, pears=3)

    # Addition - combines counts
    combined = basket1 + basket2
    print(f"Combined baskets (basket1 + basket2): {combined}")

    # Subtraction - removes counts, drops negatives
    remainder = basket1 - basket2
    print(f"Remainder (basket1 - basket2): {remainder}")

    # Practical example: finding word frequencies in text
    text = """
    Python is an interpreted, high-level, general-purpose programming language.
    Created by Guido van Rossum and first released in 1991, Python's design
    philosophy emphasizes code readability with its notable use of significant
    whitespace. Its language constructs and object-oriented approach aim to
    help programmers write clear, logical code for small and large-scale projects.
    """

    # Normalize and split text
    words = text.lower().replace(".", "").replace(",", "").split()
    word_freq = Counter(words)

    # Top 5 most common words
    print("\nWord frequency analysis:")
    for word, count in word_freq.most_common(5):
        print(f"  {word}: {count}")

    # Elements method - returns each element as many times as its count
    basket = Counter(apples=2, oranges=3)
    print(f"\nElements in basket: {list(basket.elements())}")


def main() -> None:
    """Main function to run all demos."""
    print("PYTHON COLLECTIONS MODULE DEMO")

    deque_demo()
    namedtuple_demo()
    counter_demo()


if __name__ == "__main__":
    main()
