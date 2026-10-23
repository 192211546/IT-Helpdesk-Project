import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # reads the .env file

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-key")

CATEGORIES = ["Hardware", "Software", "Network"]
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Open", "In Progress", "Resolved"]


def get_db():
    """Open a new connection to MySQL using values from .env."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "it_helpdesk"),
    )


def query(sql, params=(), fetch=True):
    """Run a parameterized query. Returns rows (as dicts) or None."""
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
    finally:
        conn.close()


@app.route("/")
def dashboard():
    try:
        rows = query("SELECT status, COUNT(*) AS n FROM tickets GROUP BY status")
    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "error")
        rows = []
    counts = {s: 0 for s in STATUSES}
    for r in rows:
        counts[r["status"]] = r["n"]
    total = sum(counts.values())
    return render_template("dashboard.html", total=total, counts=counts)


@app.route("/create", methods=["GET", "POST"])
def create_ticket():
    form = {}
    if request.method == "POST":
        form = request.form
        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        category = form.get("category", "")
        priority = form.get("priority", "")

        errors = []
        if not title or len(title) > 150:
            errors.append("Title is required (max 150 characters).")
        if not description:
            errors.append("Description is required.")
        if category not in CATEGORIES:
            errors.append("Please choose a valid category.")
        if priority not in PRIORITIES:
            errors.append("Please choose a valid priority.")

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            try:
                query(
                    "INSERT INTO tickets (title, description, category, priority) "
                    "VALUES (%s, %s, %s, %s)",
                    (title, description, category, priority),
                    fetch=False,
                )
                flash("Ticket created successfully!", "success")
                return redirect(url_for("create_ticket"))
            except mysql.connector.Error as e:
                flash(f"Database error: {e}", "error")
    return render_template("create_ticket.html", categories=CATEGORIES,
                           priorities=PRIORITIES, form=form)


@app.route("/tickets")
def tickets():
    search = request.args.get("search", "").strip()
    priority = request.args.get("priority", "")
    status = request.args.get("status", "")

    sql = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if search:
        sql += " AND title LIKE %s"
        params.append(f"%{search}%")
    if priority in PRIORITIES:
        sql += " AND priority = %s"
        params.append(priority)
    if status in STATUSES:
        sql += " AND status = %s"
        params.append(status)
    sql += " ORDER BY created_at DESC"

    try:
        rows = query(sql, tuple(params))
    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "error")
        rows = []
    return render_template("tickets.html", tickets=rows, priorities=PRIORITIES,
                           statuses=STATUSES, search=search,
                           sel_priority=priority, sel_status=status)


@app.route("/tickets/<int:ticket_id>/status", methods=["POST"])
def update_status(ticket_id):
    new_status = request.form.get("status", "")
    if new_status not in STATUSES:
        flash("Invalid status.", "error")
    else:
        try:
            query("UPDATE tickets SET status = %s WHERE id = %s",
                  (new_status, ticket_id), fetch=False)
            flash(f"Ticket #{ticket_id} updated to {new_status}.", "success")
        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "error")
    return redirect(request.referrer or url_for("tickets"))


if __name__ == "__main__":
    app.run(debug=True)
