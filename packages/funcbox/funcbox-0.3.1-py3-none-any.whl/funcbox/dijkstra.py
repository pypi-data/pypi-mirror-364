from typing import Any


def dijkstra(graph: dict, start_node: Any, end_node: Any = None) -> dict:
    """
    Compute Dijkstra's shortest path algorithm to find the shortest paths from a start node to all other nodes in a graph,
    or to a specific end node if specified.

    Args:
        graph (dict): A graph represented as an adjacency list, where keys are nodes and values are dictionaries
                      mapping neighbors to edge weights.
        start_node (Any): The node to start the pathfinding from.
        end_node (Any, optional): If specified, the algorithm will terminate early once the shortest path
                                 to this node is found. Defaults to None.

    Returns:
        dict: A dictionary containing two dictionaries:
              - 'distances': Shortest distances from the start node to each node (or just to end_node if specified).
              - 'paths': Shortest paths from the start node to each node (or just to end_node if specified).
              When end_node is specified, only distances and paths for nodes processed before finding the end_node
              will be included. Nodes not reachable will have a distance of infinity and path as None.

    Raises:
        ValueError: If the graph is not a dictionary, the start_node is not in the graph,
                   or end_node is specified but not in the graph.

    Examples:
        >>> graph = {
        ...     'A': {'B': 4, 'C': 2},
        ...     'B': {'D': 5, 'E': 1},
        ...     'C': {'B': 1, 'E': 3},
        ...     'D': {'F': 2},
        ...     'E': {'D': 1, 'F': 4},
        ...     'F': {}
        ... }
        >>> dijkstra(graph, 'A')
        ({'A': 0, 'B': 3, 'C': 2, 'D': 4, 'E': 4, 'F': 6}, {'A': ['A'], 'B': ['A', 'C', 'B'], 'C': ['A', 'C'], 'D': ['A', 'C', 'B', 'E', 'D'], 'E': ['A', 'C', 'E'], 'F': ['A', 'C', 'B', 'E', 'D', 'F']})        >>> dijkstra(graph, 'A', 'F')
        {'distances': {'A': 0, 'C': 2, 'B': 3, 'E': 4, 'D': 4, 'F': 6}, 'paths': {'A': ['A'], 'C': ['A', 'C'], 'B': ['A', 'C', 'B'], 'E': ['A', 'C', 'E'], 'D': ['A', 'C', 'E', 'D'], 'F': ['A', 'C', 'E', 'D', 'F']}}
    """
    import heapq

    if not isinstance(graph, dict):
        raise ValueError(
            "The graph must be a dictionary represented as an adjacency list."
        )
    if start_node not in graph:
        raise ValueError("The start_node must be a node present in the graph.")
    if end_node is not None and end_node not in graph:
        raise ValueError("The end_node must be a node present in the graph.")

    distances = {node: float("inf") for node in graph}
    distances[start_node] = 0
    paths = {node: None for node in graph}
    paths[start_node] = [start_node]
    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if end_node is not None and current_node == end_node:
            processed_distances = {
                node: dist
                for node, dist in distances.items()
                if dist != float("inf") or node == start_node
            }
            processed_paths = {
                node: path for node, path in paths.items() if path is not None
            }
            return {"distances": processed_distances, "paths": processed_paths}

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                paths[neighbor] = paths[current_node] + [neighbor]
                heapq.heappush(priority_queue, (distance, neighbor))

    return {"distances": distances, "paths": paths}
