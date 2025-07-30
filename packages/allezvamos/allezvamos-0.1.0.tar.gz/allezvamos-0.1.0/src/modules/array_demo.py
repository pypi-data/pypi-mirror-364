"""array_demo.py.

Demonstration of Python's built-in array module usage.
"""

import array


def main():
    # Create an array of ints
    int_array = array.array("i", [1, 2, 3, 4, 5])
    print("Initial integer array:", int_array)

    # Append and extend
    int_array.append(6)
    int_array.extend([7, 8, 9])
    print("After append and extend:", int_array)

    # Insert element at position
    int_array.insert(0, 0)
    print("After inserting 0 at position 0:", int_array)

    # Accessing elements
    print("First element:", int_array[0])
    print("Slice [2:5]:", int_array[2:5])

    # Removing elements
    int_array.remove(3)
    print("After removing 3:", int_array)
    popped = int_array.pop()
    print(f"After popping last element ({popped}):", int_array)

    # Searching and length
    index_of_5 = int_array.index(5)
    print("Index of value 5:", index_of_5)
    print("Length of array:", len(int_array))

    # Convert to list
    list_from_array = list(int_array)
    print("Converted to list:", list_from_array)

    # Bytes representation and typecode
    print("Typecode of array:", int_array.typecode)
    print("Bytes representation:", int_array.tobytes())

    # Create array of floats
    float_array = array.array("f", [1.0, 2.0, 3.5])
    print("Float array:", float_array)


if __name__ == "__main__":
    main()
