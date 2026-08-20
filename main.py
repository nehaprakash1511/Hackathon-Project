# main.py
# Digital Hospital Queue - Backend

import database


# ==========================================
# TOKEN GENERATION
# ==========================================

def generate_token():
    """Generate the next available patient token."""

    patients = database.get_all_patients()

    numbers = []

    for patient in patients:

        token = patient[5]

        if token and token.startswith("A"):

            try:
                number = int(token[1:])
                numbers.append(number)

            except ValueError:
                pass

    if not numbers:
        return "A001"

    next_number = max(numbers) + 1

    return f"A{next_number:03d}"


# ==========================================
# REGISTER PATIENT
# ==========================================

def add_patient(
    name,
    age,
    phone,
    department,
    priority="Normal"
):
    """Register a new patient in the hospital queue."""

    token = generate_token()

    database.add_patient(
        name,
        age,
        phone,
        department,
        token,
        priority
    )

    return {
        "token": token,
        "name": name,
        "age": age,
        "phone": phone,
        "department": department,
        "priority": priority,
        "status": "Waiting"
    }


# ==========================================
# GET WAITING QUEUE
# ==========================================

def get_queue():
    """Return all patients currently waiting."""

    return database.get_waiting_patients()


# ==========================================
# GET PATIENT POSITION
# ==========================================

def get_position(token):
    """Return the patient's position in the queue."""

    patients = database.get_waiting_patients()

    for position, patient in enumerate(
        patients,
        start=1
    ):

        if patient[5] == token:
            return position

    return None


# ==========================================
# ESTIMATE WAITING TIME
# ==========================================

def get_waiting_time(token):
    """Estimate waiting time in minutes."""

    position = get_position(token)

    if position is None:
        return None

    return (position - 1) * 5


# ==========================================
# CALL NEXT PATIENT
# ==========================================

def call_next_patient():
    """Call the next patient according to priority."""

    patients = database.get_waiting_patients()

    if not patients:
        return None

    # Emergency → Elderly → Normal
    next_patient = patients[0]

    patient_id = next_patient[0]

    # Check if another patient is currently serving
    current_patient = database.get_serving_patient()

    if current_patient:

        database.update_patient_status(
            current_patient[0],
            "Completed"
        )

    database.update_patient_status(
        patient_id,
        "Serving"
    )

    return next_patient


# ==========================================
# COMPLETE PATIENT
# ==========================================

def complete_patient(token):
    """Mark a patient as completed."""

    patient = database.get_patient_by_token(token)

    if patient is None:
        return False

    patient_id = patient[0]

    database.update_patient_status(
        patient_id,
        "Completed"
    )

    return True


# ==========================================
# GET PATIENT BY TOKEN
# ==========================================

def get_patient(token):
    """Find a patient using their token."""

    return database.get_patient_by_token(token)


# ==========================================
# GET CURRENTLY SERVING PATIENT
# ==========================================

def get_current_patient():
    """Return the patient currently being served."""

    return database.get_serving_patient()


# ==========================================
# DISPLAY QUEUE
# ==========================================

def display_queue():
    """Display all waiting patients."""

    patients = database.get_waiting_patients()

    print("\nCurrent Queue:")
    print("------------------------------------------")

    if not patients:

        print("No patients waiting.")
        return

    for position, patient in enumerate(
        patients,
        start=1
    ):

        name = patient[1]
        department = patient[4]
        token = patient[5]
        priority = patient[6]

        waiting_time = (position - 1) * 5

        print(
            f"{token} | "
            f"{name} | "
            f"{department} | "
            f"{priority} | "
            f"Position: {position} | "
            f"Wait: {waiting_time} minutes"
        )