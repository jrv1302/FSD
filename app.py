import os
import sys
import json
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
import sqlite3
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

app = Flask(__name__)
app.secret_key = "fc-secret-key-2026-change-in-prod"

DB_PATH = os.path.join(BASE_DIR, "complaints.db")

from model.predict import predict as ml_predict

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users (name, email, password)
        VALUES (?, ?, ?)
    """, ("Admin", "admin@fincomplaints.com", admin_pw))

    conn.commit()
    conn.close()


def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or not session.get("is_admin"):
            flash("Admin access required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw    = request.form.get("password", "")
        pw2   = request.form.get("confirm_password", "")

        if not all([name, email, pw, pw2]):
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if pw != pw2:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(pw) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("Email already registered. Please log in.", "warning")
            return render_template("register.html")

        conn.execute("INSERT INTO users (name, email, password) VALUES (?,?,?)",
                     (name, email, hash_pw(pw)))
        conn.commit()
        conn.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pw    = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, hash_pw(pw))
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"] = (email == "admin@fincomplaints.com")
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard") if session["is_admin"] else url_for("submit"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        desc  = request.form.get("description", "").strip()

        if not title or not desc:
            flash("Both title and description are required.", "danger")
            return render_template("submit.html")

        result = ml_predict(desc)

        conn = get_db()
        conn.execute(
            "INSERT INTO complaints (user_id, title, description, category, confidence) VALUES (?,?,?,?,?)",
            (session["user_id"], title, desc, result["category"], result["confidence"])
        )
        conn.commit()
        complaint_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()

        session["last_result"] = {
            "id": complaint_id,
            "title": title,
            "description": desc,
            "category": result["category"],
            "confidence": result["confidence"],
            "scores": result["scores"],
        }
        return redirect(url_for("success"))

    return render_template("submit.html")

@app.route("/success")
@login_required
def success():
    result = session.pop("last_result", None)
    if not result:
        return redirect(url_for("submit"))
    return render_template("success.html", result=result)

@app.route("/my-complaints")
@login_required
def my_complaints():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM complaints WHERE user_id=? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("my_complaints.html", complaints=rows)

@app.route("/dashboard")
@admin_required
def dashboard():
    conn = get_db()

    complaints = conn.execute("""
        SELECT c.*, u.name as user_name, u.email as user_email
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    """).fetchall()

    # Analytics
    cat_counts = {}
    status_counts = {"Pending": 0, "Resolved": 0}
    for row in complaints:
        cat = row["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE email != 'admin@fincomplaints.com'").fetchone()[0]
    conn.close()

    return render_template("dashboard.html",
                           complaints=complaints,
                           cat_counts=json.dumps(cat_counts),
                           status_counts=json.dumps(status_counts),
                           total_users=total_users,
                           total_complaints=len(complaints))

@app.route("/update-status", methods=["POST"])
@admin_required
def update_status():
    complaint_id = request.form.get("complaint_id")
    new_status   = request.form.get("status")
    if complaint_id and new_status in ("Pending", "Resolved"):
        conn = get_db()
        conn.execute("UPDATE complaints SET status=? WHERE id=?", (new_status, complaint_id))
        conn.commit()
        conn.close()
        flash("Status updated.", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
else:
    init_db()