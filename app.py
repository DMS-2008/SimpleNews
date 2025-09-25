from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests

app = Flask(__name__)

app.secret_key = "your_secret_key"  # Change this for production

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# Weather API config
API_KEY = "f0addff8ded1c7d4f5cc71579de53b4b"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# ----------------- Database Setup ----------------- #
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ----------------- Breaking News ----------------- #
breaking_news_list = [
    {
        "title": "Major Election Update: Results Rolling In",
        "description": "Leaders react as votes are counted. Stay tuned for live coverage and instant analysis."
    },
    {
        "title": "Stock Markets Surge Amid Global Optimism",
        "description": "Investors celebrate strong earnings reports. Markets on the rise."
    },
    {
        "title": "Weather Alert: Heavy Rain Expected in City Center",
        "description": "Authorities advise caution and monitor flooding risks."
    },
    {
        "title": "Tech Giant Launches New AI Tool",
        "description": "The latest AI innovation promises to change the way we work."
    }
]

# ----------------- Routes ----------------- #

# Home page with weather form and breaking news
@app.route("/", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def home():
    # Show the first breaking news item by default
    news_title = breaking_news_list[2]["title"]
    news_description = breaking_news_list[2]["description"]

    if request.method == "POST":
        city = request.form.get("city")
        url = f"{BASE_URL}q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") == 200:
            weather = {
                "city": city,
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"]
            }
            return render_template(
                "result.html",
                weather=weather,
                news_title=news_title,
                news_description=news_description
            )
        else:
            return render_template(
                "result.html",
                weather=None,
                error="City not found!",
                news_title=news_title,
                news_description=news_description
            )

    return render_template(
        "index.html",
        news_title=news_title,
        news_description=news_description
    )

# Static pages
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

# ----------------- Authentication ----------------- #

# Register
@app.route("/register.html", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["regEmail"]
        password = request.form["regPassword"]
        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, hashed_password)
            )
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")

# Login
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["loginEmail"]
        password = request.form["loginPassword"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = email
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# ----------------- Run App ----------------- #
if __name__ == "__main__":
    app.run(debug=True)
