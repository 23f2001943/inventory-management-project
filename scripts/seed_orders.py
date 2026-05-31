import sys
import os
import random

from datetime import date, timedelta, datetime

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

    print("Starting Order Seeding...")

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
    # Previous FY:
    # 01-Apr-2025 to 31-Mar-2026
    # =====================================

    start_date = date(2025, 4, 1)
    end_date = date(2026, 3, 31)

    total_days = (
        end_date - start_date
    ).days

    # =====================================
    # CREATE MRP ORDERS
    # =====================================

    print("Creating MRP Orders...")

    for _ in range(200):

        memento = random.choice(
            mementos
        )

        r = random.random()

        # 60% small
        if r < 0.60:

            qty = random.randint(
                50,
                200
            )

        # 30% medium
        elif r < 0.90:

            qty = random.randint(
                200,
                500
            )

        # 10% large
        else:

            qty = random.randint(
                500,
                1000
            )

        mrp_order = MRPOrder(

            memento_id=memento.id,

            order_quantity=qty,

            due_week=random.randint(
                1,
                50
            ),

            created_at=datetime.utcnow()

        )

        db.session.add(
            mrp_order
        )

    db.session.commit()

    print("MRP Orders Created")

    # =====================================
    # CREATE PURCHASE ORDERS
    # =====================================

    print("Creating Purchase Orders...")

    for _ in range(500):

        order = Order()

        db.session.add(order)

        db.session.flush()

        # ==========================
        # DISTRIBUTION
        # Foil       35%
        # Board      35%
        # Accessory  20%
        # Paint      10%
        # ==========================

        r = random.random()

        # =====================================
        # FOIL
        # =====================================

        if r < 0.35:

            foil = random.choice(
                foils
            )

            qty = random.randint(
                300,
                500
            )

            received_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            item = OrderItem(

                order_id=order.id,

                item_type="Foil",

                item_id=foil.id,

                code=foil.foil_code,

                quantity=qty,

                price=foil.price,

                status="Received",

                arrival_date=received_date,

                received_date=received_date

            )

            db.session.add(item)

            # Inventory Update
            foil.quantity += qty

        # =====================================
        # BOARD
        # =====================================

        elif r < 0.70:

            board = random.choice(
                boards
            )

            qty = random.randint(
                50,
                100
            )

            received_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            item = OrderItem(

                order_id=order.id,

                item_type="Board",

                item_id=board.id,

                code=board.name,

                quantity=qty,

                price=board.price,

                status="Received",

                arrival_date=received_date,

                received_date=received_date

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

            qty = random.randint(
                200,
                350
            )

            received_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            item = OrderItem(

                order_id=order.id,

                item_type="Accessory",

                item_id=accessory.id,

                code=accessory.name,

                quantity=qty,

                price=accessory.price,

                status="Received",

                arrival_date=received_date,

                received_date=received_date

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

            qty = random.randint(
                15,
                30
            )

            received_date = (
                start_date
                +
                timedelta(
                    days=random.randint(
                        0,
                        total_days
                    )
                )
            )

            item = OrderItem(

                order_id=order.id,

                item_type="Paint",

                item_id=paint.id,

                code=paint.name,

                quantity=qty,

                price=paint.price,

                status="Received",

                arrival_date=received_date,

                received_date=received_date

            )

            db.session.add(item)

            paint.quantity += qty

    db.session.commit()

    print("Purchase Orders Created")

    print("================================")
    print("ORDER SEEDING COMPLETED")
    print("================================")