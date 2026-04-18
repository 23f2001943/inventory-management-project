from flask import Blueprint, render_template, request, redirect, url_for, flash
from controller.decorators import login_required, role_required
from controller.models import Foil, Board, Accessory, db

import pandas as pd

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("Admin")
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/add-item", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_item():
    if request.method == "POST":
        item_type = request.form.get("item_type")
        file = request.files.get("excel_file")

        if not file:
            flash("Excel file is required", "danger")
            return redirect(request.url)

        df = pd.read_excel(file)

        MODEL_MAP = {
            "foil": Foil,
            "board": Board,
            "accessory": Accessory
        }

        model = MODEL_MAP.get(item_type)

        if not model:
            flash("Invalid item type selected", "danger")
            return redirect(request.url)

        for _, row in df.iterrows():
            record = model(**row.to_dict())
            db.session.add(record)

        db.session.commit()

        flash("Data uploaded successfully", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_item.html")



@admin_bp.route("/foils")
@login_required
@role_required("Admin")
def view_foils():
    foils = Foil.query.all()
    return render_template("admin/foil.html", foils=foils)

@admin_bp.route("/foil/edit/<int:foil_id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_foil(foil_id):
    foil = Foil.query.get_or_404(foil_id)

    if request.method == "POST":
        foil.foil_code = request.form.get("foil_code")
        foil.foil_type = request.form.get("foil_type")
        foil.length_in = request.form.get("length_in")
        foil.breadth_in = request.form.get("breadth_in")
        foil.quantity = request.form.get("quantity")
        foil.price = request.form.get("price")

        db.session.commit()
        flash("Foil updated successfully", "success")
        return redirect(url_for("admin.view_foils"))

    return render_template("admin/edit_foil.html", foil=foil)

@admin_bp.route("/foil/delete/<int:foil_id>", methods=["POST"])
@login_required
@role_required("Admin")
def delete_foil(foil_id):
    foil = Foil.query.get_or_404(foil_id)
    db.session.delete(foil)
    db.session.commit()

    flash("Foil deleted", "success")
    return redirect(url_for("admin.view_foils"))


@admin_bp.route("/foil/add", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_foil_manual():
    if request.method == "POST":
        foil = Foil(
            foil_code=request.form.get("foil_code"),
            foil_type=request.form.get("foil_type"),
            length_in=request.form.get("length_in"),
            breadth_in=request.form.get("breadth_in"),
            quantity=request.form.get("quantity"),
            price=request.form.get("price"),
        )

        db.session.add(foil)
        db.session.commit()

        flash("Foil added successfully", "success")
        return redirect(url_for("admin.view_foils"))

    return render_template("admin/add_foil.html")

@admin_bp.route("/foil/update/<int:foil_id>", methods=["POST"])
@login_required
@role_required("Admin")
def update_foil(foil_id):
    foil = Foil.query.get_or_404(foil_id)

    foil.foil_code = request.form.get("foil_code")
    foil.foil_type = request.form.get("foil_type")
    foil.length_in = request.form.get("length_in")
    foil.breadth_in = request.form.get("breadth_in")
    foil.quantity = request.form.get("quantity")
    foil.price = request.form.get("price")

    db.session.commit()
    flash("Foil updated", "success")
    return redirect(url_for("admin.view_foils"))

@admin_bp.route("/foil/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_foil_inline():
    foil = Foil(
        foil_code=request.form.get("foil_code"),
        foil_type=request.form.get("foil_type"),
        length_in=request.form.get("length_in"),
        breadth_in=request.form.get("breadth_in"),
        quantity=request.form.get("quantity"),
        price=request.form.get("price"),
    )

    db.session.add(foil)
    db.session.commit()

    flash("Foil added", "success")
    return redirect(url_for("admin.view_foils"))


from flask import jsonify, request

@admin_bp.route("/foils/search")
@login_required
@role_required("Admin")
def search_foils():
    query = request.args.get("q", "")

    foils = Foil.query.filter(
        Foil.foil_code.ilike(f"%{query}%")
    ).all()

    result = []
    for f in foils:
        result.append({
            "id": f.id,
            "foil_code": f.foil_code,
            "foil_type": f.foil_type,
            "length_in": f.length_in,
            "breadth_in": f.breadth_in,
            "quantity": f.quantity,
            "price": f.price
        })

    return jsonify(result)