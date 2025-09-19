from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

template_path = os.path.join(os.getcwd(), "templates")
print("Using template folder:", template_path)
print("Templates contents:", os.listdir(template_path))

app = Flask(__name__, template_folder=template_path)

app.secret_key = "your_secret_key"  # for sessions

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# Database setup
def init_db():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Home route
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

# Static routes for pages
@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/contact.html")
def contact():
    return render_template("contact.html")

@app.route("/sports.html")
def sports():
    return render_template("sports.html")

@app.route("/technology.html")
def technology():
    return render_template("technology.html")

@app.route("/politics.html")
def politics():
    return render_template("politics.html")

# Register
@app.route("/register.html", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except:
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")

# Login
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "danger")

    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
