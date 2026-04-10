# KBI Volunteer Tracker

A Streamlit web application backed by a PostgreSQL database that tracks
volunteer participation at the Kino Border Initiative (KBI), a humanitarian
aid organization operating across two locations: Nogales, Arizona and
Nogales, Sonora, Mexico. Staff members can register volunteers, manage
aid programs, and track volunteer assignments including roles, dates of
service, and hours contributed.

---

## Live App

[Click here to view the live app](https://kbi-volunteer-tracker-6tmhpkjejqsnafbzexqqvn.streamlit.app/)

---

## ERD

![ERD](erd.png)

---

## Table Descriptions

### volunteers
Stores information about each volunteer including their name, contact
information, age, and optional field of study. If a volunteer has a
field of study they may be matched to specialized programs that align
with their professional goals.

### programs
Stores information about the aid programs KBI offers at each location.
Each program is categorized as either General or Specialized and is
associated with a coordinator name and optional description.

### volunteer_assignments
The junction table that connects volunteers to programs. Each row
represents one volunteer assigned to one program and includes their
role, start date, optional end date, and total hours served.

---

## How to Run Locally

1. Clone this repository:
   git clone https://github.com/YOUR_USERNAME/kbi-volunteer-tracker.git

2. Install dependencies:
   pip install streamlit psycopg2-binary

3. Create a secrets file:
   mkdir .streamlit
   Add a file called secrets.toml inside the .streamlit folder with:
   DB_URL = "your_postgresql_connection_string_here"

4. Run the app:
   streamlit run streamlit_app.py
