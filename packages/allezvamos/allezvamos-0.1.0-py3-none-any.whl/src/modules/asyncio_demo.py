"""asyncio_demo.py.

Demonstration of Python's asyncio module usage at a high level.
"""

import asyncio
import time


async def say(message: str, delay: float) -> None:
    """Coroutine that sleeps for a given delay and prints a message with a timestamp."""
    await asyncio.sleep(delay)
    print(f"{time.strftime('%X')} - {message}")


async def main() -> None:
    """Main entry point showcasing sequential and concurrent task execution."""
    print(f"{time.strftime('%X')} - Starting main")

    # Sequential execution: tasks run one after another
    print(f"{time.strftime('%X')} - Sequential execution")
    start = time.time()
    await say("Task 1 sequential", 1)
    await say("Task 2 sequential", 1)
    print(f"Sequential execution took {time.time() - start:.2f} seconds\n")

    # Concurrent execution: tasks run concurrently using create_task
    print(f"{time.strftime('%X')} - Concurrent execution with create_task")
    start = time.time()
    task1 = asyncio.create_task(say("Task 1 concurrent", 2))
    task2 = asyncio.create_task(say("Task 2 concurrent", 1))
    await task1
    await task2
    print(f"Concurrent execution took {time.time() - start:.2f} seconds\n")

    # Using asyncio.gather to schedule multiple coroutines
    print(f"{time.strftime('%X')} - Execution with asyncio.gather")
    start = time.time()
    await asyncio.gather(
        say("Gathered task 1", 1),
        say("Gathered task 2", 2),
        say("Gathered task 3", 1),
    )
    print(f"Gather execution took {time.time() - start:.2f} seconds\n")

    print(f"{time.strftime('%X')} - Main completed")


if __name__ == "__main__":
    asyncio.run(main())
