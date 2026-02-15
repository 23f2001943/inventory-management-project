from flask import Blueprint, render_template
from controller.decorators import login_required, role_required

employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


@employee_bp.route("/dashboard")
@login_required
@role_required("Employee")
def dashboard():
    return render_template("employee/dashboard.html")
