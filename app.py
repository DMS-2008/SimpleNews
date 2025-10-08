from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import time

app = Flask(__name__)

app.secret_key = "your_secret_key"  # Change this for production

# ----------------- Database Path ----------------- #
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# ----------------- Weather API Config ----------------- #
WEATHER_API_KEY = "f0addff8ded1c7d4f5cc71579de53b4b"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# ----------------- News API Config ----------------- #
# Mani key pub_2699a35e03554ae79ac614e85f8400d8
# mohan key pub_915ed70053cb4adfb5ceb7ed12ffa0ce
NEWS_API_KEY = "pub_915ed70053cb4adfb5ceb7ed12ffa0ce" 
NEWS_URL = f"https://newsdata.io/api/1/latest?apikey={NEWS_API_KEY}&q=latest%20news"

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

# ----------------- Cache Setup ----------------- #
news_cache = {
    "data": [],
    "timestamp": 0
}
CACHE_DURATION = 15 * 60  # 15 minutes in seconds

# ----------------- Routes ----------------- #

@app.route("/", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form.get("city")
        url = f"{BASE_URL}q={city}&appid={WEATHER_API_KEY}&units=metric"
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
            return render_template("result.html", weather=weather)
        else:
            return render_template("result.html", weather=None, error="City not found!")

    return render_template("index.html")


# ✅ Endpoint to fetch latest breaking news with caching
@app.route("/get_news")
def get_news():
    global news_cache

    category = request.args.get("category", "latest")  # default to latest news
    current_time = time.time()
    
    # Check cache
    if news_cache.get(category) and (current_time - news_cache[category]["timestamp"] < CACHE_DURATION):
        return jsonify({"news": news_cache[category]["data"]})

    try:
        url = f"https://newsdata.io/api/1/latest?apikey={NEWS_API_KEY}&q={category}"
        response = requests.get(url)
        news_data = response.json()
        articles = news_data.get("results", []) or news_data.get("articles", [])
        news_list = [{
            "title": article.get("title", "No Title"),
            "description": article.get("description", ""),
            "image": article.get("image_url", "")
        } for article in articles]

        # Cache per category
        news_cache[category] = {
            "data": news_list,
            "timestamp": current_time
        }

        return jsonify({"news": news_list})
    except Exception as e:
        return jsonify({"news": [{"title": "Error fetching news", "description": str(e)}]})



# ----------------- Static Pages ----------------- #
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

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# ----------------- Run App ----------------- #
if __name__ == "__main__":
    app.run(debug=True)
