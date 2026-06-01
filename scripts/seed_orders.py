import sys
import os
import random

from datetime import (
    date,
    timedelta,
    datetime
)

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app import app
from controller.models import *

with app.app_context():

    print("================================")
    print("DELETING OLD ORDERS")
    print("================================")

    OrderItem.query.delete()
    Order.query.delete()
    MRPOrder.query.delete()

    db.session.commit()

    print("Old orders deleted")

    # =====================================
    # LOAD MASTER DATA
    # =====================================

    foils = Foil.query.all()
    paints = Paint.query.all()
    boards = Board.query.all()
    accessories = Accessory.query.all()
    mementos = Memento.query.all()

    # =====================================
    # DATE RANGE
    # =====================================

    start_date = date(2025, 4, 1)
    end_date = date(2026, 3, 31)

    total_days = (
        end_date - start_date
    ).days

    # =====================================
    # MRP ORDERS
    # =====================================

    print("Creating MRP Orders...")

    for _ in range(200):

        memento = random.choice(
            mementos
        )

        r = random.random()

        # 60%
        if r < 0.60:

            qty = random.randint(
                200,
                350
            )

        # 30%
        elif r < 0.90:

            qty = random.randint(
                350,
                500
            )

        # 10%
        else:

            qty = random.randint(
                500,
                600
            )

        mrp_order = MRPOrder(

            memento_id=memento.id,

            order_quantity=qty,

            due_week=random.randint(
                1,
                52
            ),

            created_at=datetime.utcnow()

        )

        db.session.add(
            mrp_order
        )

    db.session.commit()

    print("MRP Orders Created")

    # =====================================
    # PURCHASE ORDERS
    # =====================================

    print("Creating Purchase Orders...")

    for _ in range(500):

        r = random.random()

        # =====================================
        # FOIL
        # =====================================

        if r < 0.35:

            foil = random.choice(
                foils
            )

            supplier_material = (
                SupplierMaterial.query.filter_by(
                    item_type="Foil",
                    item_name=foil.foil_code
                ).first()
            )

            if not supplier_material:
                continue

            lead_time = (
                supplier_material.lead_time
            )

            qty = random.randint(
                400,
                600
            )

            order_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            arrival_date = (
                order_date
                +
                timedelta(
                    weeks=lead_time
                )
            )

            order = Order(
                created_at=datetime.combine(
                    order_date,
                    datetime.min.time()
                )
            )

            db.session.add(order)
            db.session.flush()

            item = OrderItem(

                order_id=order.id,

                item_type="Foil",

                item_id=foil.id,

                code=foil.foil_code,

                quantity=qty,

                price=foil.price,

                status="Received",

                arrival_date=arrival_date,

                received_date=arrival_date
            )

            db.session.add(item)

            foil.quantity += qty

        # =====================================
        # BOARD
        # =====================================

        elif r < 0.70:

            board = random.choice(
                boards
            )

            supplier_material = (
                SupplierMaterial.query.filter_by(
                    item_type="Board",
                    item_name=board.name
                ).first()
            )

            if not supplier_material:
                continue

            lead_time = (
                supplier_material.lead_time
            )

            qty = random.randint(
                200,
                400
            )

            order_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            arrival_date = (
                order_date
                +
                timedelta(
                    weeks=lead_time
                )
            )

            order = Order(
                created_at=datetime.combine(
                    order_date,
                    datetime.min.time()
                )
            )

            db.session.add(order)
            db.session.flush()

            item = OrderItem(

                order_id=order.id,

                item_type="Board",

                item_id=board.id,

                code=board.name,

                quantity=qty,

                price=board.price,

                status="Received",

                arrival_date=arrival_date,

                received_date=arrival_date
            )

            db.session.add(item)

            board.quantity += qty

        # =====================================
        # ACCESSORY
        # =====================================

        elif r < 0.90:

            accessory = random.choice(
                accessories
            )

            supplier_material = (
                SupplierMaterial.query.filter_by(
                    item_type="Accessory",
                    item_name=accessory.name
                ).first()
            )

            if not supplier_material:
                continue

            lead_time = (
                supplier_material.lead_time
            )

            qty = random.randint(
                250,
                500
            )

            order_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            arrival_date = (
                order_date
                +
                timedelta(
                    weeks=lead_time
                )
            )

            order = Order(
                created_at=datetime.combine(
                    order_date,
                    datetime.min.time()
                )
            )

            db.session.add(order)
            db.session.flush()

            item = OrderItem(

                order_id=order.id,

                item_type="Accessory",

                item_id=accessory.id,

                code=accessory.name,

                quantity=qty,

                price=accessory.price,

                status="Received",

                arrival_date=arrival_date,

                received_date=arrival_date
            )

            db.session.add(item)

            accessory.quantity += qty

        # =====================================
        # PAINT
        # =====================================

        else:

            paint = random.choice(
                paints
            )

            supplier_material = (
                SupplierMaterial.query.filter_by(
                    item_type="Paint",
                    item_name=paint.name
                ).first()
            )

            if not supplier_material:
                continue

            lead_time = (
                supplier_material.lead_time
            )

            qty = random.randint(
                50,
                100
            )

            order_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            arrival_date = (
                order_date
                +
                timedelta(
                    weeks=lead_time
                )
            )

            order = Order(
                created_at=datetime.combine(
                    order_date,
                    datetime.min.time()
                )
            )

            db.session.add(order)
            db.session.flush()

            item = OrderItem(

                order_id=order.id,

                item_type="Paint",

                item_id=paint.id,

                code=paint.name,

                quantity=qty,

                price=paint.price,

                status="Received",

                arrival_date=arrival_date,

                received_date=arrival_date
            )

            db.session.add(item)

            paint.quantity += qty

    db.session.commit()

    print("Purchase Orders Created")

    print("================================")
    print("SEEDING COMPLETED")
    print("================================")