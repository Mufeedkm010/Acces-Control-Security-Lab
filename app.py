
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, jsonify
)
from werkzeug.security import check_password_hash
from database import get_db, initialize_database
from functools import wraps

app = Flask(__name__)
app.secret_key = "local-lab-secret-key-change-this"

# Authentication decorator
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


# Home
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):

            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid username or password")

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# User Dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    with get_db() as conn:
        invoices = conn.execute(
            "SELECT * FROM invoices WHERE owner_id = ?",
            (session["user_id"],)
        ).fetchall()

    return render_template(
        "dashboard.html",
        invoices=invoices
    )


# IDOR VULNERABILITY
@app.route("/invoice/<int:invoice_id>")
@login_required
def view_invoice(invoice_id):

    # INTENTIONALLY VULNERABLE:
    # Missing invoice ownership verification.

    with get_db() as conn:
        invoice = conn.execute(
            "SELECT * FROM invoices WHERE id = ?",
            (invoice_id,)
        ).fetchone()

    if invoice is None:
        return "Invoice not found", 404

    return render_template(
        "invoice.html",
        invoice=invoice
    )


# IDOR API VULNERABILITY
@app.route("/api/invoices/<int:invoice_id>")
@login_required
def invoice_api(invoice_id):

    # INTENTIONALLY VULNERABLE:
    # Does not verify invoice ownership.

    with get_db() as conn:
        invoice = conn.execute(
            "SELECT * FROM invoices WHERE id = ?",
            (invoice_id,)
        ).fetchone()

    if invoice is None:
        return jsonify({"error": "Invoice not found"}), 404

    return jsonify(dict(invoice))


# BROKEN ACCESS CONTROL
@app.route("/admin")
@login_required
def admin():

    # INTENTIONALLY VULNERABLE:
    # Does not check whether the user has the admin role.

    with get_db() as conn:
        users = conn.execute(
            "SELECT id, username, role FROM users"
        ).fetchall()

    return render_template(
        "admin.html",
        users=users
    )


# Admin API
@app.route("/admin/api/users")
@login_required
def admin_api():

    # INTENTIONALLY VULNERABLE:
    # Missing server-side role authorization.

    with get_db() as conn:
        users = conn.execute(
            "SELECT id, username, role FROM users"
        ).fetchall()

    return jsonify([dict(user) for user in users])


if __name__ == "__main__":
    initialize_database()

    print("Access Control Lab running")
    print("Open: http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
