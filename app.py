from flask import Flask, render_template, request, redirect, url_for, session
from scoring import calculate_triage_score
from database import (
    init_db,
    add_request,
    add_volunteer,
    get_all_volunteers,
    find_matches,
    assign_match,
    resolve_request,
    save_disaster_status,
    get_disaster_status,
    counter,
    get_requests_by_filter,
    get_assignments_by_request,
    add_note,
    get_notes_by_request,
    add_location,
    add_edge,
    get_locations,
    get_routing_edges,
    delete_location,
    delete_edge,
    update_location_position,
)

import math

app = Flask(__name__)
init_db()

COORDINATOR_ACCESS_CODE = "COMMUNITY123"
PROFESSIONAL_ACCESS_CODE = "RESPONDER123"
app.secret_key = "676767"


def build_graph(locations, edges):
    nodes = []
    num_locations = len(locations)

    if num_locations == 0:
        return nodes, []

    center_x = 300
    center_y = 300
    radius = 200

    for i, location in enumerate(locations):
        angle = 2 * math.pi * i / num_locations
        location_keys = location.keys()
        location_id = location["id"] if "id" in location_keys else location["name"]
        stored_x = location["x_position"] if "x_position" in location_keys else None
        stored_y = location["y_position"] if "y_position" in location_keys else None

        if stored_x is not None and stored_y is not None:
            x_position = stored_x
            y_position = stored_y
        else:
            x_position = center_x + radius * math.cos(angle)
            y_position = center_y + radius * math.sin(angle)

        nodes.append(
            {
                "id": location_id,
                "name": location["name"],
                "x": x_position,
                "y": y_position,
            }
        )

    node_by_id = {}
    node_by_name = {}
    for node in nodes:
        node_by_id[node["id"]] = node
        node_by_name[node["name"]] = node

    graph_edges = []
    for edge in edges:
        edge_keys = edge.keys()

        if "from_location_id" in edge_keys and "to_location_id" in edge_keys:
            start_location = node_by_id.get(edge["from_location_id"])
            end_location = node_by_id.get(edge["to_location_id"])
        else:
            start_location = node_by_name.get(edge["from"])
            end_location = node_by_name.get(edge["to"])

        if start_location and end_location:
            edge_id = (
                edge["id"]
                if "id" in edge_keys
                else f'{start_location["id"]}-{end_location["id"]}'
            )

            graph_edges.append(
                {
                    "id": edge_id,
                    "from_id": start_location["id"],
                    "to_id": end_location["id"],
                    "from": edge["from"],
                    "to": edge["to"],
                    "time": edge["time"],
                    "from_x": start_location["x"],
                    "from_y": start_location["y"],
                    "to_x": end_location["x"],
                    "to_y": end_location["y"],
                }
            )

    return nodes, graph_edges


def is_community():
    return session.get("user_type") == "coordinator"


def is_professional():
    return session.get("professional_access") == "approved"


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":

        access_code = request.form.get("access_code")

        if access_code == COORDINATOR_ACCESS_CODE:
            session["user_type"] = "coordinator"
            return redirect(url_for("community"))

        error = "Invalid access code."

    return render_template("login.html", error=error)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/resident")
def resident():
    return render_template("resident.html")


@app.route("/professional-login", methods=["GET", "POST"])
def professional_login():
    error = None

    if request.method == "POST":
        access_code = request.form.get("access_code")

        if access_code == PROFESSIONAL_ACCESS_CODE:
            session["professional_access"] = "approved"
            return redirect(url_for("professional"))

        error = "Invalid professional responder code."

    return render_template("professional_login.html", error=error)


@app.route("/request", methods=["POST", "GET"])
def request_page():
    submitted_request = None
    locations = get_locations()

    if request.method == "POST":
        resident_name = request.form.get("resident_name")
        zone = request.form.get("zone", "").strip()
        need_type = request.form.get("need_type")
        phone_number = request.form.get("phone_number")
        detail_location = request.form.get("detail_location", "").strip()
        red_flags = request.form.getlist("red_flags")
        injury_level = request.form.get("injury_level")
        mobility_status = request.form.get("mobility_status")
        vulnerable_person = request.form.get("vulnerable_person")
        evacuation_need = request.form.get("evacuation_need")
        safe_shelter = request.form.get("safe_shelter")

        urgency, priority_score, triage_reasons = calculate_triage_score(
            red_flags,
            injury_level,
            mobility_status,
            vulnerable_person,
            evacuation_need,
            safe_shelter,
        )

        submitted_request = {
            "resident_name": resident_name,
            "phone_number": phone_number,
            "zone": zone,
            "need_type": need_type,
            "injury_level": injury_level,
            "mobility_status": mobility_status,
            "vulnerable_person": vulnerable_person,
            "evacuation_need": evacuation_need,
            "safe_shelter": safe_shelter,
            "red_flags": red_flags,
            "urgency": urgency,
            "priority_score": priority_score,
            "triage_reasons": triage_reasons,
            "detail_location": detail_location,
        }

        add_request(submitted_request)

    return render_template(
        "request.html", submitted_request=submitted_request, locations=locations
    )


@app.route("/community", methods=["GET", "POST"])
def community():
    if not is_community():
        return redirect(url_for("login"))

    selected_filter = request.args.get("filter", "All")

    if request.method == "POST":
        disaster_type = request.form.get("disaster_type")
        stage = request.form.get("stage")

        save_disaster_status(disaster_type, stage)
        return redirect(url_for("community", filter=selected_filter))

    current_disaster = get_disaster_status()
    requests = get_requests_by_filter(selected_filter)
    volunteers = get_all_volunteers()
    locations = get_locations()
    routing_edges = get_routing_edges()
    graph_nodes, graph_edges = build_graph(locations, routing_edges)
    open_requests = get_requests_by_filter("Open")
    available_helpers = []
    for helper in volunteers:
        if helper["status"] == "Available":
            available_helpers.append(helper)
    matches = find_matches()
    assignments_by_request = get_assignments_by_request()
    notes_by_request = get_notes_by_request()
    dashboard_stats = counter()
    dashboard_stats["suggested_matches"] = len(matches)

    return render_template(
        "community.html",
        current_disaster=current_disaster,
        selected_filter=selected_filter,
        requests=requests,
        volunteers=volunteers,
        locations=locations,
        routing_edges=routing_edges,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        open_requests=open_requests,
        available_helpers=available_helpers,
        matches=matches,
        assignments_by_request=assignments_by_request,
        notes_by_request=notes_by_request,
        dashboard_stats=dashboard_stats,
    )


@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    submitted_volunteer = None
    locations = get_locations()

    if request.method == "POST":
        volunteer_name = request.form.get("volunteer_name")
        phone_number = request.form.get("phone_number")
        zone = request.form.get("zone", "").strip()
        detail_location = request.form.get("detail_location", "").strip()
        resource_type = request.form.get("resource_type")
        availability = request.form.get("availability")

        submitted_volunteer = {
            "volunteer_name": volunteer_name,
            "phone_number": phone_number,
            "helper_type": "Community Volunteer",
            "zone": zone,
            "detail_location": detail_location,
            "resource_type": resource_type,
            "availability": availability,
        }

        add_volunteer(submitted_volunteer)

    return render_template(
        "volunteer.html",
        submitted_volunteer=submitted_volunteer,
        locations=locations,
    )


@app.route("/add-location", methods=["POST"])
def add_location_route():
    if not is_community():
        return redirect(url_for("login"))

    location_name = request.form.get("location_name", "").strip()
    selected_filter = request.form.get("current_filter", "All")

    if location_name:
        add_location(location_name)

    return redirect(url_for("community", filter=selected_filter))


@app.route("/add-edge", methods=["POST"])
def add_edge_route():
    if not is_community():
        return redirect(url_for("login"))

    from_location_id = request.form.get("from_location_id")
    to_location_id = request.form.get("to_location_id")
    travel_time = request.form.get("time", type=float)
    selected_filter = request.form.get("current_filter", "All")

    if (
        from_location_id
        and to_location_id
        and travel_time
        and from_location_id != to_location_id
    ):
        add_edge(from_location_id, to_location_id, travel_time)

    return redirect(url_for("community", filter=selected_filter))


@app.route("/delete-location", methods=["POST"])
def delete_location_route():
    if not is_community():
        return redirect(url_for("login"))

    location_id = request.form.get("location_id")
    selected_filter = request.form.get("current_filter", "All")

    if location_id:
        delete_location(location_id)

    return redirect(url_for("community", filter=selected_filter))


@app.route("/delete-edge", methods=["POST"])
def delete_edge_route():
    if not is_community():
        return redirect(url_for("login"))

    edge_id = request.form.get("edge_id")
    selected_filter = request.form.get("current_filter", "All")

    if edge_id:
        delete_edge(edge_id)

    return redirect(url_for("community", filter=selected_filter))


@app.route("/move-location", methods=["POST"])
def move_location_route():
    if not is_community():
        return {"success": False}, 403

    data = request.get_json(silent=True) or {}
    location_id = data.get("location_id")
    x_position = data.get("x")
    y_position = data.get("y")

    if location_id is None or x_position is None or y_position is None:
        return {"success": False}, 400

    update_location_position(location_id, x_position, y_position)

    return {"success": True}


@app.route("/professional", methods=["GET", "POST"])
def professional():
    if not is_professional():
        return redirect(url_for("professional_login"))

    submitted_professional = None
    locations = get_locations()

    if request.method == "POST":
        volunteer_name = request.form.get("volunteer_name")
        phone_number = request.form.get("phone_number")
        zone = request.form.get("zone", "").strip()
        detail_location = request.form.get("detail_location", "").strip()
        resource_type = request.form.get("resource_type")
        availability = request.form.get("availability")

        submitted_professional = {
            "volunteer_name": volunteer_name,
            "phone_number": phone_number,
            "helper_type": "Professional Responder",
            "zone": zone,
            "detail_location": detail_location,
            "resource_type": resource_type,
            "availability": availability,
        }

        add_volunteer(submitted_professional)

    return render_template(
        "professional.html",
        submitted_professional=submitted_professional,
        locations=locations,
    )


@app.route("/assign", methods=["POST"])
def assign():
    if not is_community():
        return redirect(url_for("login"))

    request_id = request.form.get("request_id")
    volunteer_id = request.form.get("volunteer_id")
    selected_filter = request.form.get("current_filter", "All")

    assign_match(request_id, volunteer_id)

    return redirect(url_for("community", filter=selected_filter))


@app.route("/resolve", methods=["POST"])
def resolve():
    if not is_community():
        return redirect(url_for("login"))

    request_id = request.form.get("request_id")
    selected_filter = request.form.get("current_filter", "All")

    resolve_request(request_id)

    return redirect(url_for("community", filter=selected_filter))


@app.route("/note", methods=["POST"])
def note():
    if not is_community():
        return redirect(url_for("login"))

    request_id = request.form.get("request_id")
    note_text = request.form.get("note_text", "")
    selected_filter = request.form.get("current_filter", "All")

    add_note(request_id, note_text)

    return redirect(url_for("community", filter=selected_filter))


if __name__ == "__main__":
    app.run(debug=True)
