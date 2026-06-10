from collections import deque


def build_graph(edges):
    graph = {}

    for edge in edges:
        start = edge["from"]
        end = edge["to"]
        travel_time = edge["time"]

        if start not in graph:
            graph[start] = []
        if end not in graph:
            graph[end] = []

        graph[start].append((end, travel_time))
        graph[end].append((start, travel_time))

    return graph


def dijkstra(graph, start):
    distances = {}
    previous_nodes = {}

    for location in graph:
        distances[location] = float("inf")
        previous_nodes[location] = None

    distances[start] = 0
    queue = deque([(0, start)])

    while queue:
        current_distance, current_location = queue.popleft()

        if current_distance > distances[current_location]:
            continue

        for neighbor, travel_time in graph[current_location]:
            new_distance = current_distance + travel_time

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_location
                queue.append((new_distance, neighbor))

    return distances, previous_nodes


def shortest_path(graph, start, end):

    distances, previous_nodes = dijkstra(graph, start)

    if distances[end] == float("inf"):
        return None

    path = []
    current_location = end

    while current_location is not None:
        path.append(current_location)
        current_location = previous_nodes[current_location]

    path.reverse()  # start to end

    return {"time": distances[end], "path": path}
