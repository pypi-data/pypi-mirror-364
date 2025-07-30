r"""Demonstration of Python's heapq module usage.

heapq provides an implementation of the heap queue algorithm, also known as
the priority queue algorithm. The following are important operations that can be
performed using this module:

1. Create a heap:
   - Transform a list into a heap in-place, in linear time.

2. Insert into a heap:
   - `heappush()` enables insertion while maintaining the heap property.

3. Pop from a heap:
   - `heappop()` removes and returns the smallest element.

4. Peek at the smallest element:
   - Access the smallest element without popping it.

5. Merge multiple sorted inputs into a single sorted iterator.

We also demonstrate the running median problem to emphasize practical applications.

What they do
        •       bisect
        •       Performs binary search on a sorted list to find insertion/search indices
        in O(log n) time.
        •       Provides bisect_left/bisect_right (search) and insort_left/insort_right
        (search + insert).
        •       Insertion with insort is O(n) overall, because elements to the right
        must be shifted.
        •       Great when you have a mostly-static sorted list and only occasional
        insertions or lookups.
        •       heapq
        •       Implements a binary heap (min-heap) on top of a plain list.
        •       Provides heappush/heappop to add/remove the smallest element in O(log n)
        time.
        •       The list isnt fully sorted—only the smallest element
        is guaranteed at heap[0]
        •       Ideal for priority-queue patterns or when you repeatedly need the
        next-smallest (or largest, via negation) item.
"""

import heapq
import random


def heap_operations_demo() -> None:
    """Demonstrate basic heap operations using heapq."""
    print("Heap Operations Demo:")
    heap = []
    data = [8, 1, 3, 5, 2]

    # Insert elements into the heap
    for item in data:
        heapq.heappush(heap, item)
        print(f"  Inserted {item}, heap is now: {heap}")

    # Pop elements from the heap
    while heap:
        smallest = heapq.heappop(heap)
        print(f"  Popped {smallest}, heap is now: {heap}")
    print()


def merge_sorted_lists_demo() -> None:
    """Demonstrate merging sorted input using heapq."""
    sorted_list1 = [1, 3, 5]
    sorted_list2 = [2, 4, 6]

    print("Merging two sorted lists:")
    merged = heapq.merge(sorted_list1, sorted_list2)
    print(f"  Merged result: {list(merged)}")
    print()


def running_median_demo(stream_size: int = 10) -> None:
    """Demonstrate calculating the running median with two heaps."""
    print("Running Median Demo:")
    min_heap, max_heap = [], []

    def add_number(num):
        if len(max_heap) == 0 or num < -max_heap[0]:
            heapq.heappush(max_heap, -num)
        else:
            heapq.heappush(min_heap, num)

        # Balance heaps
        if len(max_heap) > len(min_heap) + 1:
            heapq.heappush(min_heap, -heapq.heappop(max_heap))
        elif len(min_heap) > len(max_heap):
            heapq.heappush(max_heap, -heapq.heappop(min_heap))

    def get_median():
        if len(max_heap) > len(min_heap):
            return -max_heap[0]
        else:
            return (-max_heap[0] + min_heap[0]) / 2

    # Simulate stream of numbers
    for _ in range(stream_size):
        num = random.randint(1, 100)
        add_number(num)
        median = get_median()
        print(f"  Number: {num}, Running Median: {median}")

    print()


def main() -> None:
    """Main entry point showcasing heapq module capabilities."""
    print("HEAPQ MODULE DEMONSTRATION")
    print("==========================\n")

    # Demonstrate basic heap operations
    heap_operations_demo()

    # Demonstrate merging sorted lists
    merge_sorted_lists_demo()

    # Demonstrate calculating the running median
    running_median_demo()

    print("Heapq module demonstration completed")


if __name__ == "__main__":
    main()
