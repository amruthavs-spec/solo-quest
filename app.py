from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "solosafe_secret_key"

DATABASE = "solosafe.db"

# ---------------- DATABASE SETUP ----------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT UNIQUE,
                    password TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS trips(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    destination TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    accommodation TEXT,
                    transport TEXT,
                    notes TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS contacts(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    relation TEXT,
                    phone TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS checklist(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item TEXT,
                    status INTEGER
                )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- LOGIN / SIGNUP ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "signup":
            name = request.form["name"]
            email = request.form["email"]
            password = generate_password_hash(request.form["password"])

            try:
                c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                          (name, email, password))
                conn.commit()
                flash("Account created successfully!", "success")
            except:
                flash("Email already exists!", "danger")

        elif action == "login":
            email = request.form["email"]
            password = request.form["password"]

            c.execute("SELECT * FROM users WHERE email=?", (email,))
            user = c.fetchone()

            if user and check_password_hash(user[3], password):
                session["user_id"] = user[0]
                session["user_name"] = user[1]
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials!", "danger")

    conn.close()
    return render_template("login.html")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM trips WHERE user_id=? ORDER BY id DESC LIMIT 1",
              (session["user_id"],))
    trip = c.fetchone()

    c.execute("SELECT COUNT(*) FROM checklist WHERE user_id=? AND status=1",
              (session["user_id"],))
    completed = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM checklist WHERE user_id=?",
              (session["user_id"],))
    total = c.fetchone()[0]

    progress = int((completed / total) * 100) if total > 0 else 0

    conn.close()
    return render_template("dashboard.html", trip=trip, progress=progress)

# ---------------- PLANNER ----------------

@app.route("/planner", methods=["GET", "POST"])
def planner():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        destination = request.form["destination"]
        start = request.form["start_date"]
        end = request.form["end_date"]
        accommodation = request.form["accommodation"]
        transport = request.form["transport"]
        notes = request.form["notes"]

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute("""INSERT INTO trips 
                    (user_id,destination,start_date,end_date,accommodation,transport,notes)
                    VALUES (?,?,?,?,?,?,?)""",
                  (session["user_id"], destination, start, end,
                   accommodation, transport, notes))

        conn.commit()
        conn.close()

        flash("Trip saved successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("planner.html")



# ---------------- NEARBY ----------------
@app.route("/nearby")
def nearby():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("nearby.html")


# ---------------- SMART CHECKLIST ----------------
@app.route("/checklist", methods=["GET", "POST"])
def checklist():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Connect to database
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Define checklist items by category
    checklist_items = {
        "before_travel": [
            "Share trip details with family",
            "Save emergency contacts",
            "Check local laws",
            "Research local customs",
            "Check travel insurance"
        ],
        "during_travel": [
            "Keep phone charged",
            "Avoid isolated areas at night",
            "Stay hydrated and eat safely",
            "Use safe transportation options",
            "Track expenses"
        ],
        "at_destination": [
            "Verify accommodation",
            "Keep ID safe",
            "Know emergency exits",
            "Keep copies of important documents",
            "Follow local safety guidelines"
        ]
    }

    # Priority icons
    priorities = {
        "Share trip details with family": "🔴",
        "Save emergency contacts": "🔴",
        "Check local laws": "🟡",
        "Research local customs": "🟡",
        "Check travel insurance": "🟢",
        "Keep phone charged": "🔴",
        "Avoid isolated areas at night": "🔴",
        "Stay hydrated and eat safely": "🟡",
        "Use safe transportation options": "🟡",
        "Track expenses": "🟢",
        "Verify accommodation": "🔴",
        "Keep ID safe": "🔴",
        "Know emergency exits": "🟡",
        "Keep copies of important documents": "🟢",
        "Follow local safety guidelines": "🟡"
    }

    # Initialize notes dict
    notes = {"before": "", "during": "", "destination": ""}

    # Handle form submission
    if request.method == "POST":
        # Delete old checklist for user
        c.execute("DELETE FROM checklist WHERE user_id=?", (user_id,))
        conn.commit()

        # Save new checklist
        for category, items in checklist_items.items():
            for item in items:
                status = 1 if request.form.get(item) else 0
                c.execute(
                    "INSERT INTO checklist (user_id, item, status, category) VALUES (?,?,?,?)",
                    (user_id, item, status, category)
                )
        # Save notes
        notes["before"] = request.form.get("notes_before", "")
        notes["during"] = request.form.get("notes_during", "")
        notes["destination"] = request.form.get("notes_destination", "")
        flash("Checklist updated!", "success")
        conn.commit()

    # Fetch saved checklist for this user
    c.execute("SELECT item, status FROM checklist WHERE user_id=?", (user_id,))
    saved = dict(c.fetchall())

    conn.close()

    return render_template(
        "checklist.html",
        items=checklist_items,
        saved=saved,
        priorities=priorities,
        notes=notes
    )
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

DATABASE = "solosafe.db"

# ------------------ Emergency Contacts ------------------

@app.route("/emergency")
def emergency():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM emergency_contacts WHERE user_id=?", (session["user_id"],))
    contacts = c.fetchall()
    conn.close()

    return render_template("emergency.html", contacts=contacts)

# Add new emergency contact
@app.route("/add_contact", methods=["POST"])
def add_contact():
    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name")
    relationship = request.form.get("relationship")
    phone = request.form.get("phone")

    if not name or not phone:
        flash("Name and phone are required!", "error")
        return redirect(url_for("emergency"))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO emergency_contacts (user_id, name, relationship, phone)
        VALUES (?, ?, ?, ?)
    """, (session["user_id"], name, relationship, phone))
    conn.commit()
    conn.close()

    flash("Emergency contact added!", "success")
    return redirect(url_for("emergency"))
@app.route("/delete_contact/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Delete the contact that matches user_id and contact_id
    c.execute("DELETE FROM emergency_contacts WHERE id=? AND user_id=?", (contact_id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Contact deleted successfully!", "success")
    return redirect(url_for("emergency"))
    
@app.route("/award_badge/<badge_name>")
def award_badge(badge_name):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Check if user already has this badge
    c.execute("SELECT * FROM badges WHERE user_id=? AND badge_name=?", (session["user_id"], badge_name))
    exists = c.fetchone()

    if not exists:
        c.execute("INSERT INTO badges (user_id, badge_name) VALUES (?, ?)", (session["user_id"], badge_name))
        conn.commit()
    
    conn.close()
    return redirect(url_for("dashboard"))




    flash("Emergency contact added!", "success")
    return redirect(url_for("emergency"))






    



if __name__ == "__main__":
    app.run(debug=True)
