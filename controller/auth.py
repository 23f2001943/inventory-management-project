from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from controller.models import db, User, Role

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# =========================
# Login
# =========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password, is_active=True).first()

        if not user:
            flash("Invalid credentials", "danger")
            return redirect(url_for("auth.login"))

        # Store session
        session["user_id"] = user.id
        session["user_name"] = user.full_name
        session["roles"] = [role.name for role in user.roles]

        # Role-based redirect
        if "Admin" in session["roles"]:
            return redirect(url_for("admin.dashboard"))
        else:
            return redirect(url_for("employee.dashboard"))

    return render_template("login.html")


# =========================
# Employee Registration
# =========================
@auth_bp.route("/register", methods=["GET", "POST"])
def employee_register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return redirect(url_for("auth.employee_register"))

        employee_role = Role.query.filter_by(name="Employee").first()

        user = User(
            full_name=full_name,
            email=email,
            password=password
        )

        user.roles.append(employee_role)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("employee_register.html")


# =========================
# Logout
# =========================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
