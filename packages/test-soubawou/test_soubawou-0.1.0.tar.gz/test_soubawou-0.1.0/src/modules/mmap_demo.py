"""mmap_demo.py.

Demonstration of Python's mmap module usage at a high level.
"""

import mmap
import os


def write_to_memory_map(file_path: str, content: str) -> None:
    """Writes content to a memory-mapped file."""
    # Open file as writable binary and set its size
    with open(file_path, "wb") as f:
        size = len(content)
        f.write(b"\x00" * size)

    # Reopen file as a memory-mapped file
    with open(file_path, "r+b") as f:
        with mmap.mmap(f.fileno(), size, access=mmap.ACCESS_WRITE) as mm:
            mm.write(content.encode())


def read_from_memory_map(file_path: str) -> str:
    """Reads and returns content from a memory-mapped file."""
    with open(file_path, "r+b") as f:
        size = os.path.getsize(file_path)
        with mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ) as mm:
            return mm[:].decode()


def main() -> None:
    """Main entry point showcasing memory-mapped file operations."""
    file_path = "example_mmap.dat"
    content_to_write = "Sample content for mmap demo."

    print("Writing to memory-mapped file")
    write_to_memory_map(file_path, content_to_write)

    print("Reading from memory-mapped file")
    read_content = read_from_memory_map(file_path)
    print(f"Read content: {read_content}")

    # Clean up the example file
    os.remove(file_path)


if __name__ == "__main__":
    main()
