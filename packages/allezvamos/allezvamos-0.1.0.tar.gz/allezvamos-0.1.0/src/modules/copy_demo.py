"""copy_demo.py.

Demonstration of Python's copy module usage at a high level.
"""

import copy
import time


def print_with_timestamp(message: str) -> None:
    """Print a message with a timestamp."""
    print(f"{time.strftime('%X')} - {message}")


def demonstrate_shallow_copy(original_data: dict) -> dict:
    """Demonstrate shallow copy behavior and return the copied object."""
    print_with_timestamp("Performing shallow copy with copy.copy()")

    # Create a shallow copy
    shallow_copied = copy.copy(original_data)

    print_with_timestamp(f"Original: {original_data}")
    print_with_timestamp(f"Shallow copy: {shallow_copied}")

    # Show that the objects are different
    print_with_timestamp(f"Are they the same object? {original_data is shallow_copied}")

    # Modify top-level element in the copy
    shallow_copied["name"] = "Modified Name"
    print_with_timestamp("After modifying top-level element 'name' in the copy:")
    print_with_timestamp(f"Original: {original_data}")
    print_with_timestamp(f"Shallow copy: {shallow_copied}")

    # Modify nested element in the copy
    shallow_copied["details"]["age"] = 35
    print_with_timestamp("After modifying nested element 'age' in the copy:")
    print_with_timestamp(f"Original: {original_data}")
    print_with_timestamp(f"Shallow copy: {shallow_copied}")
    print_with_timestamp("Notice that the nested element was modified in both!")
    print()

    return shallow_copied


def demonstrate_deep_copy(original_data: dict) -> dict:
    """Demonstrate deep copy behavior and return the copied object."""
    print_with_timestamp("Performing deep copy with copy.deepcopy()")

    # Create a deep copy
    deep_copied = copy.deepcopy(original_data)

    print_with_timestamp(f"Original: {original_data}")
    print_with_timestamp(f"Deep copy: {deep_copied}")

    # Show that the objects are different
    print_with_timestamp(f"Are they the same object? {original_data is deep_copied}")

    # Modify top-level element in the copy
    deep_copied["name"] = "Deep Modified Name"
    print_with_timestamp("After modifying top-level element 'name' in the copy:")
    print_with_timestamp(f"Original: {original_data}")
    print_with_timestamp(f"Deep copy: {deep_copied}")

    # Modify nested element in the copy
    deep_copied["details"]["age"] = 40
    print_with_timestamp("After modifying nested element 'age' in the copy:")
    print_with_timestamp(f"Original: {original_data}")
    print_with_timestamp(f"Deep copy: {deep_copied}")
    print_with_timestamp(
        "Notice that the nested element was NOT modified in the original!"
    )
    print()

    return deep_copied


def demonstrate_custom_object_copying() -> None:
    """Demonstrate copying of custom objects with __copy__ and __deepcopy__ methods."""

    class CustomObject:
        def __init__(self, name: str, data: list) -> None:
            self.name = name
            self.data = data

        def __repr__(self) -> str:
            return f"CustomObject(name='{self.name}', data={self.data})"

        def __copy__(self) -> "CustomObject":
            print_with_timestamp("__copy__ method called")
            return CustomObject(self.name, self.data.copy())

        def __deepcopy__(self, memo: dict) -> "CustomObject":
            print_with_timestamp("__deepcopy__ method called")
            return CustomObject(self.name, copy.deepcopy(self.data, memo))

    print_with_timestamp("Demonstrating custom object copying")
    original = CustomObject("Original", [1, 2, [3, 4]])

    # Shallow copy
    print_with_timestamp("Shallow copying custom object")
    shallow = copy.copy(original)
    print_with_timestamp(f"Original: {original}")
    print_with_timestamp(f"Shallow copy: {shallow}")

    # Deep copy
    print_with_timestamp("Deep copying custom object")
    deep = copy.deepcopy(original)
    print_with_timestamp(f"Original: {original}")
    print_with_timestamp(f"Deep copy: {deep}")

    # Modify nested data
    shallow.data[2].append(5)
    print_with_timestamp("After modifying nested list in shallow copy:")
    print_with_timestamp(f"Original: {original}")
    print_with_timestamp(f"Shallow copy: {shallow}")
    print_with_timestamp(f"Deep copy: {deep}")
    print()


def main() -> None:
    """Main entry point showcasing different copy operations."""
    print_with_timestamp("Starting copy module demonstration")

    # Create a nested data structure
    original_data = {
        "name": "Original Name",
        "details": {"age": 30, "location": "Example City"},
        "scores": [95, 87, 92],
    }

    # Demonstrate the difference between shallow and deep copies
    shallow_copied = demonstrate_shallow_copy(original_data)
    deep_copied = demonstrate_deep_copy(original_data)

    # Show effect of modifying the original on the copies
    print_with_timestamp("Modifying the original after copies were made")
    original_data["scores"].append(88)
    print_with_timestamp(f"Original after appending to scores: {original_data}")
    print_with_timestamp(f"Shallow copy scores: {shallow_copied['scores']}")
    print_with_timestamp(f"Deep copy scores: {deep_copied['scores']}")
    print_with_timestamp(
        "Notice that the shallow copy's scores changed, but the deep copy's didn't!"
    )
    print()

    # Demonstrate copying custom objects
    demonstrate_custom_object_copying()

    print_with_timestamp("Copy module demonstration completed")


if __name__ == "__main__":
    main()
