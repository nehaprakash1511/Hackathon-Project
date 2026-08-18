import streamlit as st
from datetime import datetime

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Digital Hospital Queue",
    page_icon="🏥",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }

    .hospital-header {
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        color: white;
    }

    .hospital-header h1 {
        font-size: 40px;
        margin-bottom: 5px;
    }

    .hospital-header p {
        font-size: 18px;
        margin: 0;
    }

    .queue-card {
        padding: 25px;
        border-radius: 15px;
        background-color: #f0fdfa;
        border: 1px solid #99f6e4;
        text-align: center;
        margin-bottom: 20px;
    }

    .token {
        font-size: 55px;
        font-weight: bold;
        color: #0f766e;
    }

    .stat-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        text-align: center;
    }

    .footer {
        text-align: center;
        color: #64748b;
        padding: 30px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# SESSION STATE
# -----------------------------
if "patients" not in st.session_state:
    st.session_state.patients = []

if "token_number" not in st.session_state:
    st.session_state.token_number = 0

if "current_patient" not in st.session_state:
    st.session_state.current_patient = None


# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="hospital-header">
    <h1>🏥 Digital Hospital Queue</h1>
    <p>Smart • Simple • Stress-Free Hospital Visits</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🏥 Hospital Menu")

page = st.sidebar.radio(
    "Choose an option",
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
    st.write("Register your visit and receive a digital queue token.")

    with st.form("patient_form"):

        name = st.text_input(
            "Patient Name",
            placeholder="Enter patient name"
        )

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=25
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

        if not name or not phone:
            st.error("Please enter the patient name and phone number.")

        else:

            st.session_state.token_number += 1

            token = f"A{st.session_state.token_number:03d}"

            patient = {
                "token": token,
                "name": name,
                "age": age,
                "phone": phone,
                "department": department,
                "priority": priority,
                "status": "Waiting",
                "time": datetime.now().strftime("%I:%M %p")
            }

            st.session_state.patients.append(patient)

            st.success("Registration successful!")

            st.markdown(f"""
            <div class="queue-card">
                <h3>Your Queue Token</h3>
                <div class="token">{token}</div>
                <p><b>Department:</b> {department}</p>
                <p><b>Priority:</b> {priority}</p>
                <p>Please wait for your token to be called.</p>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# QUEUE STATUS
# ============================================================

elif page == "Queue Status":

    st.header("📋 Live Queue Status")

    waiting_patients = [
        p for p in st.session_state.patients
        if p["status"] == "Waiting"
    ]

    # Statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <h3>👥 Waiting Patients</h3>
                <h2>{len(waiting_patients)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        current = st.session_state.current_patient

        current_token = (
            current["token"]
            if current
            else "None"
        )

        st.markdown(
            f"""
            <div class="stat-card">
                <h3>🔔 Now Serving</h3>
                <h2>{current_token}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        estimated_time = len(waiting_patients) * 5

        st.markdown(
            f"""
            <div class="stat-card">
                <h3>⏱️ Estimated Wait</h3>
                <h2>{estimated_time} min</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Queue table
    if waiting_patients:

        st.subheader("Patients Currently Waiting")

        for patient in waiting_patients:

            priority_icon = {
                "Normal": "🟢",
                "Senior Citizen": "🟡",
                "Emergency": "🔴"
            }

            st.info(
                f"{priority_icon[patient['priority']]} "
                f"**{patient['token']}** — "
                f"{patient['name']} — "
                f"{patient['department']} — "
                f"{patient['priority']}"
            )

    else:

        st.success("🎉 No patients are currently waiting!")


# ============================================================
# DOCTOR DASHBOARD
# ============================================================

elif page == "Doctor Dashboard":

    st.header("👨‍⚕️ Doctor / Receptionist Dashboard")

    waiting_patients = [
        p for p in st.session_state.patients
        if p["status"] == "Waiting"
    ]

    current = st.session_state.current_patient

    # Current patient
    st.subheader("🔔 Current Patient")

    if current:

        st.markdown(f"""
        <div class="queue-card">
            <h3>Now Serving</h3>
            <div class="token">{current['token']}</div>
            <p><b>Name:</b> {current['name']}</p>
            <p><b>Department:</b> {current['department']}</p>
            <p><b>Priority:</b> {current['priority']}</p>
        </div>
        """, unsafe_allow_html=True)

    else:

        st.info("No patient is currently being served.")

    # Next patient button
    if st.button(
        "➡️ Call Next Patient",
        use_container_width=True
    ):

        if waiting_patients:

            # Emergency patients first
            priority_order = {
                "Emergency": 0,
                "Senior Citizen": 1,
                "Normal": 2
            }

            waiting_patients.sort(
                key=lambda p: priority_order[p["priority"]]
            )

            next_patient = waiting_patients[0]

            next_patient["status"] = "Serving"

            # Mark previous patient as completed
            if current:
                current["status"] = "Completed"

            st.session_state.current_patient = next_patient

            st.success(
                f"Now serving {next_patient['token']} — "
                f"{next_patient['name']}"
            )

            st.rerun()

        else:

            st.warning("There are no patients waiting.")

    st.divider()

    # Patient history
    st.subheader("📊 Patient Queue")

    if st.session_state.patients:

        for patient in st.session_state.patients:

            status_icon = {
                "Waiting": "🟡",
                "Serving": "🔵",
                "Completed": "🟢"
            }

            st.write(
                f"{status_icon.get(patient['status'], '⚪')} "
                f"**{patient['token']}** | "
                f"{patient['name']} | "
                f"{patient['department']} | "
                f"{patient['status']}"
            )

    else:

        st.info("No patients registered yet.")


# -----------------------------
# FOOTER
# -----------------------------

st.markdown("""
<div class="footer">
    🏥 Digital Hospital Queue System<br>
    Reducing waiting time • Improving patient experience
</div>
""", unsafe_allow_html=True)