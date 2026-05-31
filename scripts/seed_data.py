import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app import app
from controller.models import *

import random

with app.app_context():
        foil_codes = [

            "RJ-41","RJ-42","RJ-43","RJ-44","RJ-45",

            "RV-1501","RV-1502","RV-1503","RV-1504",
            "RV-1505","RV-1506","RV-1507","RV-1508",
            "RV-1509","RV-1510","RV-1511","RV-1512",
            "RV-1513","RV-1514","RV-1515","RV-1516",
            "RV-1517","RV-1518",

            "MG-101","MG-102","MG-103","MG-104","MG-105"
        ]

        for code in foil_codes:

            db.session.add(
                Foil(
                    foil_code=code,
                    foil_type=random.choice(
                        ["Gold", "Silver"]
                    ),
                    length_in=random.choice(
                        [4,5,6,7,8]
                    ),
                    breadth_in=random.choice(
                        [4,5,6,7,8]
                    ),
                    quantity=random.randint(
                        100,500
                    ),
                    price=random.randint(
                        40,150
                    )
                )
            )

        db.session.commit()

        print("Foils seeded")

        paint_names = [

        "NC Black",
        "NC White",
        "NC Gold",
        "NC Silver",
        "NC Red",
        "NC Blue",
        "NC Green",
        "NC Bronze",
        "NC Copper",
        "NC Yellow"

    ]

        for name in paint_names:

            db.session.add(
                Paint(
                    name=name,
                    quantity=random.randint(
                        50,300
                    ),
                    price=random.randint(
                        300,1200
                    )
                )
            )

        db.session.commit()

        print("Paints seeded")

        board_names = [

            "MDF Board",
            "Wooden MDF",
            "Walnut Board",
            "Rosewood Finish Board",
            "Piano Finish Board",
            "Acrylic Board",
            "Crystal Plaque",
            "Glossy Lamination Board",
            "Sunmica Board",
            "Laser MDF Board",
            "Wooden Shield Board",
            "Sublimation MDF Board"

        ]

        for name in board_names:

            db.session.add(
                Board(
                    name=name,
                    length=random.choice(
                        [8,10,12,14]
                    ),
                    breadth=random.choice(
                        [6,8,10,12]
                    ),
                    quantity=random.randint(
                        20,150
                    ),
                    price=random.randint(
                        25,120
                    )
                )
            )

        db.session.commit()

        print("Boards seeded")

        for i in range(1,21):

            db.session.add(
                Accessory(
                    name=f"AR-{i}",
                    quantity=random.randint(
                        100,500
                    ),
                    price=random.randint(
                        5,50
                    )
                )
            )

        db.session.commit()

        print("Accessories seeded")

        supplier_names = [

            "Agarwal Enterprises",
            "Gupta Traders",
            "Sharma Industries",
            "Patel Suppliers",
            "Verma Enterprises",
            "Singh Trading Co",
            "Jain Materials",
            "Reddy Suppliers",
            "Mehta Industries",
            "Yadav Enterprises"

        ]

        suppliers = []

        for name in supplier_names:

            supplier = Supplier(
                supplier_name=name
            )

            db.session.add(
                supplier
            )

            suppliers.append(
                supplier
            )

        db.session.commit()

        print("Suppliers seeded")

        foils = Foil.query.all()
        paints = Paint.query.all()
        boards = Board.query.all()
        accessories = Accessory.query.all()

        for foil in foils:

            db.session.add(
                SupplierMaterial(
                    supplier_id=random.choice(
                        suppliers
                    ).id,

                    item_type="Foil",

                    item_name=foil.foil_code,

                    lead_time=random.randint(
                        1,4
                    ),

                    safety_stock=random.randint(
                        20,100
                    ),

                    ordering_cost=random.randint(
                        100,1000
                    ),

                    holding_cost=random.randint(
                        5,50
                    )
                )
            )

        for paint in paints:

            db.session.add(
                SupplierMaterial(
                    supplier_id=random.choice(
                        suppliers
                    ).id,

                    item_type="Paint",

                    item_name=paint.name,

                    lead_time=random.randint(
                        1,4
                    ),

                    safety_stock=random.randint(
                        20,100
                    ),

                    ordering_cost=random.randint(
                        100,1000
                    ),

                    holding_cost=random.randint(
                        5,50
                    )
                )
            )

        for board in boards:

            db.session.add(
                SupplierMaterial(
                    supplier_id=random.choice(
                        suppliers
                    ).id,

                    item_type="Board",

                    item_name=board.name,

                    lead_time=random.randint(
                        1,4
                    ),

                    safety_stock=random.randint(
                        20,100
                    ),

                    ordering_cost=random.randint(
                        100,1000
                    ),

                    holding_cost=random.randint(
                        5,50
                    )
                )
            )

        for accessory in accessories:

            db.session.add(
                SupplierMaterial(
                    supplier_id=random.choice(
                        suppliers
                    ).id,

                    item_type="Accessory",

                    item_name=accessory.name,

                    lead_time=random.randint(
                        1,4
                    ),

                    safety_stock=random.randint(
                        20,100
                    ),

                    ordering_cost=random.randint(
                        100,1000
                    ),

                    holding_cost=random.randint(
                        5,50
                    )
                )
            )

        db.session.commit()

        print("Supplier Materials seeded")

        sizes = {

            "L": "Large",
            "M": "Medium",
            "S": "Small"

        }

        mementos = []

        for i in range(1501,1519):

            for code_suffix, dimension in sizes.items():

                memento = Memento(

                    code=f"RV-{i}-{code_suffix}",

                    dimension=dimension,

                    price=random.randint(
                        500,5000
                    ),

                    quantity=random.randint(
                        10,100
                    )
                )

                db.session.add(
                    memento
                )

                mementos.append(
                    memento
                )

        db.session.commit()

        print("Mementos seeded")

        foils = Foil.query.all()
        paints = Paint.query.all()
        boards = Board.query.all()
        accessories = Accessory.query.all()

        for memento in mementos:

            db.session.add(
                MementoMaterial(
                    memento_id=memento.id,
                    material_type="Foil",
                    material_id=random.choice(
                        foils
                    ).id,
                    quantity_used=random.randint(
                        1,3
                    )
                )
            )

            db.session.add(
                MementoMaterial(
                    memento_id=memento.id,
                    material_type="Paint",
                    material_id=random.choice(
                        paints
                    ).id,
                    quantity_used=random.randint(
                        1,2
                    )
                )
            )

            db.session.add(
                MementoMaterial(
                    memento_id=memento.id,
                    material_type="Board",
                    material_id=random.choice(
                        boards
                    ).id,
                    quantity_used=1
                )
            )

            db.session.add(
                MementoMaterial(
                    memento_id=memento.id,
                    material_type="Accessory",
                    material_id=random.choice(
                        accessories
                    ).id,
                    quantity_used=random.randint(
                        1,4
                    )
                )
            )

        db.session.commit()

        print("Memento Materials seeded")
        print("SEEDING COMPLETED")

