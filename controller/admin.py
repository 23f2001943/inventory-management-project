from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from controller.decorators import login_required, role_required
from controller.models import Foil, Board, Accessory, db, Order, OrderItem, Paint


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

@admin_bp.route("/paints")
@login_required
@role_required("Admin")
def view_paints():
    paints = Paint.query.all()   # if model exists
    return render_template("admin/paint.html", paints=paints)

@admin_bp.route("/paints/bulk-update", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_update_paints():

    ids = request.form.getlist("id[]")
    names = request.form.getlist("name[]")
    quantities = request.form.getlist("quantity[]")
    prices = request.form.getlist("price[]")

    for i in range(len(names)):

        # ✅ Existing paint
        if i < len(ids) and ids[i]:
            paint = Paint.query.get(ids[i])
            if paint:
                paint.name = names[i]
                paint.quantity = quantities[i]
                paint.price = prices[i]

        # ✅ New paint
        else:
            new_paint = Paint(
                name=names[i],
                quantity=quantities[i],
                price=prices[i]
            )
            db.session.add(new_paint)

    db.session.commit()

    flash("Paints updated successfully", "success")
    return redirect(url_for("admin.view_paints"))

@admin_bp.route("/paints/bulk-delete", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_delete_paints():

    ids = request.form.getlist("selected_ids[]")

    for id in ids:
        paint = Paint.query.get(id)
        if paint:
            db.session.delete(paint)

    db.session.commit()

    flash(f"{len(ids)} paints deleted", "success")
    return redirect(url_for("admin.view_paints"))

@admin_bp.route("/paints/search")
@login_required
@role_required("Admin")
def search_paints():

    q = request.args.get("q", "")

    paints = Paint.query.filter(
        Paint.name.ilike(f"%{q}%")
    ).all()

    result = []

    for p in paints:
        result.append({
            "id": p.id,
            "name": p.name,
            "quantity": p.quantity,
            "price": p.price
        })

    return jsonify(result)

@admin_bp.route("/boards")
@login_required
@role_required("Admin")
def view_boards():
    boards = Board.query.all()
    return render_template("admin/boards.html", boards=boards)

@admin_bp.route("/boards/bulk-update", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_update_boards():

    ids = request.form.getlist("id[]")
    names = request.form.getlist("name[]")
    dimensions = request.form.getlist("dimension[]")
    prices = request.form.getlist("price[]")

    for i in range(len(names)):

        dim = dimensions[i]

        length = 0
        breadth = 0

        if "*" in dim:
            parts = dim.split("*")
            if len(parts) == 2:
                try:
                    length = float(parts[0])
                    breadth = float(parts[1])
                except:
                    length = 0
                    breadth = 0

        if i < len(ids) and ids[i]:
            board = Board.query.get(ids[i])
            if board:
                board.name = names[i]
                board.length = length
                board.breadth = breadth
                board.price = prices[i]
        else:
            new_board = Board(
                name=names[i],
                length=length,
                breadth=breadth,
                price=prices[i]
            )
            db.session.add(new_board)

    db.session.commit()

    flash("Boards updated successfully", "success")
    return redirect(url_for("admin.view_boards"))

@admin_bp.route("/boards/bulk-delete", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_delete_boards():

    ids = request.form.getlist("selected_ids[]")

    for id in ids:
        board = Board.query.get(id)
        if board:
            db.session.delete(board)

    db.session.commit()

    flash(f"{len(ids)} boards deleted", "success")
    return redirect(url_for("admin.view_boards"))

# =========================
# VIEW ACCESSORIES
# =========================
@admin_bp.route("/accessories")
@login_required
@role_required("Admin")
def view_accessories():

    accessories = Accessory.query.all()

    return render_template(
        "admin/accessories.html",
        accessories=accessories
    )

# =========================
# BULK UPDATE ACCESSORIES
# =========================
@admin_bp.route("/accessories/bulk-update", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_update_accessories():

    ids = request.form.getlist("id[]")
    names = request.form.getlist("name[]")
    prices = request.form.getlist("price[]")
    quantities = request.form.getlist("quantity[]")

    total_rows = len(names)

    for i in range(total_rows):

        name = names[i].strip()
        price = prices[i]
        quantity = quantities[i]

        # SKIP EMPTY ROWS
        if name == "":
            continue

        # =========================
        # UPDATE EXISTING
        # =========================
        if i < len(ids) and ids[i]:

            accessory = Accessory.query.get(ids[i])

            if accessory:

                # CHECK DUPLICATE NAME
                existing = Accessory.query.filter(
                    Accessory.name.ilike(name),
                    Accessory.id != accessory.id
                ).first()

                if existing:

                    flash(
                        f"Accessory '{name}' already exists",
                        "danger"
                    )

                    return redirect(
                        url_for("admin.view_accessories")
                    )

                accessory.name = name
                accessory.price = float(price)
                accessory.quantity = int(quantity)

        # =========================
        # CREATE NEW
        # =========================
        else:

            # CHECK DUPLICATE
            existing = Accessory.query.filter(
                Accessory.name.ilike(name)
            ).first()

            if existing:

                flash(
                    f"Accessory '{name}' already exists",
                    "danger"
                )

                return redirect(
                    url_for("admin.view_accessories")
                )

            new_accessory = Accessory(
                name=name,
                price=float(price),
                quantity=int(quantity)
            )

            db.session.add(new_accessory)

    db.session.commit()

    flash("Accessories updated successfully", "success")

    return redirect(url_for("admin.view_accessories"))
# =========================
# BULK DELETE ACCESSORIES
# =========================
@admin_bp.route("/accessories/bulk-delete", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_delete_accessories():

    selected_ids = request.form.getlist("selected_ids[]")

    for accessory_id in selected_ids:

        accessory = Accessory.query.get(accessory_id)

        if accessory:
            db.session.delete(accessory)

    db.session.commit()

    flash("Selected accessories deleted", "danger")

    return redirect(url_for("admin.view_accessories"))

# =========================
# SEARCH ACCESSORIES
# =========================
@admin_bp.route("/accessories/search")
@login_required
@role_required("Admin")
def search_accessories():

    query = request.args.get("q", "")

    accessories = Accessory.query.filter(
        Accessory.name.ilike(f"%{query}%")
    ).all()

    result = []

    for accessory in accessories:

        result.append({
            "id": accessory.id,
            "name": accessory.name,
            "price": accessory.price,
            "quantity": accessory.quantity
        })

    return jsonify(result)

