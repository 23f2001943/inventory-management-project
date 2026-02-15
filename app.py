from flask import Flask
from controller.config import Config
from controller.models import db, User, Role
from controller.auth import auth_bp
from controller.admin import admin_bp
from controller.employee import employee_bp
from controller.main import main_bp





app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(main_bp)


app.secret_key = app.config["SECRET_KEY"]

# =========================
# Create Default Admin
# =========================
def create_default_admin():
    with app.app_context():

        db.create_all()

        # Create roles if not exist
        admin_role = Role.query.filter_by(name="Admin").first()
        employee_role = Role.query.filter_by(name="Employee").first()

        if not admin_role:
            admin_role = Role(name="Admin")
            db.session.add(admin_role)

        if not employee_role:
            employee_role = Role(name="Employee")
            db.session.add(employee_role)

        db.session.commit()

        # Create default admin user
        admin_user = User.query.filter_by(email="admin@inventory.com").first()

        if not admin_user:
            admin_user = User(
                full_name="System Administrator",
                email="admin@inventory.com",
                password="admin123"  # Plain text (as per your preference)
            )

            admin_user.roles.append(admin_role)

            db.session.add(admin_user)
            db.session.commit()

        print("Default admin ensured.")


create_default_admin()


if __name__ == "__main__":
    app.run(debug=True)
