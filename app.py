import os
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from config import init_db, mysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Initialize MySQL
init_db(app)

# Secret Key
import os

app.secret_key = os.getenv("SECRET_KEY", "sers123")


# =====================================
# Home Page
# =====================================
@app.route("/")
def home():
    return render_template("index.html")


# =====================================
# Register
# =====================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        # Check Email
        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()

        if user:
            cur.close()
            flash("Email already registered!", "danger")
            return redirect("/register")

        # Insert User
        cur.execute(
    """
    INSERT INTO users(full_name,email,password)
    VALUES(%s,%s,%s)
    """,
    (name, email, hashed_password)
)
        

        mysql.connection.commit()
        cur.close()

        flash("Registration Successful! Please Login.", "success")
        return redirect("/login")

    return render_template("register.html")
## =====================================
# Login
# =====================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        # Get user by email
        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()

        cur.close()

        if user and check_password_hash(user[3], password):

            session["user_id"] = user[0]
            session["user"] = user[1]
            session["email"] = user[2]

            flash("Login Successful!", "success")

            return redirect("/dashboard")

        else:

            flash("Invalid Email or Password!", "danger")

            return redirect("/login")

    return render_template("login.html")
# =====================================
# Dashboard
# =====================================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    cur = mysql.connection.cursor()

    # Total Reports
    cur.execute("SELECT COUNT(*) FROM reports")
    total_reports = cur.fetchone()[0]

    # Pending Reports
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='Pending'")
    pending_reports = cur.fetchone()[0]

    # Resolved Reports
    cur.execute("SELECT COUNT(*) FROM reports WHERE status='Resolved'")
    resolved_reports = cur.fetchone()[0]

    # Recent Reports
    cur.execute("""
        SELECT id, full_name, emergency_type, status
        FROM reports
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_reports = cur.fetchall()

    cur.close()

    return render_template(
        "dashboard.html",
        total_reports=total_reports,
        pending_reports=pending_reports,
        resolved_reports=resolved_reports,
        username=session.get("user"),
        recent_reports=recent_reports)
  # =====================================
# Report Emergency
# =====================================
@app.route("/report", methods=["GET", "POST"])
def report():

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        emergency_type = request.form["emergency_type"]
        priority = request.form["priority"]
        location = request.form["location"]
        description = request.form["description"]

        cur = mysql.connection.cursor()

        # Get Last Report ID
        cur.execute("SELECT id FROM reports ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()

        if last:
            next_id = last[0] + 1
        else:
            next_id = 1

        # Generate Report ID
        report_id = f"SERS-2026-{next_id:05d}"

        # Insert Report
        cur.execute("""
            INSERT INTO reports
            (report_id, full_name, mobile, emergency_type,
             priority, location, description, status)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            report_id,
            name,
            mobile,
            emergency_type,
            priority,
            location,
            description,
            "Pending"
        ))

        mysql.connection.commit()
        cur.close()

        flash(f"Report Submitted Successfully! ID: {report_id}", "success")
        return redirect("/my_reports")

    return render_template(
        "report.html",
        username=session.get("user")
    )


# =====================================
# My Reports
# =====================================
@app.route("/my_reports")
def my_reports():

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM reports
        WHERE full_name=%s
        ORDER BY id DESC
    """, (session["user"],))

    reports = cur.fetchall()

    cur.close()

    return render_template(
        "my_reports.html",
        reports=reports
    ) 
# =====================================
# Track Report
# =====================================
@app.route("/track_report", methods=["GET", "POST"])
def track_report():

    report = None

    if request.method == "POST":

        report_id = request.form["report_id"]

        cur = mysql.connection.cursor()

        cur.execute(
    """
    SELECT * FROM reports
    WHERE report_id = %s
    """,
    (report_id,)
)

        report = cur.fetchone()

        cur.close()

    return render_template(
        "track_report.html",
        report=report
    )
# =====================================
# Analytics
# =====================================
@app.route("/analytics")
def analytics():

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM reports")
    total_reports = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM reports WHERE status='Pending'"
    )
    pending_reports = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM reports WHERE status='Resolved'"
    )
    resolved_reports = cur.fetchone()[0]

    cur.close()

    return render_template(
        "analytics.html",
        total_reports=total_reports,
        pending_reports=pending_reports,
        resolved_reports=resolved_reports
    )
# =====================================
# Users List
# =====================================
@app.route("/users")
def users():

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id, full_name, email
        FROM users
    """)

    users = cur.fetchall()

    cur.close()

    return render_template(
        "users.html",
        users=users
    )
    
# =====================================
# Admin Reports
# =====================================
@app.route("/admin_reports")
def admin_reports():

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    search = request.args.get("search")

    cur = mysql.connection.cursor()

    if search:
        cur.execute(
            "SELECT * FROM reports WHERE full_name LIKE %s",
            ("%" + search + "%",)
        )
    else:
        cur.execute(
            "SELECT * FROM reports ORDER BY id DESC"
        )

    reports = cur.fetchall()

    cur.close()

    return render_template(
        "admin_reports.html",
        reports=reports
    )


# =====================================
# Update Report Status
# =====================================
@app.route("/update_status/<int:id>")
def update_status(id):

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE reports SET status='Resolved' WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    flash("Report Status Updated Successfully!", "success")

    return redirect("/admin_reports")


# =====================================
# Delete Report
# =====================================
@app.route("/delete_report/<int:id>")
def delete_report(id):

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM reports WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    flash("Report Deleted Successfully!", "success")

    return redirect("/admin_reports")


# =====================================
# =====================================
# Logout
# =====================================
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully!", "success")

    return redirect("/login")
# =====================================
# API Home
# =====================================
@app.route("/api")
def api_home():

    return jsonify({
        "project": "Smart Emergency Response System",
        "version": "1.0",
        "status": "Running"
    })


# =====================================
# Forgot Password
# =====================================
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Password Hash
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        # Check Email
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user:

            cur.execute(
                "UPDATE users SET password=%s WHERE email=%s",
                (hashed_password, email)
            )

            mysql.connection.commit()

            flash("Password Updated Successfully!", "success")

            cur.close()

            return redirect("/login")

        else:

            flash("Email Not Found!", "danger")

            cur.close()

    return render_template("forgot_password.html")
# =====================================
# API - All Reports
# =====================================
@app.route("/api/reports")
def api_reports():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id, report_id, full_name, emergency_type,
               priority, location, status, created_at
        FROM reports
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()

    reports = []

    for row in rows:
        reports.append({
            "id": row[0],
            "report_id": row[1],
            "full_name": row[2],
            "emergency_type": row[3],
            "priority": row[4],
            "location": row[5],
            "status": row[6],
            "created_at": str(row[7])
        })

    return jsonify(reports)


# =====================================
# Run Server
# =====================================
if __name__ == "__main__":
    app.run(debug=True)