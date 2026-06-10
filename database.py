import sqlite3

DATABASE = "genius.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create requests table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            zone TEXT NOT NULL,
            need_type TEXT NOT NULL,
            injury_level TEXT NOT NULL,
            mobility_status TEXT NOT NULL,
            vulnerable_person TEXT NOT NULL,
            evacuation_need TEXT NOT NULL,
            safe_shelter TEXT NOT NULL,
            red_flags TEXT,
            urgency TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            triage_reasons TEXT,
            status TEXT DEFAULT 'Open',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            detail_location TEXT
        )
    """
    )

    # Create disaster_status table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS disaster_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disaster_type TEXT NOT NULL,
            stage TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            helper_type TEXT NOT NULL DEFAULT 'Community Volunteer',
            zone TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            availability TEXT NOT NULL,
            status TEXT DEFAULT 'Available',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            detail_location TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            volunteer_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS request_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            note_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            x_position REAL,
            y_position REAL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS edges(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_location_id INTEGER NOT NULL,
            to_location_id INTEGER NOT NULL,
            time REAL NOT NULL
        )"""
    )

    ensure_column(cursor, "requests", "detail_location", "TEXT")
    ensure_column(
        cursor,
        "volunteers",
        "helper_type",
        "TEXT NOT NULL DEFAULT 'Community Volunteer'",
    )
    ensure_column(cursor, "volunteers", "detail_location", "TEXT")
    ensure_column(cursor, "locations", "x_position", "REAL")
    ensure_column(cursor, "locations", "y_position", "REAL")

    conn.commit()
    conn.close()


def ensure_column(cursor, table_name, column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [column["name"] for column in cursor.fetchall()]

    if column_name not in existing_columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


def add_request(request_data):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO requests (
            resident_name, phone_number, zone, need_type, injury_level,
            mobility_status, vulnerable_person, evacuation_need, safe_shelter,
            red_flags, urgency, priority_score, triage_reasons, detail_location
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            request_data["resident_name"],
            request_data["phone_number"],
            request_data["zone"],
            request_data["need_type"],
            request_data["injury_level"],
            request_data["mobility_status"],
            request_data["vulnerable_person"],
            request_data["evacuation_need"],
            request_data["safe_shelter"],
            ",".join(request_data.get("red_flags", [])),
            request_data["urgency"],
            request_data["priority_score"],
            ", ".join(request_data.get("triage_reasons", [])),
            request_data.get("detail_location", ""),
        ),
    )

    conn.commit()
    conn.close()


def get_all_requests():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests ORDER BY priority_score DESC, timestamp ASC")
    requests = cursor.fetchall()
    conn.close()
    return requests


def get_requests_by_filter(request_filter):
    conn = get_db()
    cursor = conn.cursor()

    if request_filter in ("Open", "Assigned", "Resolved"):
        cursor.execute(
            """
            SELECT *
            FROM requests
            WHERE status = ?
            ORDER BY priority_score DESC, timestamp ASC
        """,
            (request_filter,),
        )
    elif request_filter in ("Critical", "High", "Medium", "Low"):
        cursor.execute(
            """
            SELECT *
            FROM requests
            WHERE urgency = ?
            ORDER BY priority_score DESC, timestamp ASC
        """,
            (request_filter,),
        )
    else:
        cursor.execute(
            "SELECT * FROM requests ORDER BY priority_score DESC, timestamp ASC"
        )

    requests = cursor.fetchall()
    conn.close()
    return requests


def add_volunteer(volunteer_data):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO volunteers (
            volunteer_name,
            phone_number,
            helper_type,
            zone,
            detail_location,
            resource_type,
            availability
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            volunteer_data["volunteer_name"],
            volunteer_data["phone_number"],
            volunteer_data["helper_type"],
            volunteer_data["zone"],
            volunteer_data.get("detail_location", ""),
            volunteer_data["resource_type"],
            volunteer_data["availability"],
        ),
    )

    conn.commit()
    conn.close()


def get_all_volunteers():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM volunteers
        ORDER BY timestamp DESC, id DESC
    """
    )

    volunteers = cursor.fetchall()

    conn.close()

    return volunteers


def save_disaster_status(disaster_type, stage):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM disaster_status")

    cursor.execute(
        """
        INSERT INTO disaster_status (
            disaster_type,
            stage
        ) VALUES (?, ?)
    """,
        (disaster_type, stage),
    )

    conn.commit()
    conn.close()


def get_disaster_status():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM disaster_status
        ORDER BY timestamp DESC
        LIMIT 1
    """
    )

    disaster_status = cursor.fetchone()

    conn.close()

    if disaster_status:
        return disaster_status

    return {"disaster_type": None, "stage": None}


def find_matches():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            requests.id AS request_id,
            requests.resident_name,
            requests.phone_number AS resident_phone,
            requests.zone,
            requests.detail_location AS request_detail_location,
            requests.need_type,
            requests.urgency,
            requests.priority_score,
            volunteers.id AS volunteer_id,
            volunteers.volunteer_name,
            volunteers.phone_number AS volunteer_phone,
            volunteers.helper_type,
            volunteers.zone AS helper_zone,
            volunteers.detail_location AS helper_detail_location,
            volunteers.resource_type
        FROM requests
        JOIN volunteers
        ON LOWER(TRIM(requests.zone)) = LOWER(TRIM(volunteers.zone))
        AND (
            requests.need_type = volunteers.resource_type
            OR (
                requests.need_type = 'Medical'
                AND volunteers.resource_type IN (
                    'First Aid',
                    'EMT / Paramedic',
                    'Nurse',
                    'Doctor',
                    'Mental Health Support'
                )
            )
            OR (
                requests.need_type = 'Shelter'
                AND volunteers.resource_type = 'Shelter Space'
            )
            OR (
                requests.need_type = 'Power'
                AND volunteers.resource_type = 'Power Charging'
            )
        )
        WHERE requests.status = 'Open'
        AND volunteers.status = 'Available'
        ORDER BY requests.priority_score DESC
    """
    )

    matches = cursor.fetchall()

    conn.close()

    return matches


def assign_match(request_id, volunteer_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE requests
        SET status = 'Assigned'
        WHERE id = ?
    """,
        (request_id,),
    )

    cursor.execute(
        """
        UPDATE volunteers
        SET status = 'Assigned'
        WHERE id = ?
    """,
        (volunteer_id,),
    )

    cursor.execute("DELETE FROM assignments WHERE request_id = ?", (request_id,))

    cursor.execute(
        """
        INSERT INTO assignments (
            request_id,
            volunteer_id
        ) VALUES (?, ?)
    """,
        (request_id, volunteer_id),
    )

    conn.commit()
    conn.close()


def get_assignments_by_request():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            assignments.request_id,
            assignments.assigned_at,
            volunteers.id AS volunteer_id,
            volunteers.volunteer_name,
            volunteers.phone_number,
            volunteers.helper_type,
            volunteers.zone,
            volunteers.detail_location,
            volunteers.resource_type
        FROM assignments
        JOIN volunteers
        ON assignments.volunteer_id = volunteers.id
    """
    )

    assignment_rows = cursor.fetchall()
    conn.close()

    assignments = {}
    for assignment in assignment_rows:
        assignments[assignment["request_id"]] = assignment

    return assignments


def add_note(request_id, note_text):
    note_text = note_text.strip()

    if not note_text:
        return

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO request_notes (
            request_id,
            note_text
        ) VALUES (?, ?)
    """,
        (request_id, note_text),
    )

    conn.commit()
    conn.close()


def get_notes_by_request():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM request_notes
        ORDER BY timestamp DESC
    """
    )

    note_rows = cursor.fetchall()
    conn.close()

    notes = {}
    for note in note_rows:
        request_id = note["request_id"]
        if request_id not in notes:
            notes[request_id] = []
        notes[request_id].append(note)

    return notes


def resolve_request(request_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT volunteer_id
        FROM assignments
        WHERE request_id = ?
        ORDER BY assigned_at DESC
        LIMIT 1
    """,
        (request_id,),
    )

    assignment = cursor.fetchone()

    cursor.execute(
        """
        UPDATE requests
        SET status = 'Resolved'
        WHERE id = ?
    """,
        (request_id,),
    )

    if assignment:
        cursor.execute(
            """
            UPDATE volunteers
            SET status = 'Available'
            WHERE id = ?
        """,
            (assignment["volunteer_id"],),
        )

    conn.commit()
    conn.close()


def counter():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM requests WHERE status = 'Open'")
    open_request_count = cursor.fetchone()["count"]

    cursor.execute(
        "SELECT COUNT(*) AS count FROM volunteers WHERE status = 'Available'"
    )
    available_volunteer_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM requests")
    request_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM volunteers")
    volunteer_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM requests WHERE status = 'Assigned'")
    assigned_request_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM requests WHERE status = 'Resolved'")
    resolved_request_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM requests WHERE urgency = 'Critical'")
    critical_request_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM requests WHERE urgency = 'High'")
    high_request_count = cursor.fetchone()["count"]

    cursor.execute(
        "SELECT COUNT(*) AS count FROM volunteers WHERE helper_type = 'Community Volunteer'"
    )
    community_volunteer_count = cursor.fetchone()["count"]

    cursor.execute(
        "SELECT COUNT(*) AS count FROM volunteers WHERE helper_type = 'Professional Responder'"
    )
    professional_responder_count = cursor.fetchone()["count"]

    conn.close()

    return {
        "request_count": request_count,
        "volunteer_count": volunteer_count,
        "open_request_count": open_request_count,
        "available_volunteer_count": available_volunteer_count,
        "assigned_request_count": assigned_request_count,
        "resolved_request_count": resolved_request_count,
        "total_requests": request_count,
        "total_helpers": volunteer_count,
        "open_requests": open_request_count,
        "available_helpers": available_volunteer_count,
        "assigned_requests": assigned_request_count,
        "resolved_requests": resolved_request_count,
        "critical_requests": critical_request_count,
        "high_requests": high_request_count,
        "community_volunteers": community_volunteer_count,
        "professional_responders": professional_responder_count,
    }


def get_dashboard_stats():
    return counter()


def get_locations():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()

    conn.close()

    return locations


def get_edges():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM edges")
    edges = cursor.fetchall()

    conn.close()

    return edges


def add_location(name):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO locations (name)
        VALUES (?)
    """,
        (name.strip(),),
    )

    location_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return location_id


def add_edge(from_location_id, to_location_id, time):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM edges
        WHERE (
            from_location_id = ?
            AND to_location_id = ?
        )
        OR (
            from_location_id = ?
            AND to_location_id = ?
        )
    """,
        (from_location_id, to_location_id, to_location_id, from_location_id),
    )

    existing_edge = cursor.fetchone()

    if existing_edge:
        conn.close()
        return existing_edge["id"]

    cursor.execute(
        """
        INSERT INTO edges (
            from_location_id,
            to_location_id,
            time
        ) VALUES (?, ?, ?)
    """,
        (from_location_id, to_location_id, time),
    )

    edge_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return edge_id


def delete_location(location_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM edges
        WHERE from_location_id = ?
        OR to_location_id = ?
    """,
        (location_id, location_id),
    )

    cursor.execute(
        """
        DELETE FROM locations
        WHERE id = ?
    """,
        (location_id,),
    )

    conn.commit()
    conn.close()


def delete_edge(edge_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM edges
        WHERE id = ?
    """,
        (edge_id,),
    )

    conn.commit()
    conn.close()


def update_location_position(location_id, x_position, y_position):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE locations
        SET x_position = ?,
            y_position = ?
        WHERE id = ?
    """,
        (x_position, y_position, location_id),
    )

    conn.commit()
    conn.close()


def get_routing_edges():
    locations = get_locations()
    edges = get_edges()

    location_names = {}

    for location in locations:
        location_names[location["id"]] = location["name"]

    routing_edges = []

    for edge in edges:
        routing_edges.append(
            {
                "id": edge["id"],
                "from_location_id": edge["from_location_id"],
                "to_location_id": edge["to_location_id"],
                "from": location_names[edge["from_location_id"]],
                "to": location_names[edge["to_location_id"]],
                "time": edge["time"],
            }
        )

    return routing_edges
