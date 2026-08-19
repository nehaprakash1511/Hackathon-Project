import streamlit as st
import main


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Digital Hospital Queue",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.hospital-header {
    text-align: center;
    padding: 25px;
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


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div class="hospital-header">
    <h1>🏥 Digital Hospital Queue</h1>
    <p>Smart • Simple • Stress-Free Hospital Visits</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("🏥 Hospital Menu")

page = st.sidebar.radio(
    "Choose an option",
    [
        "Patient Registration",
        "Queue Status",
        "Doctor Dashboard"
    ]
)


# ==========================================
# PATIENT REGISTRATION
# ==========================================

if page == "Patient Registration":

    st.header("👤 Patient Registration")

    st.write(
        "Register your visit and receive a digital queue token."
    )

    with st.form("patient_form"):

        name = st.text_input(
            "Patient Name",
            placeholder="Enter patient name"
        )

        age = st.number_input(
            "Age",
            min_value=1,
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
                "Elderly",
                "Emergency"
            ]
        )

        submitted = st.form_submit_button(
            "🎫 Get Queue Token",
            use_container_width=True
        )

    if submitted:

        if not name.strip():

            st.error("Please enter the patient name.")

        elif not phone.strip():

            st.error("Please enter the phone number.")

        else:

            try:

                patient = main.add_patient(
                    name.strip(),
                    int(age),
                    phone.strip(),
                    department,
                    priority
                )

                st.success("Registration successful!")

                st.markdown(
                    f"""
                    <div class="queue-card">
                        <h3>Your Queue Token</h3>

                        <div class="token">
                            {patient["token"]}
                        </div>

                        <p>
                            <b>Patient:</b>
                            {patient["name"]}
                        </p>

                        <p>
                            <b>Department:</b>
                            {patient["department"]}
                        </p>

                        <p>
                            <b>Priority:</b>
                            {patient["priority"]}
                        </p>

                        <p>
                            Please wait for your token to be called.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                position = main.get_position(
                    patient["token"]
                )

                wait_time = main.get_waiting_time(
                    patient["token"]
                )

                if position is not None:

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "Queue Position",
                            position
                        )

                    with col2:

                        st.metric(
                            "Estimated Wait",
                            f"{wait_time} min"
                        )

            except Exception as error:

                st.error(
                    "Unable to register patient."
                )

                st.code(str(error))


# ==========================================
# QUEUE STATUS
# ==========================================

elif page == "Queue Status":

    st.header("📋 Live Queue Status")

    patients = main.get_queue()

    col1, col2, col3 = st.columns(3)

    # Waiting patients
    with col1:

        st.markdown(
            f"""
            <div class="stat-card">
                <h3>👥 Waiting Patients</h3>
                <h2>{len(patients)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Currently serving
    with col2:

        current = main.get_current_patient()

        if current:

            current_token = current[5]

        else:

            current_token = "None"

        st.markdown(
            f"""
            <div class="stat-card">
                <h3>🔔 Now Serving</h3>
                <h2>{current_token}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Estimated wait
    with col3:

        estimated_time = len(patients) * 5

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

    # Waiting patients
    if patients:

        st.subheader("Patients Currently Waiting")

        for position, patient in enumerate(
            patients,
            start=1
        ):

            token = patient[5]
            name = patient[1]
            department = patient[4]
            priority = patient[6]

            if priority == "Emergency":

                priority_icon = "🔴"

            elif priority == "Elderly":

                priority_icon = "🟡"

            else:

                priority_icon = "🟢"

            wait_time = (position - 1) * 5

            st.info(
                f"{priority_icon} "
                f"**{token}** — "
                f"{name} — "
                f"{department} — "
                f"{priority} — "
                f"Position: {position} — "
                f"Wait: {wait_time} min"
            )

    else:

        st.success(
            "🎉 No patients are currently waiting!"
        )


# ==========================================
# DOCTOR DASHBOARD
# ==========================================

elif page == "Doctor Dashboard":

    st.header(
        "👨‍⚕️ Doctor / Receptionist Dashboard"
    )

    current = main.get_current_patient()

    # --------------------------------------
    # CURRENT PATIENT
    # --------------------------------------

    st.subheader("🔔 Current Patient")

    if current:

        name = current[1]
        age = current[2]
        department = current[4]
        token = current[5]
        priority = current[6]

        st.markdown(
            f"""
            <div class="queue-card">

                <h3>Now Serving</h3>

                <div class="token">
                    {token}
                </div>

                <p>
                    <b>Name:</b> {name}
                </p>

                <p>
                    <b>Age:</b> {age}
                </p>

                <p>
                    <b>Department:</b> {department}
                </p>

                <p>
                    <b>Priority:</b> {priority}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "✅ Complete Current Patient",
            use_container_width=True
        ):

            success = main.complete_patient(token)

            if success:

                st.success(
                    f"{token} - {name} completed."
                )

                st.rerun()

            else:

                st.error(
                    "Unable to complete patient."
                )

    else:

        st.info(
            "No patient is currently being served."
        )

    st.divider()

    # --------------------------------------
    # CALL NEXT PATIENT
    # --------------------------------------

    st.subheader("📢 Queue Management")

    if st.button(
        "➡️ Call Next Patient",
        use_container_width=True
    ):

        next_patient = main.call_next_patient()

        if next_patient:

            st.success(
                f"Now serving "
                f"{next_patient[5]} - "
                f"{next_patient[1]}"
            )

            st.rerun()

        else:

            st.warning(
                "There are no patients waiting."
            )

    st.divider()

    # --------------------------------------
    # CURRENT QUEUE
    # --------------------------------------

    st.subheader("📊 Current Queue")

    patients = main.get_queue()

    if patients:

        for position, patient in enumerate(
            patients,
            start=1
        ):

            token = patient[5]
            name = patient[1]
            department = patient[4]
            priority = patient[6]

            if priority == "Emergency":

                icon = "🔴"

            elif priority == "Elderly":

                icon = "🟡"

            else:

                icon = "🟢"

            st.write(
                f"{icon} "
                f"**{token}** | "
                f"{name} | "
                f"{department} | "
                f"{priority} | "
                f"Position: {position}"
            )

    else:

        st.info(
            "No patients are currently waiting."
        )


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="footer">
        🏥 Digital Hospital Queue System<br>
        Reducing waiting time • Improving patient experience
    </div>
    """,
    unsafe_allow_html=True
)