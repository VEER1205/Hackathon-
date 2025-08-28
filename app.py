from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"   # required for sessions

# ---------- DATABASE SETUP ----------
DB_NAME = "advisor.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_class TEXT,
                interest TEXT,
                skills TEXT,
                stream TEXT,
                career TEXT
            )
        """)
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/roadmap", methods=["GET", "POST"])
def roadmap():
    if request.method == "POST":
        # get form data
        student_class = request.form.get("class")
        interest = request.form.get("interest")
        skills = request.form.get("skills")
        stream = request.form.get("stream")
        career = request.form.get("career")

        # save to DB
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO responses (student_class, interest, skills, stream, career)
                VALUES (?, ?, ?, ?, ?)
            """, (student_class, interest, skills, stream, career))
            conn.commit()

        # after saving, go to roadmap.html
        return render_template("roadmap.html")

    return render_template("roadmap.html")

# ---------- ADMIN ONLY ----------
@app.route("/admin")
def admin():
    # check if logged in
    if not session.get("is_admin"):
        return "Access Denied! Only admin can view this page.", 403

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM responses")
        data = c.fetchall()
    return render_template("admin.html", data=data)

# ---------- SIMPLE LOGIN FOR ADMIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # simple check (replace with secure method later)
        if username == "admin" and password == "admin123":
            session["is_admin"] = True
            return redirect(url_for("admin"))
        else:
            return "Invalid credentials!"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
