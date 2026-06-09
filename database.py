import sqlite3

DATABASE = 'genius.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create requests table
    cursor.execute('''
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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create disaster_status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disaster_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disaster_type TEXT NOT NULL,
            stage TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            helper_type TEXT NOT NULL DEFAULT 'Community Volunteer',
            zone TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            availability TEXT NOT NULL,
            status TEXT DEFAULT 'Available',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    ensure_column(cursor, "volunteers", "helper_type", "TEXT NOT NULL DEFAULT 'Community Volunteer'")

    conn.commit()
    conn.close()

def ensure_column(cursor, table_name, column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [column["name"] for column in cursor.fetchall()]

    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")

def add_request(request_data):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO requests (
            resident_name, phone_number, zone, need_type, injury_level,
            mobility_status, vulnerable_person, evacuation_need, safe_shelter,
            red_flags, urgency, priority_score, triage_reasons
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', 
    (
        request_data['resident_name'],
        request_data['phone_number'],
        request_data['zone'],
        request_data['need_type'],
        request_data['injury_level'],
        request_data['mobility_status'],
        request_data['vulnerable_person'],
        request_data['evacuation_need'],
        request_data['safe_shelter'],
        ','.join(request_data.get('red_flags', [])),
        request_data['urgency'],
        request_data['priority_score'],
        ', '.join(request_data.get('triage_reasons', []))
    ))

    conn.commit()
    conn.close()

def get_all_requests():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM requests ORDER BY priority_score DESC, timestamp ASC')
    requests = cursor.fetchall()
    conn.close()
    return requests

def add_volunteer(volunteer_data):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO volunteers (
            volunteer_name,
            phone_number,
            helper_type,
            zone,
            resource_type,
            availability
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''',
    (
        volunteer_data['volunteer_name'],
        volunteer_data['phone_number'],
        volunteer_data['helper_type'],
        volunteer_data['zone'],
        volunteer_data['resource_type'],
        volunteer_data['availability']
    ))

    conn.commit()
    conn.close()

def get_all_volunteers():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM volunteers
        ORDER BY timestamp DESC
    ''')

    volunteers = cursor.fetchall()

    conn.close()

    return volunteers

def save_disaster_status(disaster_type, stage):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM disaster_status')

    cursor.execute('''
        INSERT INTO disaster_status (
            disaster_type,
            stage
        ) VALUES (?, ?)
    ''',
    (
        disaster_type,
        stage
    ))

    conn.commit()
    conn.close()

def get_disaster_status():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM disaster_status
        ORDER BY timestamp DESC
        LIMIT 1
    ''')

    disaster_status = cursor.fetchone()

    conn.close()

    if disaster_status:
        return disaster_status

    return {
        "disaster_type": None,
        "stage": None
    }

def find_matches():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            requests.id AS request_id,
            requests.resident_name,
            requests.phone_number AS resident_phone,
            requests.zone,
            requests.need_type,
            requests.urgency,
            requests.priority_score,
            volunteers.id AS volunteer_id,
            volunteers.volunteer_name,
            volunteers.phone_number AS volunteer_phone,
            volunteers.helper_type,
            volunteers.resource_type
        FROM requests
        JOIN volunteers
        ON requests.zone = volunteers.zone
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
    ''')

    matches = cursor.fetchall()

    conn.close()

    return matches

def assign_match(request_id, volunteer_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE requests
        SET status = 'Assigned'
        WHERE id = ?
    ''', (request_id,))

    cursor.execute('''
        UPDATE volunteers
        SET status = 'Assigned'
        WHERE id = ?
    ''', (volunteer_id,))

    conn.commit()
    conn.close()

def resolve_request(request_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE requests
        SET status = 'Resolved'
        WHERE id = ?
    ''', (request_id,))

    conn.commit()
    conn.close()
