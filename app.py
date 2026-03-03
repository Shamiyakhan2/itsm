import streamlit as st
import sqlite3
from datetime import datetime
from passlib.hash import pbkdf2_sha256
# ---------------- DATABASE CONNECTION ----------------
conn = sqlite3.connect('itsm.db', check_same_thread=False)
c = conn.cursor()

# Create Tables
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_name TEXT,
                asset_type TEXT,
                assigned_to TEXT)''')

conn.commit()

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- UI TITLE ----------------
st.title("💻 CloudDesk - IT Service Management System")

# ---------------- SIDEBAR MENU ----------------
menu = ["Login", "Sign Up", "Create Ticket", "View Tickets", "Manage Assets", "Logout"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- LOGIN ----------------
if choice == "Login":
    st.subheader("User Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {username} 🎉")
        else:
            st.error("Invalid Credentials")

# ---------------- SIGN UP ----------------
elif choice == "Sign Up":
    st.subheader("Create New Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_pass))
            conn.commit()
            st.success("Account Created Successfully! Please Login.")
        except:
            st.error("Username already exists")

# ---------------- CREATE TICKET ----------------
elif choice == "Create Ticket":

    if not st.session_state.logged_in:
        st.warning("Please login first")
        st.stop()

    st.subheader("Create New Ticket")

    title = st.text_input("Title")
    description = st.text_area("Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

    if st.button("Submit Ticket"):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""INSERT INTO tickets 
                     (title, description, priority, status, created_at) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (title, description, priority, "Open", created_at))

        conn.commit()
        st.success("Ticket Created Successfully")

# ---------------- VIEW TICKETS ----------------
elif choice == "View Tickets":

    if not st.session_state.logged_in:
        st.warning("Please login first")
        st.stop()

    st.subheader("All Tickets")

    c.execute("SELECT * FROM tickets")
    tickets = c.fetchall()

    if tickets:
        for ticket in tickets:
            st.markdown("---")
            st.write(f"**Ticket ID:** {ticket[0]}")
            st.write(f"**Title:** {ticket[1]}")
            st.write(f"**Description:** {ticket[2]}")
            st.write(f"**Priority:** {ticket[3]}")
            st.write(f"**Status:** {ticket[4]}")
            st.write(f"**Created At:** {ticket[5]}")

            new_status = st.selectbox(
                f"Update Status for Ticket {ticket[0]}",
                ["Open", "In Progress", "Resolved"],
                key=f"status_{ticket[0]}"
            )

            if st.button(f"Update Ticket {ticket[0]}"):
                c.execute("UPDATE tickets SET status=? WHERE id=?", (new_status, ticket[0]))
                conn.commit()
                st.success("Status Updated")
    else:
        st.info("No tickets available")

# ---------------- MANAGE ASSETS ----------------
elif choice == "Manage Assets":

    if not st.session_state.logged_in:
        st.warning("Please login first")
        st.stop()

    st.subheader("Add IT Asset")

    asset_name = st.text_input("Asset Name")
    asset_type = st.text_input("Asset Type")
    assigned_to = st.text_input("Assigned To")

    if st.button("Add Asset"):
        c.execute("""INSERT INTO assets 
                     (asset_name, asset_type, assigned_to) 
                     VALUES (?, ?, ?)""",
                  (asset_name, asset_type, assigned_to))
        conn.commit()
        st.success("Asset Added Successfully")

    st.subheader("All Assets")

    c.execute("SELECT * FROM assets")
    assets = c.fetchall()

    if assets:
        for asset in assets:
            st.write(f"Asset: {asset[1]} | Type: {asset[2]} | Assigned To: {asset[3]}")
    else:
        st.info("No assets available")

# ---------------- LOGOUT ----------------
elif choice == "Logout":

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Logged Out Successfully")