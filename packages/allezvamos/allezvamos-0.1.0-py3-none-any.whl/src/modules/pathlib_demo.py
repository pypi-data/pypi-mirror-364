"""pathlib_demo.py.

Demonstration of Python's pathlib module usage at a high level.
"""

from pathlib import Path


def demo_pathlib_operations(directory: str) -> None:
    """Demonstrates basic file and directory operations using pathlib."""
    # Create a new directory
    dir_path = Path(directory)
    dir_path.mkdir(exist_ok=True)
    print(f"Created directory: {dir_path}")

    # Create a new file and write text to it
    file_path = dir_path / "example_file.txt"
    file_path.write_text("Hello, pathlib!")
    print(f"Created and wrote to file: {file_path}")

    # Read the content from the file
    content = file_path.read_text()
    print(f"Read from file: {content}")

    # Check if the file exists
    if file_path.exists():
        print(f"File exists: {file_path}")

    # Print all files in directory
    print("Files in directory:")
    for file in dir_path.iterdir():
        print(file.name)

    # Clean up: remove the file and directory
    file_path.unlink()
    dir_path.rmdir()
    print(f"Cleaned up directory and files in: {dir_path}")


def main() -> None:
    """Main entry point showcasing pathlib operations."""
    print("Starting pathlib demo")
    demo_pathlib_operations("example_directory")


if __name__ == "__main__":
    main()
