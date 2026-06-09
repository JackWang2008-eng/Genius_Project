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

    conn.commit()
    conn.close()

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

        # Create volunteers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            zone TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            availability TEXT NOT NULL,
            status TEXT DEFAULT 'Available',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

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
            zone,
            resource_type,
            availability
        ) VALUES (?, ?, ?, ?, ?)
    ''',
    (
        volunteer_data['volunteer_name'],
        volunteer_data['phone_number'],
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
            volunteers.resource_type
        FROM requests
        JOIN volunteers
        ON requests.zone = volunteers.zone
        AND requests.need_type = volunteers.resource_type
        WHERE requests.status = 'Open'
        AND volunteers.status = 'Available'
        ORDER BY requests.priority_score DESC
    ''')

    matches = cursor.fetchall()

    conn.close()

    return matches