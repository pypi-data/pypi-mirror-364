"""struct_demo.py.

Demonstration of Python's struct module usage at a high level.
"""

import struct


def pack_data(fmt: str, *data) -> bytes:
    """Packs data into a binary format according to the specified format string."""
    packed_data = struct.pack(fmt, *data)
    print(f"Packed data: {packed_data}")
    return packed_data


def unpack_data(fmt: str, packed_data: bytes) -> tuple:
    """Unpacks data from a binary format into a tuple according to the specified format
    string."""
    unpacked_data = struct.unpack(fmt, packed_data)
    print(f"Unpacked data: {unpacked_data}")
    return unpacked_data


def main() -> None:
    """Main entry point showcasing struct packing and unpacking."""
    # Example: Pack and unpack a struct containing an int, a float, and a bytes-string
    fmt = "if4s"  # Specifies the format: int, float, and a 4-byte string
    data_to_pack = (1, 3.14, b"abcd")

    # Pack the data
    packed_data = pack_data(fmt, *data_to_pack)

    # Unpack the data
    _ = unpack_data(fmt, packed_data)


if __name__ == "__main__":
    main()
