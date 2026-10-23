import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "helpdesk-secret-key-12345")
DB_PATH = os.path.join(os.path.dirname(__file__), "helpdesk.db")

CATEGORIES = ["Hardware", "Software", "Network", "Account"]
PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Open", "In Progress", "Resolved"]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Auto-create the table on startup
init_db()

@app.route("/")
def dashboard():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) AS c FROM tickets").fetchone()["c"]
    counts = {s: 0 for s in STATUSES}
    for row in conn.execute("SELECT status, COUNT(*) AS c FROM tickets GROUP BY status").fetchall():
        if row["status"] in counts:
            counts[row["status"]] = row["c"]
    conn.close()
    return render_template("dashboard.html", total=total, counts=counts)

@app.route("/create", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category")
        priority = request.form.get("priority")

        if not title or not description or category not in CATEGORIES or priority not in PRIORITIES:
            flash("Please fill in all fields correctly.", "danger")
            return render_template("create_ticket.html", categories=CATEGORIES, priorities=PRIORITIES, form=request.form)

        conn = get_db()
        conn.execute(
            "INSERT INTO tickets (title, description, category, priority, status) VALUES (?, ?, ?, ?, 'Open')",
            (title, description, category, priority)
        )
        conn.commit()
        conn.close()
        flash("Ticket created successfully!", "success")
        return redirect(url_for("tickets"))

    return render_template("create_ticket.html", categories=CATEGORIES, priorities=PRIORITIES, form={})

@app.route("/tickets")
def tickets():
    search = request.args.get("search", "").strip()
    sel_priority = request.args.get("priority", "")
    sel_status = request.args.get("status", "")

    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    if sel_priority in PRIORITIES:
        query += " AND priority = ?"
        params.append(sel_priority)
    if sel_status in STATUSES:
        query += " AND status = ?"
        params.append(sel_status)

    query += " ORDER BY id DESC"

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    
    ticket_list = []
    for r in rows:
        t = dict(r)
        try:
            t["created_at"] = datetime.strptime(str(t["created_at"])[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            t["created_at"] = datetime.now()
        ticket_list.append(t)
    conn.close()

    return render_template(
        "tickets.html",
        tickets=ticket_list,
        priorities=PRIORITIES,
        statuses=STATUSES,
        search=search,
        sel_priority=sel_priority,
        sel_status=sel_status
    )

@app.route("/ticket/<int:ticket_id>/status", methods=["POST"])
def update_status(ticket_id):
    new_status = request.form.get("status")
    if new_status in STATUSES:
        conn = get_db()
        conn.execute("UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, ticket_id))
        conn.commit()
        conn.close()
        flash("Status updated.", "success")
    return redirect(url_for("tickets"))

if __name__ == "__main__":
    app.run(debug=True)
