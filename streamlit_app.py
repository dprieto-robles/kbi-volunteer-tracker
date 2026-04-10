import streamlit as st
import psycopg2

st.set_page_config(page_title="KBI Volunteer Tracker", page_icon="🌎")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🌎 Kino Border Initiative Volunteer Tracker")
st.write("Welcome! Use the sidebar to navigate between pages.")

st.markdown("---")
st.subheader("📊 Dashboard")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM volunteers;")
    volunteer_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM programs;")
    program_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM volunteer_assignments;")
    assignment_count = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(hours_served), 0) FROM volunteer_assignments;")
    total_hours = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Volunteers", volunteer_count)
    col2.metric("Total Programs", program_count)
    col3.metric("Total Assignments", assignment_count)
    col4.metric("Total Hours Served", f"{total_hours:.1f}")

    st.markdown("---")
    st.subheader("📋 Recent Volunteer Assignments")

    cur.execute("""
        SELECT
            v.first_name || ' ' || v.last_name AS volunteer,
            p.program_name,
            p.location,
            va.role,
            va.start_date,
            va.hours_served
        FROM volunteer_assignments va
        JOIN volunteers v ON va.volunteer_id = v.id
        JOIN programs p ON va.program_id = p.id
        ORDER BY va.created_at DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        st.table([{
            "Volunteer": r[0],
            "Program": r[1],
            "Location": r[2],
            "Role": r[3],
            "Start Date": str(r[4]),
            "Hours Served": r[5]
        } for r in rows])
    else:
        st.info("No assignments yet. Add volunteers and programs to get started!")

except Exception as e:
    st.error(f"Database connection error: {e}")
