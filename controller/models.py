from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# =========================
# User Table
# =========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship(
        "Role",
        secondary="user_roles",
        backref=db.backref("users", lazy="dynamic")
    )

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)


# =========================
# Role Table
# =========================
class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


# =========================
# Association Table
# =========================
class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

class Foil(db.Model):
    __tablename__ = "foils"

    id = db.Column(db.Integer, primary_key=True)
    foil_code = db.Column(db.String(50),  nullable=False)
    foil_type = db.Column(db.String(20), nullable=False)
    length_in = db.Column(db.Float, nullable=False)
    breadth_in = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    length = db.Column(db.Float)
    breadth = db.Column(db.Float)
    price = db.Column(db.Float)

class Accessory(db.Model):
    __tablename__ = "accessories"

    id = db.Column(db.Integer, primary_key=True)

    
    name = db.Column(db.String(100), nullable=False, unique= True)

    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)

class Memento(db.Model):
    __tablename__ = "mementos"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    dimension = db.Column(db.String(100), nullable=False)

    price = db.Column(db.Float, nullable=False)

    quantity = db.Column(db.Integer, default=0)

    materials = db.relationship(
    "MementoMaterial",
    backref="memento",
    cascade="all, delete-orphan"
)

class MementoMaterial(db.Model):
    __tablename__ = "memento_materials"

    id = db.Column(db.Integer, primary_key=True)

    # WHICH MEMENTO
    memento_id = db.Column(
        db.Integer,
        db.ForeignKey("mementos.id"),
        nullable=False
    )

    # MATERIAL TYPE
    # Foil / Paint / Accessory / Board
    material_type = db.Column(
        db.String(50),
        nullable=False
    )

    # ACTUAL MATERIAL ID
    material_id = db.Column(
        db.Integer,
        nullable=False
    )

    # HOW MUCH USED
    quantity_used = db.Column(
        db.Float,
        nullable=False
    )

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    # 🔹 TYPE (Foil / Board / Accessory)
    item_type = db.Column(db.String(50), nullable=False)

    # 🔹 ACTUAL ITEM REFERENCE
    item_id = db.Column(db.Integer, nullable=False)

    # 🔹 DISPLAY DATA (snapshot)
    code = db.Column(db.String(50))
    
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

class Paint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)


# =========================
# SUPPLIER MASTER
# =========================
class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)

    supplier_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    materials = db.relationship(
        "SupplierMaterial",
        backref="supplier",
        cascade="all, delete-orphan"
    )


# =========================
# SUPPLIER MATERIALS
# =========================
class SupplierMaterial(db.Model):
    __tablename__ = "supplier_materials"

    id = db.Column(db.Integer, primary_key=True)

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id"),
        nullable=False
    )

    item_type = db.Column(
        db.String(50),
        nullable=False
    )

    item_name = db.Column(
        db.String(100),
        nullable=False
    )

    lead_time = db.Column(
        db.Integer,
        nullable=False
    )

    safety_stock = db.Column(
    db.Integer,
    default=0
    )