from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import os
import logging
import datetime

app = Flask(__name__)
app.secret_key = "htf-secret-2025"

logging.basicConfig(
    filename="/tmp/session_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", 5432),
        dbname=os.environ.get("DB_NAME", "fakebank"),
        user=os.environ.get("DB_USER", "bankuser"),
        password=os.environ.get("DB_PASS", "bankpass123")
    )

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        ip = request.remote_addr

        logging.info(f"LOGIN ATTEMPT | user={username} | ip={ip}")

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, full_name, role FROM employees WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["role"] = user[2]
            logging.info(f"LOGIN SUCCESS | user={username} | role={user[2]} | ip={ip}")
            return redirect("/dashboard")
        else:
            logging.warning(f"LOGIN FAILED | user={username} | ip={ip}")
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT account_number, balance FROM accounts LIMIT 10")
    accounts = cur.fetchall()
    conn.close()

    logging.info(f"DASHBOARD ACCESS | user={session['name']} | role={session['role']}")
    return render_template("dashboard.html", name=session["name"], accounts=accounts)

@app.route("/transactions")
def transactions():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.id, a.account_number, t.amount, t.txn_type, t.created_at
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        ORDER BY t.created_at DESC LIMIT 20
    """)
    txns = cur.fetchall()
    conn.close()

    logging.info(f"TRANSACTIONS ACCESS | user={session['name']}")
    return render_template("transactions.html", txns=txns)

@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/login")

    logging.info(f"ADMIN ACCESS ATTEMPT | user={session['name']} | role={session['role']}")

    if session["role"] != "admin":
        logging.warning(f"UNAUTHORIZED ADMIN ACCESS | user={session['name']}")
        return "Access Denied", 403

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, username, role FROM employees")
    employees = cur.fetchall()
    conn.close()

    return render_template("admin.html", employees=employees)

@app.route("/config")
def config():
    # This is the honeytoken endpoint
    # Any access here fires an alert
    ip = request.remote_addr
    user = session.get("name", "unknown")

    alert_msg = f"HONEYTOKEN TRIGGERED | user={user} | ip={ip} | time={datetime.datetime.now()}"
    logging.critical(alert_msg)

    # Write to a separate honeytoken alert file
    with open("/tmp/honeytoken_alert.txt", "a") as f:
        f.write(alert_msg + "\n")

    # Return fake config to keep attacker engaged
    return jsonify({
        "db_host": "10.0.0.5",
        "db_user": "root_backup",
        "db_pass": "Backup@Bank#2024",
        "api_key": "sk-live-xK9mP2nQrT8vW3jL",
        "admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    })

@app.route("/logout")
def logout():
    logging.info(f"LOGOUT | user={session.get('name', 'unknown')}")
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
