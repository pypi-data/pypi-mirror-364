"""pickle_demo.py.

Demonstration of Python's pickle module usage at a high level.
"""

import pickle


def serialize_object(obj, filename: str) -> None:
    """Serializes an object to a file using pickle."""
    with open(filename, "wb") as file:
        pickle.dump(obj, file)
    print(f"Serialized object to {filename}")


def deserialize_object(filename: str):
    """Deserializes an object from a file using pickle."""
    with open(filename, "rb") as file:
        obj = pickle.load(file)
    print(f"Deserialized object from {filename}")
    return obj


def main() -> None:
    """Main entry point showcasing pickle serialization and deserialization."""
    test_object = {
        "key1": "value1",
        "key2": [1, 2, 3],
        "key3": {"nested_key": "nested_value"},
    }
    filename = "example_pickle.pkl"

    # Serialize the object
    serialize_object(test_object, filename)

    # Deserialize the object
    loaded_object = deserialize_object(filename)
    print("Loaded object:", loaded_object)


if __name__ == "__main__":
    main()
