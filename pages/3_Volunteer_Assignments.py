import streamlit as st
import psycopg2
from datetime import date

st.set_page_config(page_title="Volunteer Assignments", page_icon="🔗")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🔗 Volunteer Assignments")

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
            selected_volunteer = st.selectbox("Select Volunteer *", options=list(volunteer_options.keys()))
            selected_program = st.selectbox("Select Program *", options=list(program_options.keys()))
            role = st.text_input("Role *")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date *", value=date.today())
            with col2:
                end_date = st.date_input("End Date (optional)", value=None)
            hours_served = st.number_input("Hours Served (optional)", min_value=0.0, step=0.5)
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
                        st.success(f"Successfully assigned '{selected_volunteer}' to '{selected_program}'!")
                    except Exception as e:
                        st.error(f"Error: {e}")

except Exception as e:
    st.error(f"Error loading data: {e}")

st.markdown("---")
st.subheader("Current Assignments")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            va.id,
            v.first_name || ' ' || v.last_name AS volunteer,
            p.program_name,
            p.location,
            va.role,
            va.start_date,
            va.end_date,
            va.hours_served
        FROM volunteer_assignments va
        JOIN volunteers v ON va.volunteer_id = v.id
        JOIN programs p ON va.program_id = p.id
        ORDER BY va.start_date DESC;
    """)
    assignments = cur.fetchall()
    cur.close()
    conn.close()

    if not assignments:
        st.info("No assignments yet. Create one above to get started!")
    else:
        for a in assignments:
            col1, col2 = st.columns([5, 1])
            with col1:
                end = str(a[6]) if a[6] else "Ongoing"
                st.write(
                    f"**{a[1]}** | {a[2]} ({a[3]}) | Role: {a[4]} | "
                    f"{str(a[5])} to {end} | Hours: {a[7]}"
                )
            with col2:
                if st.button("Delete", key=f"delete_{a[0]}"):
                    st.session_state["deleting_assignment"] = a[0]

except Exception as e:
    st.error(f"Error loading assignments: {e}")

if "deleting_assignment" in st.session_state:
    aid = st.session_state["deleting_assignment"]
    st.warning("Are you sure you want to delete this assignment?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, delete"):
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM volunteer_assignments WHERE id = %s;", (aid,))
                conn.commit()
                cur.close()
                conn.close()
                del st.session_state["deleting_assignment"]
                st.success("Assignment deleted successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    with col2:
        if st.button("Cancel"):
            del st.session_state["deleting_assignment"]
            st.rerun()
