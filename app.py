import os
import pymysql
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash



def get_connection():
    return pymysql.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        port=4000,
        user="otDZndFBCN8S6vm.root",
        password="YAHA_APNA_NAYA_PASSWORD_DALO",
        database="sys",
        ssl_disabled=False,
        autocommit=True
    )


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "sers123")


# =====================================
# TiDB MySQL Connection
# =====================================
def get_connection():
    return pymysql.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        port=4000,
        user="otDZndFBCN8S6vm.root",
        password="28hKV4MIop0jIYVi",
        database="test",
        ssl={"ssl": {}},
        autocommit=True,
        cursorclass=pymysql.cursors.Cursor
    )


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

        conn = get_connection()
        cur = conn.cursor()

        # Check if email already exists
        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()

        if user:
            cur.close()
            conn.close()
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

        conn.commit()
        cur.close()
        conn.close()

        flash("Registration Successful! Please Login.", "success")
        return redirect("/login")

    return render_template("register.html")


# =====================================
# Login
# =====================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, full_name, email, password, role
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[3], password):

            print(user)

            session["user_id"] = user[0]
            session["user"] = user[1]
            session["email"] = user[2]
            session["role"] = user[4]

            print("ROLE =", session["role"])

            flash("Login Successful!", "success")
            return redirect("/dashboard")

        flash("Invalid Email or Password!", "danger")
        return redirect("/login")

    return render_template("login.html")
# =====================================
# Logout
# =====================================
@app.route("/logout")
def logout():

    session.clear()
    flash("Logged Out Successfully!", "success")

    return redirect("/login")
# =====================================
# Dashboard
# =====================================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    print("ROLE =", session.get("role"))

    conn = get_connection()
    cur = conn.cursor()

    # Total Reports
    cur.execute("SELECT COUNT(*) FROM reports")
    total_reports = cur.fetchone()[0]

    # Pending Reports
    cur.execute("SELECT COUNT(*) FROM reports WHERE status=%s", ("Pending",))
    pending_reports = cur.fetchone()[0]

    # Resolved Reports
    cur.execute("SELECT COUNT(*) FROM reports WHERE status=%s", ("Resolved",))
    resolved_reports = cur.fetchone()[0]

    # Recent Reports
    cur.execute("""
        SELECT report_id, full_name, emergency_type, status
        FROM reports
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_reports = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        username=session.get("user"),
        role=session.get("role"),
        total_reports=total_reports,
        pending_reports=pending_reports,
        resolved_reports=resolved_reports,
        recent_reports=recent_reports
    )


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

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM reports ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()

        next_id = last[0] + 1 if last else 1
        report_id = f"SERS-2026-{next_id:05d}"

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

        conn.commit()
        cur.close()
        conn.close()

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

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM reports
        WHERE full_name=%s
        ORDER BY id DESC
    """, (session["user"],))

    reports = cur.fetchall()

    cur.close()
    conn.close()

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

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM reports
            WHERE report_id=%s
        """, (report_id,))

        report = cur.fetchone()

        cur.close()
        conn.close()

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

    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM reports")
    total_reports = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM reports WHERE status=%s",
        ("Pending",)
    )
    pending_reports = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM reports WHERE status=%s",
        ("Resolved",)
    )
    resolved_reports = cur.fetchone()[0]

    cur.close()
    conn.close()

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

    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, full_name, email
        FROM users
        ORDER BY id DESC
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()

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

    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    # baaki code...

    try:
        search = request.args.get("search")

        conn = get_connection()
        cur = conn.cursor()

        if search:
            cur.execute("""
                SELECT *
                FROM reports
                WHERE full_name LIKE %s
                ORDER BY id DESC
            """, ("%" + search + "%",))
        else:
            cur.execute("""
                SELECT *
                FROM reports
                ORDER BY id DESC
            """)

        reports = cur.fetchall()

        cur.close()
        conn.close()

        return render_template("admin_reports.html", reports=reports)

    except Exception as e:
        return str(e)

# =====================================
# Update Report Status
# =====================================
@app.route("/update_status/<int:id>")
def update_status(id):

    if "user" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE reports
        SET status=%s
        WHERE id=%s
        """,
        ("Resolved", id)
    )

    conn.commit()

    cur.close()
    conn.close()

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

    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM reports
        WHERE id=%s
        """,
        (id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    flash("Report Deleted Successfully!", "success")

    return redirect("/admin_reports")
# =====================================
# Forgot Password
# =====================================
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()

        if user:

            cur.execute(
                "UPDATE users SET password=%s WHERE email=%s",
                (hashed_password, email)
            )

            conn.commit()

            cur.close()
            conn.close()

            flash("Password Updated Successfully!", "success")
            return redirect("/login")

        cur.close()
        conn.close()

        flash("Email Not Found!", "danger")

    return render_template("forgot_password.html")


# =====================================
# API Home
# =====================================
@app.route("/api")
def api_home():

    return jsonify({
        "project": "Smart Emergency Response System",
        "version": "2.0",
        "status": "Running"
    })


# =====================================
# API Reports
# =====================================
@app.route("/api/reports")
def api_reports():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,
               report_id,
               full_name,
               emergency_type,
               priority,
               location,
               status,
               created_at
        FROM reports
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

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