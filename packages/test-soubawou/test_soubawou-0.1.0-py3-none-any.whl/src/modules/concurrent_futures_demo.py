"""concurrent_futures_demo.py.

Demonstration of Python's concurrent.futures module for threading and processing.
"""

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def task(name: str, delay: int) -> str:
    """Simulates a task by sleeping for a given delay and returns a result message."""
    print(f"Task {name} is starting")
    time.sleep(delay)
    result = f"Task {name} completed"
    print(result)
    return result


def threading_demo() -> None:
    """Showcases concurrent execution using a thread pool."""
    print("Starting threading demo")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(task, f"Thread-{i}", i) for i in range(1, 4)]
        for future in futures:
            print(future.result())


def processing_demo() -> None:
    """Showcases concurrent execution using a process pool."""
    print("Starting processing demo")
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(task, f"Process-{i}", i) for i in range(1, 4)]
        for future in futures:
            print(future.result())


def main() -> None:
    """Main entry point for concurrent.futures demos."""
    threading_demo()
    processing_demo()


if __name__ == "__main__":
    main()
