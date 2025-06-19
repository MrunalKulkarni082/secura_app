import streamlit as st
import mysql.connector
import bcrypt

# ---------- MYSQL CONFIGURATION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",          # or your remote DB host
        user="root",               # change if different
        password="Mru2003@",  # use your MySQL password
        database="secura_db"       # create this database before running
    )

# ---------- DATABASE SETUP ----------
def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            phone VARCHAR(20),
            email VARCHAR(255) UNIQUE,
            password_hash BLOB
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            contact_name VARCHAR(255),
            contact_phone VARCHAR(20),
            contact_email VARCHAR(255),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_user(name, phone, email, password_hash):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (name, phone, email, password_hash)
        VALUES (%s, %s, %s, %s)
    ''', (name, phone, email, password_hash))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def insert_emergency_contacts(user_id, contacts):
    conn = get_connection()
    c = conn.cursor()
    for contact in contacts:
        c.execute('''
            INSERT INTO emergency_contacts (user_id, contact_name, contact_phone, contact_email)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, contact["name"], contact["phone"], contact["email"]))
    conn.commit()
    conn.close()

def verify_login(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE email=%s", (email,))
    user = c.fetchone()
    conn.close()
    if user:
        user_id, password_hash = user
        if isinstance(password_hash, str):
            password_hash = password_hash.encode()
        if bcrypt.checkpw(password.encode(), password_hash):
            return user_id
    return None

def get_user_info(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name, phone, email FROM users WHERE id=%s", (user_id,))
    user = c.fetchone()
    c.execute("SELECT contact_name, contact_phone, contact_email FROM emergency_contacts WHERE user_id=%s", (user_id,))
    contacts = c.fetchall()
    conn.close()
    return user, contacts

# ---------- UI FLOW ----------
st.set_page_config(page_title="SECURA", layout="centered")
st.sidebar.title("🔐 SECURA")
page = st.sidebar.radio("Go to", ["Login", "Register"])

create_tables()

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------- LOGIN PAGE ----------
if page == "Login":
    st.title("🔑 Login to Your Account")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id = verify_login(login_email, login_password)
        if user_id:
            st.session_state.user_id = user_id
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid email or password.")

    if st.session_state.user_id:
        user, contacts = get_user_info(st.session_state.user_id)
        st.subheader("👤 Your Details")
        st.write(f"**Name:** {user[0]}")
        st.write(f"**Phone:** {user[1]}")
        st.write(f"**Email:** {user[2]}")

        st.subheader("📇 Emergency Contacts")
        for i, c in enumerate(contacts, 1):
            st.write(f"**Contact {i}:** {c[0]} | {c[1]} | {c[2]}")

        if st.button("Logout"):
            st.session_state.user_id = None
            st.experimental_rerun()

# ---------- REGISTER PAGE ----------
elif page == "Register":
    st.title("📝 Create Your SECURA Account")

    st.subheader("👤 Your Details")
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")

    st.subheader("🔑 Create Password")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    st.subheader("📇 Emergency Contacts")
    contact_count = st.number_input("How many emergency contacts?", min_value=1, max_value=5, step=1)
    contacts = []
    for i in range(contact_count):
        st.markdown(f"**Contact {i+1}**")
        c_name = st.text_input(f"Name {i+1}", key=f"name_{i}")
        c_phone = st.text_input(f"Phone {i+1}", key=f"phone_{i}")
        c_email = st.text_input(f"Email {i+1}", key=f"email_{i}")
        contacts.append({"name": c_name, "phone": c_phone, "email": c_email})

    if st.button("Register"):
        if not (name and phone and email and password and confirm_password):
            st.error("🚫 Please fill in all personal fields.")
        elif password != confirm_password:
            st.error("🚫 Passwords do not match.")
        elif any(not c["name"] or not c["phone"] or not c["email"] for c in contacts):
            st.error("🚫 Please fill in all emergency contact fields.")
        else:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            user_id = insert_user(name, phone, email, password_hash)
            insert_emergency_contacts(user_id, contacts)
            st.success("✅ Registration successful! You can now log in.")
