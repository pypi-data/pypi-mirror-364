# FuncBox

FuncBox is a streamlined Python utility library designed to provide essential utilities.

## Installation

To install FuncBox, use pip:

```bash
pip install -U funcbox
```

## Usage

Import FuncBox into your Python project to access its functions:

```python
from funcbox import *
```

## Available Functions

### `is_prime(n: int) -> bool`
Efficiently check if a number is prime. Only checking potential divisors of form 6k±1 up to sqrt(n)

*   **Parameters**:
    *   `n`: The number to check for primality
*   **Returns**:
    *   `bool`: True if the number is prime, False otherwise
*   **Examples**:
    ```python
    print(is_prime(7))  # Output: True
    print(is_prime(10))  # Output: False
    ```

### `fibonacci(n: int, type="int") -> Union[int, List[int]]`
Calculate Fibonacci numbers efficiently.

*   **Parameters**:
    *   `n`: The index of Fibonacci number to calculate (0-indexed) or count of numbers for list
    *   `type`: Output format - 'int' for single value or 'list' for sequence. Defaults to "int".
*   **Returns**:
    *   `Union[int, List[int]]`: Either the nth Fibonacci number or a list of n Fibonacci numbers
*   **Raises**:
    *   `ValueError`: If n is negative or type is not 'int' or 'list'
*   **Examples**:
    ```python
    print(fibonacci(0))  # Output: 0
    print(fibonacci(5))  # Output: 5
    print(fibonacci(5, "list"))  # Output: [0, 1, 1, 2, 3]
    ```

### `get_factors(num: int) -> List[int]`
Get all factors of a number, excluding the number itself.

*   **Parameters**:
    *   `num`: The number to find factors for.
*   **Returns**:
    *   `List[int]`: A sorted list of all factors of the number (excluding the number itself).
*   **Examples**:
    ```python
    print(get_factors(12))  # Output: [1, 2, 3, 4, 6]
    print(get_factors(7))   # Output: [1]
    ```

### `dijkstra(graph: dict, start_node: Any, end_node: Any = None) -> dict`
Compute Dijkstra's shortest path algorithm to find the shortest paths from a start node to all other nodes in a graph,
or to a specific end node if specified.

*   **Parameters**:
    *   `graph`: A graph represented as an adjacency list, where keys are nodes and values are dictionaries mapping neighbors to edge weights.
    *   `start_node`: The node to start the pathfinding from.
    *   `end_node`: (Optional) If specified, the algorithm will terminate early once the shortest path to this node is found. Defaults to None.
*   **Returns**:
    *   `dict`: A dictionary containing two dictionaries:
        *   `'distances'`: Shortest distances from the start node to each node.
        *   `'paths'`: Shortest paths from the start node to each node.
        Nodes not reachable from the start node will have a distance of infinity and path as None.
*   **Examples**:
    ```python
    graph = {
        'A': {'B': 4, 'C': 2},
        'B': {'D': 5, 'E': 1},
        'C': {'B': 1, 'E': 3},
        'D': {'F': 2},
        'E': {'D': 1, 'F': 4},
        'F': {}
    }
    result = dijkstra(graph, 'A')
    print(result['distances'])  # Output distances from A to all nodes
    print(result['paths'])      # Output paths from A to all nodes
    
    # Using end_node parameter
    result = dijkstra(graph, 'A', 'F')
    print(result['distances'])  # Output distances for nodes processed
    print(result['paths'])      # Output paths for nodes processed
    ```

### `primes(start: int = 2, limit: int = None) -> List[int]`
Efficiently generate all prime numbers between start and limit using the Sieve of Eratosthenes algorithm.

*   **Parameters**:
    *   `start`: The lower bound for finding prime numbers (inclusive). Defaults to 2.
    *   `limit`: The upper bound for finding prime numbers (inclusive).
*   **Returns**:
    *   `List[int]`: A list of all prime numbers from start to the given limit.
*   **Raises**:
    *   `ValueError`: If `limit` is less than 2 or `start` is less than 2.
*   **Examples**:
    ```python
    print(primes(limit=10))  # Output: [2, 3, 5, 7]
    print(primes(start=10, limit=20))  # Output: [11, 13, 17, 19]
    ```

## Disclaimer

FuncBox provides utility functions for general use. The developer is not responsible for any issues caused by improper use or abuse of the library.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request with your improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
