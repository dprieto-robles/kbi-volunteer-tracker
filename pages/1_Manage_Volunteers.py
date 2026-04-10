import streamlit as st
import psycopg2
import re

st.set_page_config(page_title="Manage Volunteers", page_icon="👤")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("👤 Manage Volunteers")

# ========================================
# ADD VOLUNTEER FORM
# ========================================
st.subheader("Add a New Volunteer")

with st.form("add_volunteer_form"):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name *")
        email = st.text_input("Email *")
        age = st.number_input("Age *", min_value=1, max_value=120, step=1)
    with col2:
        last_name = st.text_input("Last Name *")
        phone = st.text_input("Phone *")
        field_of_study = st.text_input("Field of Study (optional)")

    submitted = st.form_submit_button("Add Volunteer")

    if submitted:
        errors = []
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not first_name.strip():
            errors.append("First name is required.")
        if not last_name.strip():
            errors.append("Last name is required.")
        if not email.strip():
            errors.append("Email is required.")
        elif not re.match(email_pattern, email):
            errors.append("Please enter a valid email address.")
        if not phone.strip():
            errors.append("Phone number is required.")
        elif not re.match(r'^\d{10,}$', phone.replace("-", "").replace(" ", "")):
            errors.append("Phone must contain at least 10 digits.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO volunteers
                    (first_name, last_name, email, phone, age, field_of_study)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (
                    first_name.strip(),
                    last_name.strip(),
                    email.strip(),
                    phone.strip(),
                    age,
                    field_of_study.strip() or None
                ))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"Volunteer '{first_name} {last_name}' added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error("A volunteer with that email already exists.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ========================================
# SEARCH AND FILTER
# ========================================
st.subheader("Current Volunteers")
search = st.text_input("Search by name")

# ========================================
# VOLUNTEER TABLE
# ========================================
try:
    conn = get_connection()
    cur = conn.cursor()

    if search.strip():
        cur.execute("""
            SELECT id, first_name, last_name, email, phone, age, field_of_study
            FROM volunteers
            WHERE first_name ILIKE %s OR last_name ILIKE %s
            ORDER BY last_name;
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("""
            SELECT id, first_name, last_name, email, phone, age, field_of_study
            FROM volunteers
            ORDER BY last_name;
        """)

    volunteers = cur.fetchall()
    cur.close()
    conn.close()

    if not volunteers:
        st.info("No volunteers found.")
    else:
        for v in volunteers:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                field = f" | Field of Study: {v[6]}" if v[6] else ""
                st.writ
