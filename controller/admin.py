from flask import Blueprint, render_template, request, redirect, url_for, flash
from controller.decorators import login_required, role_required
from controller.models import Foil, Board, Accessory, db, Order, OrderItem


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

@admin_bp.route("/foils/bulk-update", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_update_foils():
    ids = request.form.getlist("id[]")
    codes = request.form.getlist("foil_code[]")
    types = request.form.getlist("foil_type[]")
    lengths = request.form.getlist("length_in[]")
    breadths = request.form.getlist("breadth_in[]")
    quantities = request.form.getlist("quantity[]")
    prices = request.form.getlist("price[]")

    for i in range(len(ids)):
        foil = Foil.query.get(ids[i])
        if foil:
            foil.foil_code = codes[i]
            foil.foil_type = types[i]
            foil.length_in = lengths[i]
            foil.breadth_in = breadths[i]
            foil.quantity = quantities[i]
            foil.price = prices[i]

    db.session.commit()

    flash("All changes saved successfully", "success")
    return redirect(url_for("admin.view_foils"))

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


@admin_bp.route("/foils/bulk-delete", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_delete_foils():
    ids = request.form.getlist("selected_ids[]")

    for id in ids:
        foil = Foil.query.get(id)
        if foil:
            db.session.delete(foil)

    db.session.commit()

    flash(f"{len(ids)} foils deleted successfully", "success")
    return redirect(url_for("admin.view_foils"))



@admin_bp.route("/orders/create", methods=["POST"])
@login_required
@role_required("Admin")
def create_order():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    # ✅ Create Order
    order = Order()
    db.session.add(order)
    db.session.flush()  # get order.id without commit

    # ✅ Create Order Items
    for item in data:
        order_item = OrderItem(
            order_id=order.id,
            item_type="foil",  # TEMP (we'll improve later)
            item_id=item.get("item_id"),         # TEMP (will replace with autocomplete)
            code=item.get("code"),
            quantity=int(item.get("quantity", 0)),
            price=float(item.get("price", 0))
        )

        db.session.add(order_item)

    # ✅ Commit everything
    db.session.commit()

    print("Order Saved:", order.id)

    return jsonify({"message": "Order saved successfully"})

@admin_bp.route("/items/search")
@login_required
@role_required("Admin")
def search_items():
    q = request.args.get("q", "")

    foils = Foil.query.filter(Foil.foil_code.ilike(f"%{q}%")).limit(10).all()

    results = []
    for f in foils:
        results.append({
            "id": f.id,
            "label": f"{f.foil_code} ({f.foil_type})",
            "price": f.price,
            "type": "foil"
        })

    return jsonify(results)

@admin_bp.route("/inventory/use", methods=["POST"])
@login_required
@role_required("Admin")
def use_inventory():
    data = request.get_json()

    print("USED INVENTORY:", data)  # 👈 IMPORTANT

    for item in data:
        item_id = item.get("item_id")
        used_qty = int(item.get("quantity", 0))

        foil = Foil.query.get(item_id)

        if foil:
            foil.quantity = max(0, foil.quantity - used_qty)

    db.session.commit()

    return jsonify({"message": "Inventory updated"})


@admin_bp.route("/orders/history")
@login_required
@role_required("Admin")
def order_history():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/order_history.html", orders=orders)