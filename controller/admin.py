from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from controller.decorators import login_required, role_required
from controller.models import Foil, Board, Accessory, db, Order, OrderItem, Paint, Memento, MementoMaterial, Supplier, SupplierMaterial, MRPOrder
from datetime import datetime, timedelta, date
from math import sqrt
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
            item_type="Foil",  # TEMP (we'll improve later)
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


@admin_bp.route("/paint/order/<int:paint_id>", methods=["POST"])
@login_required
@role_required("Admin")
def order_paint(paint_id):

    paint = Paint.query.get_or_404(paint_id)

    data = request.get_json()

    qty = int(data.get("quantity", 0))

    if qty <= 0:
        return jsonify({
            "message": "Invalid quantity"
        }), 400

    supplier_material = SupplierMaterial.query.filter_by(
        item_type="Paint",
        item_name=paint.name
    ).first()

    if not supplier_material:
        return jsonify({
            "message": f"No supplier configured for {paint.name}"
        }), 400

    arrival_date = (
        datetime.utcnow().date() +
        timedelta(weeks=supplier_material.lead_time)
    )

    order = Order()

    db.session.add(order)
    db.session.flush()

    order_item = OrderItem(

        order_id=order.id,

        item_type="Paint",

        item_id=paint.id,

        code=paint.name,

        quantity=qty,

        price=paint.price,

        status="Placed",

        arrival_date=arrival_date
    )

    db.session.add(order_item)

    db.session.commit()

    return jsonify({
        "message":
        f"Order placed successfully. Expected arrival: {arrival_date}"
    })

@admin_bp.route("/orders/receive/<int:item_id>")
@login_required
@role_required("Admin")
def receive_order(item_id):

    item = OrderItem.query.get_or_404(item_id)

    if item.status == "Received":

        flash("Order already received", "warning")

        return redirect(
            url_for("admin.order_history")
        )

    # ======================
    # PAINT
    # ======================

    if item.item_type.lower() == "paint":

        paint = Paint.query.get(item.item_id)

        if paint:
            paint.quantity += item.quantity

    # ======================
    # ACCESSORY
    # ======================

    elif item.item_type.lower() == "accessory":

        accessory = Accessory.query.get(item.item_id)

        if accessory:
            accessory.quantity += item.quantity

    # ======================
    # BOARD
    # ======================

    elif item.item_type.lower() == "board":

        board = Board.query.get(item.item_id)

        if board:
            board.quantity += item.quantity

    # ======================
    # FOIL
    # ======================

    elif item.item_type.lower() == "foil":

        foil = Foil.query.get(item.item_id)

        if foil:
            foil.quantity += item.quantity

    # ======================
    # UPDATE ORDER STATUS
    # ======================

    item.status = "Received"

    item.received_date = datetime.utcnow().date()

    db.session.commit()

    flash(
        "Order received and inventory updated",
        "success"
    )

    return redirect(
        url_for("admin.order_history")
    )

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
    quantities = request.form.getlist("quantity[]")

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
                board.quantity = quantities[i]
                board.length = length
                board.breadth = breadth
                board.price = prices[i]
        else:
            new_board = Board(
                name=names[i],
                quantity=quantities[i],
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

@admin_bp.route("/board/order/<int:board_id>", methods=["POST"])
@login_required
@role_required("Admin")
def order_board(board_id):

    board = Board.query.get_or_404(board_id)

    data = request.get_json()

    qty = int(data.get("quantity", 0))

    if qty <= 0:
        return jsonify({
            "message": "Invalid quantity"
        }), 400

    supplier_material = SupplierMaterial.query.filter_by(
        item_type="Board",
        item_name=board.name
    ).first()

    if not supplier_material:

        return jsonify({
            "message":
            f"No supplier configured for {board.name}"
        }), 400

    arrival_date = (
        datetime.utcnow().date() +
        timedelta(
            weeks=supplier_material.lead_time
        )
    )

    order = Order()

    db.session.add(order)
    db.session.flush()

    order_item = OrderItem(

        order_id=order.id,

        item_type="Board",

        item_id=board.id,

        code=board.name,

        quantity=qty,

        price=board.price,

        status="Placed",

        arrival_date=arrival_date
    )

    db.session.add(order_item)

    db.session.commit()

    return jsonify({

        "message":
        f"Board order placed. Arrival: {arrival_date}"

    })

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

@admin_bp.route("/accessory/order/<int:accessory_id>", methods=["POST"])
@login_required
@role_required("Admin")
def order_accessory(accessory_id):

    accessory = Accessory.query.get_or_404(
        accessory_id
    )

    data = request.get_json()

    qty = int(data.get("quantity", 0))

    if qty <= 0:

        return jsonify({
            "message": "Invalid quantity"
        }), 400

    supplier_material = SupplierMaterial.query.filter_by(
        item_type="Accessory",
        item_name=accessory.name
    ).first()

    if not supplier_material:

        return jsonify({
            "message":
            f"No supplier configured for {accessory.name}"
        }), 400

    arrival_date = (
        datetime.utcnow().date()
        +
        timedelta(
            weeks=supplier_material.lead_time
        )
    )

    order = Order()

    db.session.add(order)

    db.session.flush()

    order_item = OrderItem(

        order_id=order.id,

        item_type="Accessory",

        item_id=accessory.id,

        code=accessory.name,

        quantity=qty,

        price=accessory.price,

        status="Placed",

        arrival_date=arrival_date
    )

    db.session.add(order_item)

    db.session.commit()

    return jsonify({

        "message":
        f"Accessory order placed. Arrival: {arrival_date}"

    })

# =========================
# VIEW MEMENTOS
# =========================
@admin_bp.route("/mementos")
@login_required
@role_required("Admin")
def view_mementos():

    mementos = Memento.query.all()

    foils = Foil.query.all()
    paints = Paint.query.all()
    accessories = Accessory.query.all()
    boards = Board.query.all()

    return render_template(
        "admin/memento.html",
        mementos=mementos,
        foils=foils,
        paints=paints,
        accessories=accessories,
        boards=boards
    )

# =========================
# BULK UPDATE MEMENTOS
# =========================
@admin_bp.route("/mementos/bulk-update", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_update_mementos():

    ids = request.form.getlist("id[]")
    codes = request.form.getlist("code[]")
    dimensions = request.form.getlist("dimension[]")
    prices = request.form.getlist("price[]")
    quantities = request.form.getlist("quantity[]")

    total_rows = len(codes)

    for i in range(total_rows):

        code = codes[i].strip()
        dimension = dimensions[i].strip()
        price = prices[i]
        quantity = quantities[i]

        if code == "":
            continue

        # UPDATE EXISTING
        if i < len(ids) and ids[i]:

            memento = Memento.query.get(ids[i])

            if memento:

                existing = Memento.query.filter(
                    Memento.code.ilike(code),
                    Memento.id != memento.id
                ).first()

                if existing:

                    flash(
                        f"Memento code '{code}' already exists",
                        "danger"
                    )

                    return redirect(
                        url_for("admin.view_mementos")
                    )

                memento.code = code
                memento.dimension = dimension
                memento.price = float(price)
                memento.quantity = int(quantity)

        # CREATE NEW
        else:

            existing = Memento.query.filter(
                Memento.code.ilike(code)
            ).first()

            if existing:

                flash(
                    f"Memento code '{code}' already exists",
                    "danger"
                )

                return redirect(
                    url_for("admin.view_mementos")
                )

            new_memento = Memento(
                code=code,
                dimension=dimension,
                price=float(price),
                quantity=int(quantity)
            )

            db.session.add(new_memento)

    db.session.commit()

    flash("Mementos updated successfully", "success")

    return redirect(url_for("admin.view_mementos"))

# =========================
# BULK DELETE MEMENTOS
# =========================
@admin_bp.route("/mementos/bulk-delete", methods=["POST"])
@login_required
@role_required("Admin")
def bulk_delete_mementos():

    selected_ids = request.form.getlist("selected_ids[]")

    for memento_id in selected_ids:

        memento = Memento.query.get(memento_id)

        if memento:
            db.session.delete(memento)

    db.session.commit()

    flash("Selected mementos deleted", "danger")

    return redirect(url_for("admin.view_mementos"))

# =========================
# SEARCH MEMENTOS
# =========================
@admin_bp.route("/mementos/search")
@login_required
@role_required("Admin")
def search_mementos():

    query = request.args.get("q", "")

    if query.strip() == "":

        mementos = Memento.query.all()

    else:

        mementos = Memento.query.filter(
            Memento.code.ilike(f"%{query}%")
        ).all()

    result = []

    for memento in mementos:

        result.append({
            "id": memento.id,
            "code": memento.code,
            "dimension": memento.dimension,
            "price": memento.price,
            "quantity": memento.quantity
        })

    return jsonify(result)


# =========================
# SAVE MEMENTO MATERIALS
# =========================
@admin_bp.route(
    "/mementos/<int:memento_id>/save-materials",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def save_memento_materials(memento_id):

    material_types = request.form.getlist("material_type[]")
    material_ids = request.form.getlist("material_id[]")
    quantities = request.form.getlist("quantity_used[]")

    # DELETE OLD
    MementoMaterial.query.filter_by(
        memento_id=memento_id
    ).delete()

    # SAVE NEW
    for i in range(len(material_types)):

        if material_ids[i] == "":
            continue

        material = MementoMaterial(
            memento_id=memento_id,
            material_type=material_types[i],
            material_id=int(material_ids[i]),
            quantity_used=float(quantities[i])
        )

        db.session.add(material)

    db.session.commit()

    flash("Materials saved successfully", "success")

    return redirect(url_for("admin.view_mementos"))

# =========================
# GET MEMENTO MATERIALS
# =========================
@admin_bp.route(
    "/mementos/<int:memento_id>/materials"
)
@login_required
@role_required("Admin")
def get_memento_materials(memento_id):

    materials = MementoMaterial.query.filter_by(
        memento_id=memento_id
    ).all()

    result = []

    for material in materials:

        material_name = ""

        if material.material_type == "Foil":

            item = Foil.query.get(
                material.material_id
            )

            if item:
                material_name = item.foil_code

        elif material.material_type == "Paint":

            item = Paint.query.get(
                material.material_id
            )

            if item:
                material_name = item.name

        elif material.material_type == "Accessory":

            item = Accessory.query.get(
                material.material_id
            )

            if item:
                material_name = item.name

        elif material.material_type == "Board":

            item = Board.query.get(
                material.material_id
            )

            if item:
                material_name = item.name

        result.append({
            "id": material.id,
            "material_type": material.material_type,
            "material_id": material.material_id,
            "material_name": material_name,
            "quantity_used": material.quantity_used
        })

    return jsonify(result)


# =========================
# SAVE MATERIALS AJAX
# =========================
@admin_bp.route(
    "/mementos/<int:memento_id>/materials/save",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def save_memento_materials_ajax(memento_id):

    data = request.get_json()

    MementoMaterial.query.filter_by(
        memento_id=memento_id
    ).delete()

    for row in data:

        material = MementoMaterial(
            memento_id=memento_id,
            material_type=row["material_type"],
            material_id=int(row["material_id"]),
            quantity_used=float(row["quantity_used"])
        )

        db.session.add(material)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Materials saved"
    })

# =========================
# GET MATERIAL OPTIONS
# =========================
@admin_bp.route("/materials/options")
@login_required
@role_required("Admin")
def material_options():

    return jsonify({

        "foils": [
            {
                "id": f.id,
                "name": f.foil_code
            }
            for f in Foil.query.all()
        ],

        "paints": [
            {
                "id": p.id,
                "name": p.name
            }
            for p in Paint.query.all()
        ],

        "accessories": [
            {
                "id": a.id,
                "name": a.name
            }
            for a in Accessory.query.all()
        ],

        "boards": [
            {
                "id": b.id,
                "name": b.name
            }
            for b in Board.query.all()
        ]
    })

# =========================
# VIEW SUPPLIERS
# =========================
@admin_bp.route("/suppliers")
@login_required
@role_required("Admin")
def view_suppliers():

    suppliers = Supplier.query.all()

    foils = Foil.query.all()
    paints = Paint.query.all()
    accessories = Accessory.query.all()
    boards = Board.query.all()

    return render_template(
        "admin/supplier.html",
        suppliers=suppliers,
        foils=foils,
        paints=paints,
        accessories=accessories,
        boards=boards
    )

# =========================
# ADD SUPPLIER
# =========================
@admin_bp.route(
    "/suppliers/add",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def add_supplier():

    supplier_name = request.form.get(
        "supplier_name"
    )

    if supplier_name.strip() == "":
        return redirect(
            url_for("admin.view_suppliers")
        )

    existing = Supplier.query.filter_by(
        supplier_name=supplier_name
    ).first()

    if existing:
        flash(
            "Supplier already exists",
            "danger"
        )

        return redirect(
            url_for("admin.view_suppliers")
        )

    supplier = Supplier(
        supplier_name=supplier_name
    )

    db.session.add(supplier)
    db.session.commit()

    return redirect(
        url_for("admin.view_suppliers")
    )

# =========================
# SAVE SUPPLIER MATERIALS
# =========================
# =========================
# SAVE SUPPLIER MATERIALS
# =========================
@admin_bp.route(
    "/suppliers/<int:supplier_id>/save",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def save_supplier_materials(supplier_id):

    item_types = request.form.getlist(
        "item_type[]"
    )

    item_names = request.form.getlist(
        "item_name[]"
    )

    lead_times = request.form.getlist(
        "lead_time[]"
    )
    safety_stocks = request.form.getlist(
    "safety_stock[]"
)
    
    ordering_costs = request.form.getlist(
        "ordering_cost[]"
    )

    holding_costs = request.form.getlist(
        "holding_cost[]"
    )

    SupplierMaterial.query.filter_by(
        supplier_id=supplier_id
    ).delete()

    for i in range(len(item_types)):

        if item_names[i].strip() == "":
            continue

        material = SupplierMaterial(

            supplier_id=supplier_id,

            item_type=item_types[i],

            item_name=item_names[i],

            lead_time=int(
                lead_times[i] or 0
            ),

            safety_stock=int(
                safety_stocks[i] or 0
            ),

            ordering_cost=float(
                ordering_costs[i] or 0
            ),

            holding_cost=float(
                holding_costs[i] or 0
            )

        )

        db.session.add(material)

    db.session.commit()

    flash(
        "Supplier materials updated successfully",
        "success"
    )

    return redirect(
        url_for("admin.view_suppliers")
    )

# =========================
# VIEW MRP
# =========================
@admin_bp.route("/mrp")
@login_required
@role_required("Admin")
def view_mrp():

    mementos = Memento.query.all()

    orders = MRPOrder.query.order_by(
        MRPOrder.id.desc()
    ).all()

    return render_template(
        "admin/mrp.html",
        mementos=mementos,
        orders=orders,
        selected_order=None
    )

# =========================
# ADD MRP ORDER
# =========================
@admin_bp.route(
    "/mrp/add-order",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def add_mrp_order():

    order = MRPOrder(

        memento_id=
        request.form.get("memento_id"),

        order_quantity=
        request.form.get("order_quantity"),

        due_week=
        request.form.get("due_week")
    )

    db.session.add(order)

    db.session.commit()

    flash(
        "MRP Order Added",
        "success"
    )

    return redirect(
        url_for("admin.view_mrp")
    )

# =========================
# VIEW SINGLE MRP
# =========================
@admin_bp.route("/mrp/order/<int:order_id>")
@login_required
@role_required("Admin")
def view_single_mrp(order_id):

    order = MRPOrder.query.get_or_404(order_id)

    mementos = Memento.query.all()

    orders = MRPOrder.query.order_by(
        MRPOrder.id.desc()
    ).all()

    mrp_rows = []

    materials = MementoMaterial.query.filter_by(
        memento_id=order.memento_id
    ).all()

    sr_no = 1

    for material in materials:

        need = (
            material.quantity_used
            * order.order_quantity
        )

        material_name = ""

        available = 0

        # =========================
        # FOIL
        # =========================

        if material.material_type == "Foil":

            item = Foil.query.get(
                material.material_id
            )

            if item:

                material_name = item.foil_code

                available = item.quantity

        # =========================
        # PAINT
        # =========================

        elif material.material_type == "Paint":

            item = Paint.query.get(
                material.material_id
            )

            if item:

                material_name = item.name

                available = item.quantity

        # =========================
        # ACCESSORY
        # =========================

        elif material.material_type == "Accessory":

            item = Accessory.query.get(
                material.material_id
            )

            if item:

                material_name = item.name

                available = item.quantity

        # =========================
        # BOARD
        # =========================

        elif material.material_type == "Board":

            item = Board.query.get(
                material.material_id
            )

            if item:

                material_name = item.name

                available = item.quantity

        supplier = SupplierMaterial.query.filter_by(
            item_type=material.material_type,
            item_name=material_name
        ).first()

        lead_time = 0
        safety_stock = 0

        if supplier:

            lead_time = supplier.lead_time

            safety_stock = supplier.safety_stock

        shortage = max(
            0,
            need + safety_stock - available
        )

        if shortage > 0:

            order_week = max(
                1,
                order.due_week - lead_time
            )

        else:

            order_week = None

        mrp_rows.append({

    "material_id":
        material.id,

    "sr_no":
        sr_no,

    "material":
        material_name,

    "need":
        need,

    "available":
        available,

    "safety_stock":
        safety_stock,

    "shortage":
        shortage,

    "lead_time":
        lead_time,

    "order_week":
        order_week

})

        sr_no += 1

    return render_template(
        "admin/mrp.html",
        mementos=mementos,
        orders=orders,
        selected_order=order,
        mrp_rows=mrp_rows
    )

# =========================
# MATERIAL MRP DETAILS
# =========================
@admin_bp.route(
    "/mrp/order/<int:order_id>/material/<int:material_id>"
)
@login_required
@role_required("Admin")
def material_mrp_details(
    order_id,
    material_id
):

    order = MRPOrder.query.get_or_404(order_id)

    material = MementoMaterial.query.get_or_404(
        material_id
    )

    due_week = order.due_week

    available = 0
    material_name = ""

    # =========================
    # GET MATERIAL
    # =========================

    if material.material_type == "Foil":

        item = Foil.query.get(
            material.material_id
        )

        if item:

            available = item.quantity

            material_name = item.foil_code

    elif material.material_type == "Paint":

        item = Paint.query.get(
            material.material_id
        )

        if item:

            available = item.quantity

            material_name = item.name

    elif material.material_type == "Accessory":

        item = Accessory.query.get(
            material.material_id
        )

        if item:

            available = item.quantity

            material_name = item.name

    elif material.material_type == "Board":

        item = Board.query.get(
            material.material_id
        )

        if item:

            material_name = item.name

            available = item.quantity

    # =========================
    # SUPPLIER INFO
    # =========================

    supplier = SupplierMaterial.query.filter_by(
        item_type=material.material_type,
        item_name=material_name
    ).first()

    lead_time = 0
    safety_stock = 0

    if supplier:

        lead_time = supplier.lead_time

        safety_stock = supplier.safety_stock

    # =========================
    # SCHEDULE STRUCTURE
    # =========================

    schedule = {

        "gross": {},

        "scheduled_receipt": {},

        "projected": {},

        "net": {},

        "receipt": {},

        "release": {}
    }

    for week in range(1, due_week + 1):

        schedule["gross"][week] = 0

        schedule["scheduled_receipt"][week] = 0

        schedule["projected"][week] = 0

        schedule["net"][week] = 0

        schedule["receipt"][week] = 0

        schedule["release"][week] = 0

    # =========================
    # GROSS REQUIREMENTS
    # ALL CUSTOMER ORDERS
    # =========================

    all_orders = MRPOrder.query.filter(
        MRPOrder.due_week <= due_week
    ).all()

    for customer_order in all_orders:

        bom_items = MementoMaterial.query.filter_by(
            memento_id=customer_order.memento_id
        ).all()

        for bom in bom_items:

            if (
                bom.material_type ==
                material.material_type
                and
                bom.material_id ==
                material.material_id
            ):

                qty_needed = (

                    bom.quantity_used
                    *
                    customer_order.order_quantity

                )

                schedule["gross"][
                    customer_order.due_week
                ] += qty_needed

    # =========================
    # SCHEDULED RECEIPTS
    # PURCHASE ORDERS
    # =========================

    purchase_orders = OrderItem.query.filter_by(
        item_type=material.material_type,
        status="Received"
    ).all()

    for po in purchase_orders:

        if po.code != material_name:
            continue

        if not po.received_date:
            continue

        week = po.received_date.isocalendar()[1]

        if 1 <= week <= due_week:

            schedule[
                "scheduled_receipt"
            ][week] += po.quantity

    # =========================
    # MRP EXPLOSION
    # =========================

    current_inventory = available

    for week in range(1, due_week + 1):

        gross = schedule["gross"][week]

        scheduled_receipt = (
            schedule["scheduled_receipt"][week]
        )

        current_inventory += (
            scheduled_receipt
        )

        projected_after_demand = (
            current_inventory
            -
            gross
        )

        if projected_after_demand < safety_stock:

            net_req = (

                safety_stock
                -
                projected_after_demand

            )

            schedule["net"][
                week
            ] = net_req

            schedule["receipt"][
                week
            ] = net_req

            release_week = max(
                1,
                week - lead_time
            )

            schedule["release"][
                release_week
            ] += net_req

            projected_after_demand += (
                net_req
            )

        schedule["projected"][
            week
        ] = projected_after_demand

        current_inventory = (
            projected_after_demand
        )

    return render_template(

        "admin/mrp_schedule.html",

        order=order,

        material_name=material_name,

        due_week=due_week,

        available=available,

        safety_stock=safety_stock,

        lead_time=lead_time,

        schedule=schedule
    )

@admin_bp.route("/abc-analysis")
@login_required
@role_required("Admin")
def view_abc_analysis():

    return render_template(
        "admin/abc.html"
    )

from collections import defaultdict

@admin_bp.route("/abc-analysis/data")
@login_required
@role_required("Admin")
def abc_analysis_data():

    analysis_type = request.args.get(
        "type",
        "all"
    )

    order_items = OrderItem.query.filter_by(
        status="Received"
    ).all()

    summary = defaultdict(lambda: {
        "type": "",
        "item": "",
        "qty": 0,
        "value": 0
    })

    for item in order_items:

        item_type = item.item_type.strip()

        if (
            analysis_type != "all"
            and
            item_type.lower() != analysis_type.lower()
        ):
            continue

        key = (
            item_type,
            item.code
        )

        summary[key]["type"] = item_type
        summary[key]["item"] = item.code

        summary[key]["qty"] += item.quantity

        summary[key]["value"] += (
            item.quantity * item.price
        )

    rows = list(summary.values())

    rows.sort(
        key=lambda x: x["value"],
        reverse=True
    )

    total_value = sum(
        row["value"]
        for row in rows
    )

    cumulative = 0

    for row in rows:

        row["avg_price"] = round(
            row["value"] / row["qty"],
            2
        ) if row["qty"] else 0

        if total_value > 0:

            cumulative += (
                row["value"] /
                total_value
            ) * 100

        row["cum_percent"] = round(
            cumulative,
            2
        )

        if cumulative <= 70:

            row["abc_class"] = "A"

        elif cumulative <= 90:

            row["abc_class"] = "B"

        else:

            row["abc_class"] = "C"

    return jsonify(rows)

@admin_bp.route("/eoq")
@login_required
@role_required("Admin")
def view_eoq():

    return render_template(
        "admin/eoq.html"
    )

@admin_bp.route("/eoq/data")
@login_required
@role_required("Admin")
def eoq_data():

    analysis_type = request.args.get(
        "type",
        "all"
    )

    today = date.today()

    # Previous completed FY

    if today.month >= 4:

        fy_start = date(
            today.year - 1,
            4,
            1
        )

        fy_end = date(
            today.year,
            3,
            31
        )

    else:

        fy_start = date(
            today.year - 2,
            4,
            1
        )

        fy_end = date(
            today.year - 1,
            3,
            31
        )

    rows = []

    materials = SupplierMaterial.query.all()

    sr_no = 1

    for material in materials:

        if (
            analysis_type != "all"
            and
            material.item_type.lower()
            != analysis_type.lower()
        ):
            continue

        demand = 0

        orders = OrderItem.query.filter_by(
            item_type=material.item_type,
            code=material.item_name,
            status="Received"
        ).all()

        for order in orders:

            if (
                order.received_date
                and
                fy_start
                <= order.received_date
                <= fy_end
            ):

                demand += order.quantity

        S = material.ordering_cost or 0

        H = material.holding_cost or 0

        lead_time_weeks = material.lead_time or 0

        safety_stock = material.safety_stock or 0

        eoq = 0

        reorder_point = 0

        if demand > 0:

            daily_demand = demand / 365

            lead_time_days = (
                lead_time_weeks * 7
            )

            reorder_point = round(
                (
                    daily_demand
                    *
                    lead_time_days
                )
                +
                safety_stock
            )

        if demand > 0 and S > 0 and H > 0:

            eoq = round(
                sqrt(
                    (2 * demand * S)
                    / H
                )
            )

        rows.append({

            "sr_no": sr_no,

            "type": material.item_type,

            "item": material.item_name,

            "demand": demand,

            "ordering_cost": S,

            "holding_cost": H,

            "eoq": eoq,

            "reorder_point": reorder_point

        })

        sr_no += 1

    return jsonify(rows)