from routing import build_graph, shortest_path


MEDICAL_RESOURCES = {
    "First Aid",
    "EMT / Paramedic",
    "Nurse",
    "Doctor",
    "Mental Health Support",
}


def value_from(row, key, default=None):
    if row is None:
        return default

    if hasattr(row, "keys") and key in row.keys():
        return row[key]

    if isinstance(row, dict):
        return row.get(key, default)

    return default


def resource_matches(need_type, resource_type):
    if need_type == resource_type:
        return True

    if need_type == "Medical" and resource_type in MEDICAL_RESOURCES:
        return True

    if need_type == "Shelter" and resource_type == "Shelter Space":
        return True

    if need_type == "Power" and resource_type == "Power Charging":
        return True

    return False


def route_between(graph, start_location, end_location):
    if start_location == end_location:
        return {"time": 0, "path": [start_location]}

    if start_location not in graph or end_location not in graph:
        return None

    return shortest_path(graph, start_location, end_location)


def find_nearest_helper_for_request(request_row, helpers, edges):
    request_location = value_from(request_row, "zone", "")
    need_type = value_from(request_row, "need_type", "")
    graph = build_graph(edges)
    best_match = None

    for helper in helpers:
        if value_from(helper, "status") != "Available":
            continue

        resource_type = value_from(helper, "resource_type")
        if not resource_matches(need_type, resource_type):
            continue

        helper_location = value_from(helper, "zone", "")
        route = route_between(graph, helper_location, request_location)

        if route is None:
            continue

        candidate = {
            "helper": helper,
            "travel_time": route["time"],
            "path": route["path"],
        }

        if best_match is None or candidate["travel_time"] < best_match["travel_time"]:
            best_match = candidate

    return best_match
