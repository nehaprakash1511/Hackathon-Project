# database.py
# Digital Hospital Queue - Database Layer

import sqlite3

DATABASE_NAME = "hospital.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def connect_db():
    return sqlite3.connect(DATABASE_NAME)


# ==========================================
# CREATE DATABASE TABLE
# ==========================================

def create_table():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            priority TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'Waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# ADD PATIENT
# ==========================================

def add_patient(
    name,
    age,
    phone,
    department,
    token,
    priority="Normal"
):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO patients
        (
            name,
            age,
            phone,
            department,
            token,
            priority
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        phone,
        department,
        token,
        priority
    ))

    connection.commit()
    connection.close()


# ==========================================
# GET WAITING PATIENTS
# ==========================================

def get_waiting_patients():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            age,
            phone,
            department,
            token,
            priority,
            status
        FROM patients
        WHERE status = 'Waiting'
        ORDER BY
            CASE priority
                WHEN 'Emergency' THEN 1
                WHEN 'Elderly' THEN 2
                ELSE 3
            END,
            id ASC
    """)

    patients = cursor.fetchall()

    connection.close()

    return patients


# ==========================================
# GET ALL PATIENTS
# ==========================================

def get_all_patients():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            age,
            phone,
            department,
            token,
            priority,
            status,
            created_at
        FROM patients
        ORDER BY id ASC
    """)

    patients = cursor.fetchall()

    connection.close()

    return patients


# ==========================================
# GET PATIENT BY TOKEN
# ==========================================

def get_patient_by_token(token):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            age,
            phone,
            department,
            token,
            priority,
            status
        FROM patients
        WHERE token = ?
    """, (token,))

    patient = cursor.fetchone()

    connection.close()

    return patient


# ==========================================
# UPDATE PATIENT STATUS
# ==========================================

def update_patient_status(patient_id, status):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE patients
        SET status = ?
        WHERE id = ?
    """, (
        status,
        patient_id
    ))

    connection.commit()
    connection.close()


# ==========================================
# GET CURRENTLY SERVING PATIENT
# ==========================================

def get_serving_patient():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            age,
            phone,
            department,
            token,
            priority,
            status
        FROM patients
        WHERE status = 'Serving'
        ORDER BY id ASC
        LIMIT 1
    """)

    patient = cursor.fetchone()

    connection.close()

    return patient


# ==========================================
# COUNT WAITING PATIENTS
# ==========================================

def count_waiting_patients():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE status = 'Waiting'
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ==========================================
# INITIALIZE DATABASE
# ==========================================

create_table()