import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Programs", page_icon="📋")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📋 Manage Programs")

# ========================================
# ADD PROGRAM FORM
# ========================================
st.subheader("Add a New Program")

with st.form("add_program_form"):
    program_name = st.text_input("Program Name *")
    program_type = st.selectbox("Program Type *", options=["General", "Specialized"])
    location = st.selectbox("Location *", options=["Nogales, AZ", "Nogales, Sonora"])
    coordinator_name = st.text_input("Coordinator Name *")
    description = st.text_area("Description (optional)")

    submitted = st.form_submit_button("Add Program")

    if submitted:
        errors = []

        if not program_name.strip():
            errors.append("Program name is required.")
        if not coordinator_name.strip():
            errors.append("Coordinator name is required.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO programs
                    (program_name, program_type, location, coordinator_name, description)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    program_name.strip(),
                    program_type,
                    location,
                    coordinator_name.strip(),
                    description.strip() or None
                ))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"Program '{program_name}' added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error("A program with that name already exists.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ========================================
# PROGRAMS TABLE
# ========================================
st.subheader("Current Programs")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, program_name, program_type, location, coordinator_name, description
        FROM programs
        ORDER BY program_name;
    """)
    programs = cur.fetchall()
    cur.close()
    conn.close()

    if not programs:
        st.info("No programs yet. Add a program above to get started!")
    else:
        for p in programs:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                desc = f" | {p[5]}" if p[5] else ""
                st.write(f"**{p[1]}** | {p[2]} | {p[3]} | Coordinator: {p[4]}{desc}")
            with col2:
                if st.button("Edit", key=f"edit_{p[0]}"):
                    st.session_state["editing_program"] = p[0]
            with col3:
                if st.button("Delete", key=f"delete_{p[0]}"):
                    st.session_state["deleting_program"] = p[0]

except Exception as e:
    st.error(f"Error loading programs: {e}")

# ========================================
# DELETE CONFIRMATION
# ========================================
if "deleting_program" in st.session_state:
    pid = st.session_state["deleting_program"]
    st.warning("Are you sure you want to delete this program? This will also remove all associated assignments.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, delete"):
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM programs WHERE id = %s;", (pid,))
                conn.commit()
                cur.close()
                conn.close()
                del st.session_state["deleting_program"]
                st.success("Program deleted successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    with col2:
        if st.button("Cancel"):
            del st.session_state["deleting_program"]
            st.rerun()

# ========================================
# EDIT FORM
# ========================================
if "editing_program" in st.session_state:
    pid = st.session_state["editing_program"]
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT program_name, program_type, location, coordinator_name, description
            FROM programs WHERE id = %s;
        """, (pid,))
        p = cur.fetchone()
        cur.close()
        conn.close()

        if p:
            st.markdown("---")
            st.subheader("Edit Program")
            with st.form("edit_program_form"):
                new_name = st.text_input("Program Name *", value=p[0])
                new_type = st.selectbox(
                    "Program Type *",
                    options=["General", "Specialized"],
                    index=["General", "Specialized"].index(p[1])
                )
                new_location = st.selectbox(
                    "Location *",
                    options=["Nogales, AZ", "Nogales, Sonora"],
                    index=["Nogales, AZ", "Nogales, Sonora"].index(p[2])
                )
                new_coordinator = st.text_input("Coordinator Name *", value=p[3])
                new_description = st.text_area("Description (optional)", value=p[4] or "")

                col1, col2 = st.columns(2)
                with col1:
                    save = st.form_submit_button("Save Changes")
                with col2:
                    cancel = st.form_submit_button("Cancel")

                if save:
                    errors = []

                    if not new_name.strip():
                        errors.append("Program name is required.")
                    if not new_coordinator.strip():
                        errors.append("Coordinator name is required.")

                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("""
                                UPDATE programs
                                SET program_name=%s, program_type=%s, location=%s,
                                    coordinator_name=%s, description=%s
                                WHERE id=%s;
                            """, (
                                new_name.strip(),
                                new_type,
                                new_location,
                                new_coordinator.strip(),
                                new_description.strip() or None,
                                pid
                            ))
                            conn.commit()
                            cur.close()
                            conn.close()
                            del st.session_state["editing_program"]
                            st.success("Program updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

                if cancel:
                    del st.session_state["editing_program"]
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading program: {e}")
