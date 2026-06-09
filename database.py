import sqlite3

DATABASE = "SafeHarbor.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row #use dictionary
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resident_name TEXT NOT NULL,
            zone TEXT NOT NULL,
            need_type TEXT NOT NULL,
            urgency TEXT NOT NULL,
            factors TEXT,
            priority_score INTEGER,
            priority_reasons TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create volunteers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_name TEXT NOT NULL,
            availability TEXT NOT NULL,
            zone TEXT NOT NULL,
            resources TEXT
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def add_request(resident_name, zone, need_type, urgency, factors, priority_score, priority_reasons):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO requests (
            resident_name,
            zone,
            need_type,
            urgency,
            factors,
            priority_score,
            priority_reasons,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, 
    (
        resident_name,
        zone,
        need_type,
        urgency,
        ", ".join(factors),
        priority_score,
        ", ".join(priority_reasons),
        "Open"
    )
    )

    conn.commit()
    conn.close()

def add_volunteer(volunteer_name, availability, zone, resources):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO volunteers (
            volunteer_name,
            availability,
            zone,
            resources,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, 
    (
        volunteer_name,
        availability,
        zone,
        ", ".join(resources),
        "Available"
    )
    )

    conn.commit()
    conn.close()

def count_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM requests WHERE status = 'Open'")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def count_volunteers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM volunteers WHERE status = 'Available'")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def count_critical():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM requests WHERE urgency = 'Critical' AND status = 'Open'")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def get_recent_requests():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM requests
        ORDER BY created_at DESC
        LIMIT 5
    """)

    requests = cursor.fetchall()

    connection.close()
    return requests