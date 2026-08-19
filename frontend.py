import streamlit as st
import database


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Digital Hospital Queue",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# DATABASE SETUP
# ============================================================

database.create_table()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_token(token):
    """
    Converts:
        1    -> A001
        2    -> A002
        A001 -> A001

    This keeps the app compatible with the existing database.
    """

    if token is None:
        return "N/A"

    token = str(token).strip()

    if token.upper().startswith("A"):
        return token.upper()

    try:
        return f"A{int(token):03d}"
    except ValueError:
        return token


def get_all_patients():
    """Get all patients from the database."""

    connection = database.connect_db()
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


def get_current_patient():
    """Get the patient currently being served."""

    connection = database.connect_db()
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
        WHERE status = 'Serving'
        ORDER BY id ASC
        LIMIT 1
    """)

    patient = cursor.fetchone()

    connection.close()

    return patient


def get_waiting_patients():
    """
    Get waiting patients and arrange them by priority.

    Emergency -> first
    Senior Citizen / Elderly -> second
    Normal -> last
    """

    patients = database.get_waiting_patients()

    priority_order = {
        "Emergency": 0,
        "Senior Citizen": 1,
        "Elderly": 1,
        "Normal": 2
    }

    patients.sort(
        key=lambda patient: (
            priority_order.get(patient[6], 2),
            str(patient[5])
        )
    )

    return patients


def get_next_token_number():
    """Find the next available token number."""

    patients = get_all_patients()

    highest_number = 0

    for patient in patients:

        token = patient[5]

        if token is None:
            continue

        token = str(token).strip()

        if token.upper().startswith("A"):
            token = token[1:]

        try:
            number = int(token)

            if number > highest_number:
                highest_number = number

        except ValueError:
            continue

    return highest_number + 1


def register_patient(
    name,
    age,
    phone,
    department,
    priority
):
    """Register a new patient."""

    token_number = get_next_token_number()

    database.add_patient(
        name,
        age,
        phone,
        department,
        token_number,
        priority
    )

    return token_number


def call_next_patient():
    """Call the next patient in the queue."""

    waiting_patients = get_waiting_patients()

    if not waiting_patients:
        return None

    current_patient = get_current_patient()

    # Complete the current patient first
    if current_patient is not None:
        database.update_patient_status(
            current_patient[0],
            "Completed"
        )

    # Call the next patient
    next_patient = waiting_patients[0]

    database.update_patient_status(
        next_patient[0],
        "Serving"
    )

    return next_patient


def complete_current_patient():
    """Complete the currently serving patient."""

    current_patient = get_current_patient()

    if current_patient is None:
        return False

    database.update_patient_status(
        current_patient[0],
        "Completed"
    )

    return True


# ============================================================
# HEADER
# ============================================================

st.title("🏥 Digital Hospital Queue")

st.caption(
    "Smart • Simple • Stress-Free Hospital Visits"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏥 Hospital Menu")

page = st.sidebar.radio(
    "Choose an option:",
    [
        "Patient Registration",
        "Queue Status",
        "Doctor Dashboard"
    ]
)


# ============================================================
# PATIENT REGISTRATION
# ============================================================

if page == "Patient Registration":

    st.header("👤 Patient Registration")

    st.write(
        "Register your visit and receive a digital queue token."
    )

    with st.form("patient_registration_form"):

        name = st.text_input(
            "Patient Name",
            placeholder="Enter patient name"
        )

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=25,
            step=1
        )

        phone = st.text_input(
            "Phone Number",
            placeholder="Enter phone number"
        )

        department = st.selectbox(
            "Select Department",
            [
                "General Medicine",
                "Cardiology",
                "Orthopedics",
                "Pediatrics",
                "Dermatology",
                "ENT",
                "Dental"
            ]
        )

        priority = st.selectbox(
            "Patient Priority",
            [
                "Normal",
                "Senior Citizen",
                "Emergency"
            ]
        )

        submitted = st.form_submit_button(
            "🎫 Get Queue Token",
            use_container_width=True
        )

    if submitted:

        if not name.strip():

            st.error(
                "Please enter the patient name."
            )

        elif not phone.strip():

            st.error(
                "Please enter the phone number."
            )

        elif len(phone.strip()) < 10:

            st.error(
                "Please enter a valid phone number."
            )

        else:

            try:

                token_number = register_patient(
                    name.strip(),
                    int(age),
                    phone.strip(),
                    department,
                    priority
                )

                token = format_token(token_number)

                st.success(
                    "Registration successful!"
                )

                st.subheader("🎫 Your Queue Token")

                st.title(token)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Patient",
                        name
                    )

                with col2:
                    st.metric(
                        "Department",
                        department
                    )

                with col3:
                    st.metric(
                        "Priority",
                        priority
                    )

                waiting_patients = get_waiting_patients()

                position = None

                for index, patient in enumerate(
                    waiting_patients,
                    start=1
                ):

                    if str(patient[5]) == str(token_number):
                        position = index
                        break

                if position is not None:

                    wait_time = (position - 1) * 5

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Queue Position",
                            position
                        )

                    with col2:
                        st.metric(
                            "Estimated Wait",
                            f"{wait_time} minutes"
                        )

                st.info(
                    "Please wait for your token to be called."
                )

            except Exception as error:

                st.error(
                    "Registration failed."
                )

                st.write(
                    "Please check the terminal for details."
                )

                print(error)


# ============================================================
# QUEUE STATUS
# ============================================================

elif page == "Queue Status":

    st.header("📋 Live Queue Status")

    waiting_patients = get_waiting_patients()

    current_patient = get_current_patient()

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    if current_patient:

        current_token = format_token(
            current_patient[5]
        )

    else:

        current_token = "None"

    estimated_wait = len(waiting_patients) * 5

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "👥 Waiting Patients",
            len(waiting_patients)
        )

    with col2:

        st.metric(
            "🔔 Now Serving",
            current_token
        )

    with col3:

        st.metric(
            "⏱️ Estimated Wait",
            f"{estimated_wait} min"
        )

    st.divider()

    # --------------------------------------------------------
    # CURRENT PATIENT
    # --------------------------------------------------------

    if current_patient:

        st.subheader("🔔 Currently Being Served")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write("**Token**")
            st.write(
                format_token(current_patient[5])
            )

        with col2:
            st.write("**Name**")
            st.write(current_patient[1])

        with col3:
            st.write("**Department**")
            st.write(current_patient[4])

        with col4:
            st.write("**Priority**")
            st.write(current_patient[6])

        st.divider()

    # --------------------------------------------------------
    # WAITING PATIENTS
    # --------------------------------------------------------

    st.subheader("👥 Patients Currently Waiting")

    if not waiting_patients:

        st.success(
            "🎉 No patients are currently waiting!"
        )

    else:

        for position, patient in enumerate(
            waiting_patients,
            start=1
        ):

            token = format_token(patient[5])

            name = patient[1]

            department = patient[4]

            priority = patient[6]

            wait_time = (position - 1) * 5

            if priority == "Emergency":

                icon = "🔴"

            elif priority in [
                "Senior Citizen",
                "Elderly"
            ]:

                icon = "🟡"

            else:

                icon = "🟢"

            with st.container(border=True):

                st.write(
                    f"{icon} **{token} — {name}**"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"Department: **{department}**"
                    )

                with col2:

                    st.write(
                        f"Priority: **{priority}**"
                    )

                with col3:

                    st.write(
                        f"Position: **{position}**"
                    )

                st.caption(
                    f"Estimated wait: {wait_time} minutes"
                )


# ============================================================
# DOCTOR DASHBOARD
# ============================================================

elif page == "Doctor Dashboard":

    st.header(
        "👨‍⚕️ Doctor / Receptionist Dashboard"
    )

    # --------------------------------------------------------
    # CURRENT PATIENT
    # --------------------------------------------------------

    st.subheader("🔔 Current Patient")

    current_patient = get_current_patient()

    if current_patient:

        token = format_token(
            current_patient[5]
        )

        name = current_patient[1]

        age = current_patient[2]

        department = current_patient[4]

        priority = current_patient[6]

        st.success(
            f"Now Serving: {token}"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write("### Patient Details")

            st.write(
                f"**Token:** {token}"
            )

            st.write(
                f"**Name:** {name}"
            )

            st.write(
                f"**Age:** {age}"
            )

        with col2:

            st.write("### Visit Details")

            st.write(
                f"**Department:** {department}"
            )

            st.write(
                f"**Priority:** {priority}"
            )

            st.write(
                "**Status:** Serving"
            )

        if st.button(
            "✅ Complete Current Patient",
            use_container_width=True
        ):

            try:

                complete_current_patient()

                st.success(
                    f"{token} - {name} has been completed."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    "Could not complete the patient."
                )

                print(error)

    else:

        st.info(
            "No patient is currently being served."
        )

    st.divider()

    # --------------------------------------------------------
    # CALL NEXT PATIENT
    # --------------------------------------------------------

    st.subheader("📢 Queue Management")

    if st.button(
        "➡️ Call Next Patient",
        use_container_width=True
    ):

        try:

            next_patient = call_next_patient()

            if next_patient is None:

                st.warning(
                    "There are no patients waiting."
                )

            else:

                next_token = format_token(
                    next_patient[5]
                )

                next_name = next_patient[1]

                st.success(
                    f"Now serving {next_token} — {next_name}"
                )

                st.rerun()

        except Exception as error:

            st.error(
                "Could not call the next patient."
            )

            print(error)

    st.divider()

    # --------------------------------------------------------
    # WAITING QUEUE
    # --------------------------------------------------------

    st.subheader("📊 Current Queue")

    waiting_patients = get_waiting_patients()

    if not waiting_patients:

        st.info(
            "No patients are currently waiting."
        )

    else:

        for position, patient in enumerate(
            waiting_patients,
            start=1
        ):

            token = format_token(patient[5])

            name = patient[1]

            department = patient[4]

            priority = patient[6]

            wait_time = (position - 1) * 5

            if priority == "Emergency":

                icon = "🔴"

            elif priority in [
                "Senior Citizen",
                "Elderly"
            ]:

                icon = "🟡"

            else:

                icon = "🟢"

            with st.container(border=True):

                st.write(
                    f"{icon} **{token} — {name}**"
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(
                        f"Position: **{position}**"
                    )

                with col2:
                    st.write(
                        f"Department: **{department}**"
                    )

                with col3:
                    st.write(
                        f"Priority: **{priority}**"
                    )

                with col4:
                    st.write(
                        f"Wait: **{wait_time} min**"
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏥 Digital Hospital Queue System | "
    "Reducing waiting time • Improving patient experience"
)