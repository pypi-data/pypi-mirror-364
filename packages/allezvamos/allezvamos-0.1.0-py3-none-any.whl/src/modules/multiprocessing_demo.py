import multiprocessing
import time


def pool_worker_task(name: str) -> str:
    """Task for pool workers that returns a result."""
    print(f"Pool worker {name} started")
    time.sleep(2)
    print(f"Pool worker {name} finished")
    return f"Result from {name}"


def main() -> None:
    """Main entry point showcasing process-based parallelism."""
    start_time = time.time()

    print("Starting multiprocessing demo")

    # Create processes (note args is now a single-tuple)
    processes = [
        multiprocessing.Process(target=pool_worker_task, args=(f"Worker-{i}",))
        for i in range(1, 4)
    ]

    # Start processes
    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

    print(f"All processes finished; total time: {time.time() - start_time:.2f} seconds")

    # Demonstration of using a Pool
    print("Starting pool demo")
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.map(pool_worker_task, [f"Pool-Worker-{i}" for i in range(1, 4)])
        print("Pool results:", results)

    print(f"Total time including pool: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
