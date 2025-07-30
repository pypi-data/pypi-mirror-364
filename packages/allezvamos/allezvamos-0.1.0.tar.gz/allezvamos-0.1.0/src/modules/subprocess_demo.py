"""subprocess_demo.py.

Demonstration of Python's subprocess module usage for executing shell commands.
"""

import subprocess


def execute_command(command: str) -> None:
    """Executes a shell command and prints the output."""
    print(f"Executing command: {command}")
    try:
        # Run the command
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        print("Command output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")


def main() -> None:
    """Main entry point showcasing subprocess command execution."""
    print("Starting subprocess demo")

    # Example command: List files and directories
    command = "ls -l"
    execute_command(command)

    # Example command: Display current working directory
    command = "pwd"
    execute_command(command)

    # Example command: Echo a message
    command = "echo 'Hello, subprocess!'"
    execute_command(command)


if __name__ == "__main__":
    main()
