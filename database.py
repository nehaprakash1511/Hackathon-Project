import sqlite3

DATABASE_NAME = "hospital.db"


def connect_db():
    return sqlite3.connect(DATABASE_NAME)
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
            token INTEGER NOT NULL,
            priority TEXT DEFAULT 'Normal',
            status TEXT DEFAULT 'Waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()
def add_patient(name, age, phone, department, token, priority="Normal"):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO patients
        (name, age, phone, department, token, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, phone, department, token, priority))

    connection.commit()
    connection.close()
if __name__ == "__main__":
    create_table()

def get_waiting_patients():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, age, phone, department, token, priority, status
        FROM patients
        WHERE status = 'Waiting'
        ORDER BY token ASC
    """)

    patients = cursor.fetchall()

    connection.close()

    return patients

def update_patient_status(patient_id, status):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE patients
        SET status = ?
        WHERE id = ?
    """, (status, patient_id))

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_table()

    update_patient_status(1, "Serving")

    print("Patient status updated successfully!")

    patients = get_waiting_patients()

    print("Waiting patients:")

    for patient in patients:
        print(patient)