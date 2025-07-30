"""threading_demo.py.

Demonstration of Python's threading module usage for executing tasks concurrently.
"""

import threading
import time


def thread_task(name: str, delay: int) -> None:
    """Function to be executed by each thread, prints its name and sleeps for a given
    delay."""
    print(f"Thread {name} is starting")
    time.sleep(delay)
    print(f"Thread {name} is finishing")


def main() -> None:
    """Main entry point showcasing threading for concurrent task execution."""
    print("Starting threading demo")

    # Create threads
    threads = [
        threading.Thread(target=thread_task, args=(f"Thread-{i}", i))
        for i in range(1, 4)
    ]

    # Start threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("All threads have finished")


if __name__ == "__main__":
    main()
