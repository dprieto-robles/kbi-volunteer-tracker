import streamlit as st
import psycopg2
from datetime import date

st.set_page_config(page_title="Volunteer Assignments", page_icon="🔗")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🔗 Volunteer Assignments")

# ========================================
# ADD ASSIGNMENT FORM
# ========================================
st.subheader("Assign a Volunteer to a Program")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, first_name || ' ' || last_name FROM volunteers ORDER BY last_name;")
    volunteers = cur.fetchall()

    cur.execute("SELECT id, program_name, location FROM programs ORDER BY program_name;")
    programs = cur.fetchall()

    cur.close()
    conn.close()

    if not volunteers:
        st.warning("No volunteers found. Please add a volunteer first.")
    elif not programs:
        st.warning("No programs found. Please add a program first.")
    else:
        volunteer_options = {row[1]: row[0] for row in volunteers}
        program_options = {f"{row[1]} ({row[2]})": row[0] for row in programs}

        with st.form("add_assignment_form"):
            selected_volunteer = st.selectbox(
                "Select Volunteer *",
                options=list(volunteer_options.keys())
            )
            selected_program = st.selectbox(
                "Select Program *",
                options=list(program_options.keys())
            )
            role = st.text_input("Role *")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date *", value=date.today())
            with col2:
                end_date = st.date_input("End Date (optional)", value=None)
            hours_served = st.number_input(
                "Hours Served (optional)",
                min_value=0.0,
                step=0.5
            )

            submitted = st.form_submit_button("Create Assignment")

            if submitted:
                errors = []

                if not role.strip():
                    errors.append("Role is required.")
                if end_date and end_date < start_date:
                    errors.append("End date cannot be before start date.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO volunteer_assignments
                            (volunteer_id, program_id, role, start_date, end_date, hours_served)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, (
                            volunteer_options[selected_volunteer],
                            program_options[selected_program],
                            role.strip(),
                            start_date,
                            end_date or None,
                            hours_served
                        ))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"Successfully assigned '{selected_volunteer}' to '{selected_
